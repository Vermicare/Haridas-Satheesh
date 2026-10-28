"""Regression evidence: fictional revocation does NOT guard legacy outbox dispatch.

These tests intentionally assert an unsafe legacy outcome as a negative control.
They do not authorize a real connector or claim that revocation is enforced
across the delivery boundary. Only disposable SQLite databases are used.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from authorization_guard_v02 import ContractError
from fictional_outbox_v07 import FictionalIdempotentSink, FictionalOutbox
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture


class RevocationOutboxGapTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / "receipts.sqlite3"
        self.sinkdb = Path(temp.name) / "fake-sink.sqlite3"
        self.store = FictionalRevocableStore(self.db)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.outbox = FictionalOutbox(self.db)
        self.sink = FictionalIdempotentSink(self.sinkdb)
        self.scenario = fixture()
        self.scope = copy.deepcopy(self.scenario["authorization"]["scope"])
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.identity = issuer.issue_identity(
            "fictional-user", "2026-10-01T09:00:00Z", "2026-10-01T12:00:00Z"
        )
        self.approval = issuer.issue_approval(self.scenario)
        self.args = dict(identity_token=self.identity, approval_token=self.approval, now=NOW)
        self.receipt = self.boundary.execute(self.scenario, self.scope, **self.args)
        self.assertEqual(self.receipt["external_actions"], 0)

    def revoke_and_check_signed_gate(self):
        self.boundary.revoke(
            self.approval, now=NOW, reason="fictional withdrawal before fake delivery"
        )
        with self.assertRaisesRegex(ContractError, "revoked"):
            self.boundary.execute(self.scenario, self.scope, **self.args)
        self.assertEqual(self.store.revocation_count(), 1)

    def test_staged_before_revocation_still_delivers_to_legacy_fake_sink(self):
        nonce = self.receipt["nonce"]
        self.outbox.stage(nonce)
        self.revoke_and_check_signed_gate()
        # INTENTIONAL NEGATIVE RESULT: v0.7 dispatch ignores v1.1 revocations.
        ack = FictionalOutbox(self.db).dispatch(nonce, self.sink)
        self.assertEqual(ack["external_actions"], 0)
        self.assertEqual(ack["simulated_actions"], 1)
        self.assertEqual(self.sink.count(), 1)
        self.assertEqual(self.outbox.status(nonce), "acked")

    def test_staging_after_revocation_still_delivers_to_legacy_fake_sink(self):
        nonce = self.receipt["nonce"]
        self.revoke_and_check_signed_gate()
        self.outbox.stage(nonce)
        ack = FictionalOutbox(self.db).dispatch(
            nonce, FictionalIdempotentSink(self.sinkdb)
        )
        self.assertEqual(ack["external_actions"], 0)
        self.assertEqual(ack["simulated_actions"], 1)
        self.assertEqual(self.sink.count(), 1)
        self.assertEqual(self.store.receipt_count(), 1)


if __name__ == "__main__":
    unittest.main()
