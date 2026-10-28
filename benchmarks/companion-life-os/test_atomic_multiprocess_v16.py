"""Cross-process SQLite race tests for a FICTIONAL, same-database delivery gate.

No real connector, human authorization, trusted clock, or production security
claim. A marker synchronizes process readiness, NOT the actual transaction order.
The test accepts either valid serialized order and rejects split-brain effects.
"""
import copy
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path

from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture

CHILD = r"""
import json
import sys
from pathlib import Path
from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW

db, nonce, approval, operation, marker, output = sys.argv[1:]
Path(marker).write_text("ready", encoding="ascii")
try:
    boundary = FictionalRevocableBoundary(
        FictionalRevocableStore(db), IDENTITY_KEY, APPROVAL_KEY)
    if operation == "revoke":
        value = boundary.revoke(approval, now=NOW, reason="fictional parallel withdrawal")
    elif operation == "dispatch":
        value = AtomicFictionalDelivery(boundary).dispatch(nonce)
    else:
        raise ValueError("unsupported operation")
    result = {"status": "ok", "operation": operation, "value": value}
except FictionalDeliveryError as exc:
    result = {"status": "denied", "operation": operation, "error": str(exc)}
except BaseException as exc:
    result = {"status": "unexpected", "operation": operation,
              "error": type(exc).__name__ + ": " + str(exc)}
Path(output).write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
"""


class FictionalMultiprocessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def _stage(self, name):
        db = self.root / (name + ".sqlite3")
        boundary = FictionalRevocableBoundary(
            FictionalRevocableStore(db), IDENTITY_KEY, APPROVAL_KEY)
        adapter = AtomicFictionalDelivery(boundary)
        scenario = fixture()
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        identity = issuer.issue_identity(
            "fictional-user", "2026-10-01T09:00:00Z", "2026-10-01T12:00:00Z")
        approval = issuer.issue_approval(scenario)
        nonce = adapter.stage(
            scenario, copy.deepcopy(scenario["authorization"]["scope"]),
            identity_token=identity, approval_token=approval, now=NOW)["nonce"]
        return db, adapter, nonce, approval

    def _parallel(self, db, nonce, approval, operations, label):
        # Holding a SQLite RESERVED write lock prevents either child's DB write
        # from winning before both children have reached the ready marker.
        lock = sqlite3.connect(db, timeout=15.0, isolation_level=None)
        children = []
        paths = []
        try:
            lock.execute("BEGIN IMMEDIATE")
            for index, operation in enumerate(operations):
                marker = self.root / f"{label}-{index}.ready"
                output = self.root / f"{label}-{index}.json"
                proc = subprocess.Popen(
                    [sys.executable, "-B", "-c", CHILD, str(db), nonce,
                     approval, operation, str(marker), str(output)],
                    cwd=str(Path(__file__).resolve().parent),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                children.append(proc)
                paths.append((marker, output))
            deadline = time.monotonic() + 20
            while not all(marker.exists() for marker, _ in paths):
                self.assertLess(time.monotonic(), deadline,
                                "fictional child did not signal readiness")
                time.sleep(0.02)
        finally:
            if lock.in_transaction:
                lock.commit()
            lock.close()
        try:
            results = []
            for proc, (_, output) in zip(children, paths):
                stdout, stderr = proc.communicate(timeout=35)
                self.assertEqual(proc.returncode, 0,
                                 f"child exited {proc.returncode}: {stderr[-1000:]}")
                self.assertTrue(output.is_file(), f"missing result: {stderr[-1000:]}")
                result = json.loads(output.read_text(encoding="utf-8"))
                self.assertNotEqual(result["status"], "unexpected", result)
                results.append(result)
            return results
        finally:
            for proc in children:
                if proc.poll() is None:
                    proc.kill()
                    proc.communicate()

    def test_six_cross_process_revoke_dispatch_races_are_serializable(self):
        for round_number in range(6):
            with self.subTest(round=round_number):
                db, adapter, nonce, approval = self._stage(f"race-{round_number}")
                operations = (["revoke", "dispatch"] if round_number % 2 == 0
                              else ["dispatch", "revoke"])
                results = self._parallel(
                    db, nonce, approval, operations, f"race-{round_number}")
                revoked = next(x for x in results if x["operation"] == "revoke")
                delivery = next(x for x in results if x["operation"] == "dispatch")
                self.assertEqual(revoked["status"], "ok")
                self.assertEqual(revoked["value"]["external_actions"], 0)
                counts = adapter.counts(nonce)
                self.assertEqual(counts["external_actions"], 0)
                with closing(sqlite3.connect(db)) as connection:
                    self.assertEqual(
                        connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                    self.assertEqual(
                        connection.execute(
                            "SELECT COUNT(*) FROM fictional_revocations").fetchone()[0], 1)
                if delivery["status"] == "ok":
                    self.assertEqual(counts["status"], "acked")
                    self.assertEqual(counts["fictional_sink_rows"], 1)
                    self.assertTrue(adapter.dispatch(nonce)["outbox_replay"])
                else:
                    self.assertEqual(delivery["status"], "denied")
                    self.assertIn("revoked", delivery["error"])
                    self.assertEqual(counts["status"], "cancelled")
                    self.assertEqual(counts["fictional_sink_rows"], 0)
                    with self.assertRaises(FictionalDeliveryError):
                        adapter.dispatch(nonce)

    def test_six_cross_process_dispatches_produce_one_fictional_sink_row(self):
        db, adapter, nonce, approval = self._stage("parallel-dispatch")
        results = self._parallel(
            db, nonce, approval, ["dispatch"] * 6, "parallel-dispatch")
        self.assertEqual([r["status"] for r in results], ["ok"] * 6)
        self.assertEqual(
            sum(not r["value"]["outbox_replay"] for r in results), 1)
        self.assertEqual(
            sum(r["value"]["outbox_replay"] for r in results), 5)
        self.assertEqual(
            adapter.counts(nonce),
            {"status": "acked", "fictional_sink_rows": 1, "external_actions": 0})


if __name__ == "__main__":
    unittest.main()
