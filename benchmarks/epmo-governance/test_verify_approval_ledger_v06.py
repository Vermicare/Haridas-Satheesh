"""Adversarial structural audit of the exact v0.5 fictional SQLite schema."""
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from approval_consumption_v05 import (initialize, seed_fictional_approval,
                                      consume_fictional_approval)
from verify_approval_ledger_v06 import LedgerIntegrityError, verify


class LedgerIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fictional.sqlite3"
        initialize(self.path)
        self.approval = dict(approval_id="fictional-ap", actor_id="fictional-actor",
                             action="fictional-update", scope="fictional-scope",
                             nonce="fictional-nonce", expires_at=200)
        seed_fictional_approval(self.path, **self.approval)
        self.request = {k: v for k, v in self.approval.items() if k != "expires_at"}
        self.request.update(request_id="fictional-req", receipt_id="fictional-receipt", now=100)

    def consume(self):
        self.assertEqual(consume_fictional_approval(self.path, **self.request)["outcome"], "consumed")

    def tamper(self, statement, params=()):
        with closing(sqlite3.connect(self.path)) as db:
            with db:
                db.execute(statement, params)

    def rejects(self, statement, params=()):
        self.consume()
        self.tamper(statement, params)
        with self.assertRaises(LedgerIntegrityError):
            verify(self.path)

    def test_valid_unconsumed(self):
        r = verify(self.path)
        self.assertEqual((r["approvals"], r["receipts"]), (1, 0))
        self.assertFalse(r["identity_authenticated"])

    def test_valid_consumed_deterministic_and_read_only(self):
        self.consume()
        first = verify(self.path)
        self.assertEqual(first, verify(self.path))
        self.assertEqual(first["receipts"], 1)
        self.assertFalse(first["tamper_proof"])
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM consumption_receipts").fetchone()[0], 1)

    def test_wrong_origin_rejected(self):
        with self.assertRaises(LedgerIntegrityError):
            verify(self.path, origin="REAL")

    def test_missing_database_does_not_create(self):
        missing = self.path.with_name("missing.sqlite3")
        with self.assertRaises(LedgerIntegrityError):
            verify(missing)
        self.assertFalse(missing.exists())

    def test_wrong_schema_rejected(self):
        self.tamper("DROP TABLE consumption_receipts")
        with self.assertRaises(LedgerIntegrityError):
            verify(self.path)

    def test_missing_receipt_detected(self):
        self.rejects("DELETE FROM consumption_receipts")

    def test_orphan_receipt_detected(self):
        self.rejects("DELETE FROM approvals")

    def test_wrong_actor_detected(self):
        self.rejects("UPDATE consumption_receipts SET actor_id='forged'")

    def test_wrong_action_detected(self):
        self.rejects("UPDATE consumption_receipts SET action='forged'")

    def test_wrong_scope_detected(self):
        self.rejects("UPDATE consumption_receipts SET scope='forged'")

    def test_wrong_nonce_detected(self):
        self.rejects("UPDATE consumption_receipts SET nonce='forged'")

    def test_wrong_request_detected(self):
        self.rejects("UPDATE consumption_receipts SET request_id='forged'")

    def test_wrong_receipt_detected(self):
        self.rejects("UPDATE approvals SET consumed_receipt='forged'")

    def test_partial_approval_detected(self):
        self.rejects("UPDATE approvals SET consumed_request=NULL")

    def test_unconsumed_approval_with_receipt_detected(self):
        self.rejects("UPDATE approvals SET consumed_request=NULL, consumed_receipt=NULL")

    def test_expired_consumption_detected(self):
        self.rejects("UPDATE consumption_receipts SET consumed_at=200")

    def test_negative_consumption_time_detected(self):
        self.rejects("UPDATE consumption_receipts SET consumed_at=-1")

    def test_invalid_expiry_detected(self):
        self.tamper("UPDATE approvals SET expires_at=-1")
        with self.assertRaises(LedgerIntegrityError):
            verify(self.path)

    def test_blank_actor_detected(self):
        self.rejects("UPDATE approvals SET actor_id=' '")

    def test_type_confusion_detected(self):
        self.rejects("UPDATE consumption_receipts SET consumed_at='not-a-time'")

    def test_coordinated_forgery_not_detectable(self):
        self.consume()
        self.tamper("UPDATE approvals SET actor_id='fictional-forged'")
        self.tamper("UPDATE consumption_receipts SET actor_id='fictional-forged'")
        # An internally consistent forgery is outside this structural checker's scope.
        self.assertTrue(verify(self.path)["structurally_consistent"])

    def test_empty_database_valid_but_not_proof(self):
        self.tamper("DELETE FROM approvals")
        r = verify(self.path)
        self.assertEqual(r["approvals"], 0)
        self.assertFalse(r["identity_authenticated"])


if __name__ == "__main__":
    unittest.main()
