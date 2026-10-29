"""v1.7 controlled interleaving: receipt insertion precedes outbox staging.

This intentionally preserves a negative control. Disposable fictional SQLite only.
It does NOT test a real user, service, or connector.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from authorization_guard_v02 import ContractError
from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from fictional_outbox_v07 import FictionalOutbox, FictionalIdempotentSink
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import IDENTITY_KEY, APPROVAL_KEY, NOW, fixture


class StageReceiptRevocationGapTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / "fictional-receipts.sqlite3"
        self.sinkdb = Path(temp.name) / "fictional-legacy-sink.sqlite3"
        self.store = FictionalRevocableStore(self.db)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.delivery = AtomicFictionalDelivery(self.boundary)
        self.scenario = fixture()
        self.scope = copy.deepcopy(self.scenario["authorization"]["scope"])
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.identity = issuer.issue_identity(
            "fictional-user", "2026-10-01T09:00:00Z", "2026-10-01T12:00:00Z"
        )
        self.approval = issuer.issue_approval(self.scenario)
        self.args = dict(identity_token=self.identity, approval_token=self.approval, now=NOW)

    def _stage_with_forced_revocation_between_receipt_and_outbox(self):
        original = self.boundary.execute

        def interleave(*args, **kwargs):
            receipt = original(*args, **kwargs)
            # Deterministically inject revocation AFTER the receipt COMMIT,
            # BEFORE v1.4 opens the outbox staging transaction.
            self.boundary.revoke(self.approval, now=NOW, reason="fictional interleaving")
            return receipt

        with patch.object(self.boundary, "execute", side_effect=interleave):
            with self.assertRaisesRegex(FictionalDeliveryError, "revoked before staging"):
                self.delivery.stage(self.scenario, self.scope, **self.args)
        return self.scenario["authorization"]["nonce"]

    def test_clean_stage_is_pending_without_fake_sink_effect(self):
        nonce = self.delivery.stage(self.scenario, self.scope, **self.args)["nonce"]
        self.assertEqual(self.store.receipt_count(), 1)
        self.assertEqual(self.delivery.counts(nonce), {
            "status": "pending", "fictional_sink_rows": 0, "external_actions": 0
        })

    def test_revocation_before_receipt_leaves_no_receipt_or_outbox(self):
        self.boundary.revoke(self.approval, now=NOW, reason="fictional pre-stage stop")
        with self.assertRaisesRegex(ContractError, "revoked"):
            self.delivery.stage(self.scenario, self.scope, **self.args)
        self.assertEqual(self.store.receipt_count(), 0)
        self.assertEqual(self.delivery.counts(self.scenario["authorization"]["nonce"]), {
            "status": None, "fictional_sink_rows": 0, "external_actions": 0
        })

    def test_revocation_between_receipt_and_stage_leaves_stranded_receipt(self):
        nonce = self._stage_with_forced_revocation_between_receipt_and_outbox()
        # NEGATIVE RESULT: stage was denied, but the earlier receipt committed.
        self.assertEqual(self.store.receipt_count(), 1)
        self.assertEqual(self.delivery.counts(nonce), {
            "status": None, "fictional_sink_rows": 0, "external_actions": 0
        })
        with self.assertRaisesRegex(ContractError, "revoked"):
            self.boundary.execute(self.scenario, self.scope, **self.args)

    def test_legacy_outbox_can_dispatch_stranded_receipt_after_revocation(self):
        nonce = self._stage_with_forced_revocation_between_receipt_and_outbox()
        # INTENTIONAL UNSAFE NEGATIVE CONTROL, never an endorsed API.
        legacy = FictionalOutbox(self.db)
        legacy.stage(nonce)
        fake_sink = FictionalIdempotentSink(self.sinkdb)
        result = legacy.dispatch(nonce, fake_sink)
        self.assertEqual(result["simulated_actions"], 1)
        self.assertEqual(result["external_actions"], 0)
        self.assertEqual(fake_sink.count(), 1)
        self.assertEqual(self.delivery.counts(nonce)["fictional_sink_rows"], 0)


if __name__ == "__main__":
    unittest.main()
