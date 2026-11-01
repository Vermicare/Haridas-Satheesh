"""v2.0 executable inventory of four legacy *fictional* effect routes.

Positive results are deliberate negative-control evidence: the legacy paths
can write disposable SQLite fixtures without calling the newer signed/revocable
boundary. They are NOT real-world vulnerabilities or production reachability
proofs. No external connectors, accounts, or private data are involved.
"""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from authorization_store_v03 import FictionalDurableStore
from fictional_outbox_v07 import (
    FictionalIdempotentSink, FictionalOutbox, OutboxContractError,
)
from test_authorization_store_v03 import scenario


class LegacyRuntimeReachabilityV20(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.receipts = Path(self.tmp.name) / "fictional-receipts.sqlite3"
        self.sink_db = Path(self.tmp.name) / "fictional-sink.sqlite3"
        self.nonce = "v20-fictional-nonce"
        self.payload = {
            "nonce": self.nonce, "decision": "fictional-D1",
            "action": "fictional-A1", "synthetic": True,
        }

    def seed_unsigned_receipt(self, *, synthetic=True):
        """Directly seed a disposable fixture, without an approval token."""
        receipt = dict(self.payload, synthetic=synthetic, external_actions=0)
        with closing(sqlite3.connect(self.receipts)) as db, db:
            db.execute("CREATE TABLE receipts (nonce TEXT PRIMARY KEY, "
                       "fingerprint TEXT, receipt_json TEXT)")
            db.execute("INSERT INTO receipts VALUES(?,?,?)",
                       (self.nonce, "fixture-only", json.dumps(receipt)))

    def test_01_legacy_durable_execute_accepts_fictional_principal_without_signed_token(self):
        fixture = scenario()
        store = FictionalDurableStore(self.receipts)
        receipt = store.execute(
            fixture, fixture["authorization"]["scope"],
            principal="fictional-user", now="2026-10-01T10:30:00Z",
            trusted_principals={"fictional-user"},
        )
        self.assertEqual(store.receipt_count(), 1)
        self.assertTrue(receipt["synthetic"])
        self.assertEqual(receipt["external_actions"], 0)
        # The legacy API accepts no signed identity or approval token.

    def test_02_legacy_outbox_stages_unsigned_fixture(self):
        self.seed_unsigned_receipt()
        outbox = FictionalOutbox(self.receipts)
        result = outbox.stage(self.nonce)
        self.assertEqual(outbox.status(self.nonce), "pending")
        self.assertFalse(result["stage_replay"])
        # No FictionalRevocableBoundary object or approval token was supplied.

    def test_03_legacy_outbox_dispatches_unsigned_fixture_to_fake_sink(self):
        self.seed_unsigned_receipt()
        outbox = FictionalOutbox(self.receipts)
        sink = FictionalIdempotentSink(self.sink_db)
        outbox.stage(self.nonce)
        result = outbox.dispatch(self.nonce, sink)
        self.assertEqual(outbox.status(self.nonce), "acked")
        self.assertEqual(sink.count(), 1)
        self.assertEqual(result["external_actions"], 0)
        self.assertEqual(result["simulated_actions"], 1)

    def test_04_legacy_fake_sink_direct_apply_needs_no_receipt(self):
        sink = FictionalIdempotentSink(self.sink_db)
        result = sink.apply(self.payload)
        self.assertEqual(sink.count(), 1)
        self.assertFalse(self.receipts.exists())
        self.assertEqual(result["external_actions"], 0)
        self.assertEqual(result["simulated_actions"], 1)

    def test_05_fake_sink_still_rejects_nonfictional_payload(self):
        sink = FictionalIdempotentSink(self.sink_db)
        with self.assertRaises(OutboxContractError):
            sink.apply(dict(self.payload, synthetic=False))
        self.assertEqual(sink.count(), 0)

    def test_06_legacy_outbox_still_rejects_nonfictional_receipt(self):
        self.seed_unsigned_receipt(synthetic=False)
        outbox = FictionalOutbox(self.receipts)
        with self.assertRaises(OutboxContractError):
            outbox.stage(self.nonce)
        self.assertIsNone(outbox.status(self.nonce))


if __name__ == "__main__":
    unittest.main()
