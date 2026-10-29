"""v1.8 expiry-at-dispatch negative controls; disposable fictional SQLite only.

These tests intentionally PASS when the older v1.4 adapter demonstrates a
policy gap. They do not validate a real identity, clock, connector, or user.
"""
import copy
import inspect
import tempfile
import unittest
from pathlib import Path

from authorization_guard_v02 import ContractError
from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import IDENTITY_KEY, APPROVAL_KEY, NOW, fixture


EXPIRED = "2026-10-01T11:00:00Z"


class DispatchExpiryGapTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / "fictional.sqlite3"
        self.store = FictionalRevocableStore(self.db)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.adapter = AtomicFictionalDelivery(self.boundary)
        self.scenario = fixture()
        self.scope = copy.deepcopy(self.scenario["authorization"]["scope"])
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.identity = issuer.issue_identity(
            "fictional-user", "2026-10-01T09:00:00Z", "2026-10-01T12:00:00Z"
        )
        self.approval = issuer.issue_approval(self.scenario)
        self.kw = dict(identity_token=self.identity, approval_token=self.approval, now=NOW)

    def test_new_stage_at_expiry_denied_and_no_receipt(self):
        with self.assertRaisesRegex(ContractError, "expired"):
            self.adapter.stage(self.scenario, self.scope,
                               **{**self.kw, "now": EXPIRED})
        self.assertEqual(self.store.receipt_count(), 0)
        self.assertEqual(self.adapter.counts(self.scenario["authorization"]["nonce"]),
                         {"status": None, "fictional_sink_rows": 0, "external_actions": 0})

    def test_expired_approval_still_dispatches_previously_staged_work_negative_control(self):
        nonce = self.adapter.stage(self.scenario, self.scope, **self.kw)["nonce"]
        with self.assertRaisesRegex(ContractError, "expired"):
            self.boundary.execute(self.scenario, self.scope,
                                  **{**self.kw, "now": EXPIRED})
        # NEGATIVE CONTROL: v1.4 dispatch has no time argument or expiry check.
        # The hypothetical time of dispatch is AFTER the approval's expiry;
        # the adapter itself never observes that time.
        result = self.adapter.dispatch(nonce)
        self.assertEqual(result["simulated_actions"], 1)
        self.assertEqual(result["external_actions"], 0)
        self.assertEqual(self.adapter.counts(nonce),
                         {"status": "acked", "fictional_sink_rows": 1, "external_actions": 0})

    def test_dispatch_contract_has_no_clock_or_approval_token(self):
        params = inspect.signature(AtomicFictionalDelivery.dispatch).parameters
        self.assertNotIn("now", params)
        self.assertNotIn("approval_token", params)
        self.assertNotIn("trusted_clock", params)

    def test_revocation_still_blocks_pending_fake_dispatch(self):
        nonce = self.adapter.stage(self.scenario, self.scope, **self.kw)["nonce"]
        self.boundary.revoke(self.approval, now=NOW, reason="fictional stop")
        with self.assertRaisesRegex(FictionalDeliveryError, "revoked"):
            self.adapter.dispatch(nonce)
        self.assertEqual(self.adapter.counts(nonce),
                         {"status": "cancelled", "fictional_sink_rows": 0, "external_actions": 0})


if __name__ == "__main__":
    unittest.main()
