"""Fictional, isolated SQLite concurrency and crash/recovery negative controls."""
import concurrent.futures
import tempfile
import unittest
from pathlib import Path

from durable_receipt_sandbox import (InjectedFailure, ReceiptConflict, initialize,
    record_simulated_receipt as reserve, record_simulated_correction as correct,
    snapshot, demonstration)


class DurableReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fictional.sqlite3"
        initialize(self.path)
        self.data = dict(request_id="fictional-rq1", receipt_id="fictional-rc1",
                         approval_id="fictional-ap1", action="fictional-action", scope="fictional-scope")

    def test_16_concurrent_identical_requests_create_exactly_one_row(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(reserve, self.path, **self.data) for _ in range(16)]
            outcomes = [f.result()["outcome"] for f in futures]
        self.assertEqual(outcomes.count("created"), 1)
        self.assertEqual(outcomes.count("idempotent"), 15)
        self.assertEqual(len(snapshot(self.path)), 1)

    def test_distinct_requests_cannot_reuse_receipt_even_after_correction(self):
        reserve(self.path, **self.data)
        correct(self.path, request_id=self.data["request_id"],
                receipt_id=self.data["receipt_id"], reason="fictional correction")
        with self.assertRaises(ReceiptConflict):
            reserve(self.path, **{**self.data, "request_id": "fictional-rq2"})
        self.assertEqual(snapshot(self.path)[0]["status"], "corrected")

    def test_same_request_cannot_change_scope(self):
        reserve(self.path, **self.data)
        with self.assertRaises(ReceiptConflict):
            reserve(self.path, **{**self.data, "scope": "different-scope"})

    def test_same_request_cannot_change_receipt(self):
        reserve(self.path, **self.data)
        with self.assertRaises(ReceiptConflict):
            reserve(self.path, **{**self.data, "receipt_id": "other-receipt"})

    def test_restart_idempotency(self):
        reserve(self.path, **self.data)
        self.assertEqual(reserve(self.path, **self.data)["outcome"], "idempotent")
        self.assertEqual(len(snapshot(self.path)), 1)

    def test_crash_before_commit_rolls_back(self):
        with self.assertRaises(InjectedFailure):
            reserve(self.path, **self.data, failpoint="before_commit")
        self.assertEqual(snapshot(self.path), [])
        self.assertEqual(reserve(self.path, **self.data)["outcome"], "created")

    def test_crash_after_commit_is_recoverable(self):
        with self.assertRaises(InjectedFailure):
            reserve(self.path, **self.data, failpoint="after_commit")
        self.assertEqual(reserve(self.path, **self.data)["outcome"], "idempotent")

    def test_correction_persists_across_connections(self):
        reserve(self.path, **self.data)
        correct(self.path, request_id=self.data["request_id"],
                receipt_id=self.data["receipt_id"], reason="reason A")
        self.assertEqual(snapshot(self.path)[0]["correction_reason"], "reason A")
        self.assertEqual(reserve(self.path, **self.data)["outcome"], "idempotent")

    def test_correction_changed_reason_rejected(self):
        reserve(self.path, **self.data)
        correct(self.path, request_id=self.data["request_id"],
                receipt_id=self.data["receipt_id"], reason="reason A")
        with self.assertRaises(ReceiptConflict):
            correct(self.path, request_id=self.data["request_id"],
                    receipt_id=self.data["receipt_id"], reason="reason B")

    def test_correction_before_commit_failure_preserves_reservation(self):
        reserve(self.path, **self.data)
        with self.assertRaises(InjectedFailure):
            correct(self.path, request_id=self.data["request_id"],
                    receipt_id=self.data["receipt_id"], reason="reason A", failpoint="before_commit")
        self.assertEqual(snapshot(self.path)[0]["status"], "reserved")

    def test_correction_after_commit_failure_recovers(self):
        reserve(self.path, **self.data)
        with self.assertRaises(InjectedFailure):
            correct(self.path, request_id=self.data["request_id"],
                    receipt_id=self.data["receipt_id"], reason="reason A", failpoint="after_commit")
        self.assertEqual(correct(self.path, request_id=self.data["request_id"],
                                 receipt_id=self.data["receipt_id"], reason="reason A")["outcome"], "idempotent")

    def test_unknown_receipt_correction_rejected(self):
        with self.assertRaises(ReceiptConflict):
            correct(self.path, request_id="unknown", receipt_id="unknown", reason="reason")

    def test_wrong_request_correction_rejected(self):
        reserve(self.path, **self.data)
        with self.assertRaises(ReceiptConflict):
            correct(self.path, request_id="wrong", receipt_id=self.data["receipt_id"], reason="reason")

    def test_origin_rejects_physical(self):
        with self.assertRaises(ValueError):
            reserve(self.path, **self.data, origin="PHYSICAL")

    def test_blank_fields_rejected(self):
        with self.assertRaises(ValueError):
            reserve(self.path, **{**self.data, "approval_id": " "})

    def test_distinct_requests_concurrent_same_receipt_one_winner(self):
        a, b = self.data, {**self.data, "request_id": "fictional-rq2"}
        def attempt(data):
            try:
                return reserve(self.path, **data)["outcome"]
            except ReceiptConflict:
                return "conflict"
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, (a, b)))
        self.assertCountEqual(outcomes, ["created", "conflict"])
        self.assertEqual(len(snapshot(self.path)), 1)

    def test_demo_is_deterministic_and_side_effect_free(self):
        self.assertEqual(demonstration(), demonstration())
        self.assertEqual(demonstration()["external_actions"], 0)
        self.assertFalse(demonstration()["identity_authenticated"])


if __name__ == "__main__":
    unittest.main()
