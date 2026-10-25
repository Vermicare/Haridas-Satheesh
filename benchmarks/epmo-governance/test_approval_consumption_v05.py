"""Adversarial fictional-only one-time SQLite approval gate tests."""
import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from approval_consumption_v05 import (
    FictionalInputError, InjectedFailure, initialize, seed_fictional_approval,
    consume_fictional_approval, snapshot)


class ApprovalConsumptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fictional.sqlite3"
        initialize(self.path)
        self.approval = dict(approval_id="fictional-ap1", actor_id="fictional-actor",
                             action="fictional-update", scope="fictional-project",
                             nonce="fictional-nonce-1", expires_at=200)
        seed_fictional_approval(self.path, **self.approval)
        self.req = {k: v for k, v in self.approval.items() if k != "expires_at"}
        self.req.update(request_id="fictional-req1", receipt_id="fictional-receipt1", now=100)

    def take(self, **changes):
        return consume_fictional_approval(self.path, **{**self.req, **changes})

    def test_success_and_one_receipt(self):
        self.assertEqual(self.take()["outcome"], "consumed")
        self.assertEqual(len(snapshot(self.path)["receipts"]), 1)

    def test_identical_retry_is_idempotent_even_after_expiry(self):
        self.take()
        self.assertEqual(self.take(now=201)["outcome"], "idempotent")
        self.assertEqual(len(snapshot(self.path)["receipts"]), 1)

    def test_different_request_cannot_reuse_approval(self):
        self.take()
        self.assertEqual(self.take(request_id="fictional-req2")["reason"], "already_consumed")

    def test_different_receipt_cannot_reuse_approval(self):
        self.take()
        self.assertEqual(self.take(receipt_id="fictional-receipt2")["reason"], "already_consumed")

    def test_expiry_boundary_rejects(self):
        self.assertEqual(self.take(now=200)["reason"], "expired")
        self.assertEqual(len(snapshot(self.path)["receipts"]), 0)

    def test_wrong_scope_rejects(self):
        self.assertEqual(self.take(scope="other")["reason"], "binding_mismatch")

    def test_wrong_action_rejects(self):
        self.assertEqual(self.take(action="other")["reason"], "binding_mismatch")

    def test_wrong_actor_rejects(self):
        self.assertEqual(self.take(actor_id="other")["reason"], "binding_mismatch")

    def test_wrong_nonce_rejects(self):
        self.assertEqual(self.take(nonce="other")["reason"], "binding_mismatch")

    def test_unknown_approval_rejects(self):
        self.assertEqual(self.take(approval_id="unknown")["reason"], "unknown_approval")

    def test_duplicate_issuance_nonce_rejected(self):
        with self.assertRaises(Exception):
            seed_fictional_approval(self.path, **{**self.approval, "approval_id": "other"})

    def test_cross_approval_request_collision_rollback(self):
        self.take()
        other = {**self.approval, "approval_id": "ap2", "nonce": "nonce2"}
        seed_fictional_approval(self.path, **other)
        r = self.take(approval_id="ap2", nonce="nonce2", receipt_id="receipt2")
        self.assertEqual(r["reason"], "receipt_or_request_collision")
        self.assertIsNone(next(x for x in snapshot(self.path)["approvals"] if x["approval_id"] == "ap2")["consumed_request"])

    def test_cross_approval_receipt_collision_rollback(self):
        self.take()
        seed_fictional_approval(self.path, **{**self.approval, "approval_id": "ap2", "nonce": "nonce2"})
        r = self.take(approval_id="ap2", nonce="nonce2", request_id="req2")
        self.assertEqual(r["reason"], "receipt_or_request_collision")

    def test_16_concurrent_same_approval_one_winner(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: self.take(request_id=f"req{i}", receipt_id=f"rc{i}"), range(16)))
        self.assertEqual(sum(r["outcome"] == "consumed" for r in results), 1)
        self.assertEqual(len(snapshot(self.path)["receipts"]), 1)

    def test_16_concurrent_identical_requests_one_creation(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.take(), range(16)))
        self.assertEqual(sum(r["outcome"] == "consumed" for r in results), 1)
        self.assertEqual(sum(r["outcome"] == "idempotent" for r in results), 15)

    def test_crash_before_commit_rolls_back_both_tables(self):
        with self.assertRaises(InjectedFailure):
            self.take(failpoint="before_commit")
        self.assertEqual(len(snapshot(self.path)["receipts"]), 0)
        self.assertIsNone(snapshot(self.path)["approvals"][0]["consumed_request"])
        self.assertEqual(self.take()["outcome"], "consumed")

    def test_crash_after_commit_recovered_by_retry(self):
        with self.assertRaises(InjectedFailure):
            self.take(failpoint="after_commit")
        self.assertEqual(self.take()["outcome"], "idempotent")
        self.assertEqual(len(snapshot(self.path)["receipts"]), 1)

    def test_restart_reopen_persists_consumption(self):
        self.take()
        self.assertEqual(self.take()["outcome"], "idempotent")

    def test_nonfictional_origin_rejected(self):
        with self.assertRaises(FictionalInputError):
            self.take(origin="REAL")

    def test_boolean_clock_rejected(self):
        with self.assertRaises(FictionalInputError):
            self.take(now=True)

    def test_negative_clock_rejected(self):
        with self.assertRaises(FictionalInputError):
            self.take(now=-1)

    def test_blank_id_rejected(self):
        with self.assertRaises(FictionalInputError):
            self.take(request_id=" ")

    def test_unknown_failpoint_rejected(self):
        with self.assertRaises(FictionalInputError):
            self.take(failpoint="any")

    def test_rejected_request_does_not_consume_approval(self):
        self.take(scope="wrong")
        self.assertEqual(self.take()["outcome"], "consumed")

    def test_no_authentication_or_external_actions_claim(self):
        self.take()
        state = snapshot(self.path)
        self.assertFalse(state["identity_authenticated"])
        self.assertFalse(state["trusted_clock"])
        self.assertEqual(state["external_actions"], 0)


if __name__ == "__main__":
    unittest.main()
