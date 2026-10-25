"""End-to-end fictional v0.3 receipt -> v0.5 correction integration contract.

Unlike v0.5's unit fixtures, the original receipt is produced by the actual
v0.3 evaluator. No real identity proof, task update, or reversal occurs.
"""
import copy
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from authorization_store_v03 import FictionalDurableStore
from correction_ledger_v05 import FictionalCorrectionLedger, CorrectionContractError


def fictional_scenario():
    value = json.loads(Path(__file__).with_name("scenario.json").read_text(encoding="utf-8"))
    value["proposed_decision"]["scope"] = copy.deepcopy(value["authorization"]["scope"])
    value["authorization"].update(
        issued_at="2026-10-01T10:00:00Z",
        expires_at="2026-10-01T11:00:00Z",
        nonce="fictional-nonce-1",
    )
    return value


def fictional_correction(*, correction_id="C1", parent="fictional-nonce-1",
                         grant_nonce="correction-nonce-1"):
    return {
        "id": correction_id, "parent_event_id": parent,
        "approved_by": "fictional-user", "decision": "D1", "action": "ACT1",
        "grant": {
            "id": "AUTH-C-" + correction_id, "nonce": grant_nonce,
            "approved_by": "fictional-user",
            "issued_at": "2026-10-01T10:00:00Z",
            "expires_at": "2026-10-01T11:00:00Z",
            "scope": {
                "operation": "restore_due_date",
                "original_nonce": "fictional-nonce-1",
                "parent_event_id": parent, "new_due": "2026-10-02",
            },
        },
    }


class ActualReceiptIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fictional.sqlite3"
        self.original = FictionalDurableStore(self.path)
        self.corrections = FictionalCorrectionLedger(self.path)
        self.scenario = fictional_scenario()
        self.original_kwargs = {
            "principal": "fictional-user", "now": "2026-10-01T10:30:00Z",
            "trusted_principals": {"fictional-user"},
        }
        self.correction_kwargs = dict(self.original_kwargs)

    def authorize(self, store=None):
        return (store or self.original).execute(
            self.scenario, self.scenario["authorization"]["scope"],
            **self.original_kwargs,
        )

    def correct(self, value=None, ledger=None, **kwargs):
        options = {**self.correction_kwargs, **kwargs}
        return (ledger or self.corrections).record(
            "fictional-nonce-1", value if value is not None else fictional_correction(),
            **options,
        )

    def stored_original(self):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute(
                "SELECT fingerprint, receipt_json FROM receipts WHERE nonce=?",
                ("fictional-nonce-1",),
            ).fetchone()

    def test_actual_v03_receipt_is_preserved_after_v05_correction(self):
        receipt = self.authorize()
        before = self.stored_original()
        self.assertEqual(json.loads(before[1]), {
            key: value for key, value in receipt.items() if key != "idempotent_replay"
        })
        correction = self.correct()
        self.assertEqual(self.stored_original(), before)
        self.assertEqual(correction["original_nonce"], receipt["nonce"])
        self.assertEqual(correction["action"], receipt["action"])
        self.assertEqual(correction["decision"], receipt["decision"])
        self.assertEqual(correction["external_actions"], 0)
        self.assertEqual(self.original.receipt_count(), 1)
        self.assertEqual(self.corrections.correction_count(), 1)

    def test_restarted_both_modules_are_idempotent(self):
        first = self.authorize()
        correction = self.correct()
        second = self.authorize(FictionalDurableStore(self.path))
        replay = self.correct(ledger=FictionalCorrectionLedger(self.path))
        self.assertFalse(first["idempotent_replay"])
        self.assertFalse(correction["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertTrue(replay["idempotent_replay"])
        self.assertEqual(self.original.receipt_count(), 1)
        self.assertEqual(self.corrections.correction_count(), 1)

    def test_correction_requires_receipt_from_original_store(self):
        with self.assertRaisesRegex(CorrectionContractError, "not found"):
            self.correct()
        self.assertEqual(self.corrections.correction_count(), 0)
        self.authorize()
        self.assertFalse(self.correct()["idempotent_replay"])

    def test_wrong_action_binding_rejected_without_history_change(self):
        self.authorize()
        before = self.stored_original()
        forged = fictional_correction()
        forged["action"] = "ACT2"
        with self.assertRaisesRegex(CorrectionContractError, "binding mismatch"):
            self.correct(forged)
        self.assertEqual(self.stored_original(), before)
        self.assertEqual(self.corrections.correction_count(), 0)

    def test_correction_precommit_crash_preserves_original(self):
        self.authorize()
        before = self.stored_original()
        with self.assertRaisesRegex(RuntimeError, "before commit"):
            self.correct(failure_point="before_commit")
        self.assertEqual(self.stored_original(), before)
        self.assertEqual(self.corrections.correction_count(), 0)
        self.assertFalse(self.correct()["idempotent_replay"])

    def test_correction_postcommit_crash_recovers_without_duplicate(self):
        self.authorize()
        with self.assertRaisesRegex(RuntimeError, "after commit"):
            self.correct(failure_point="after_commit")
        self.assertTrue(self.correct(ledger=FictionalCorrectionLedger(self.path))["idempotent_replay"])
        self.assertEqual(self.original.receipt_count(), 1)
        self.assertEqual(self.corrections.correction_count(), 1)

    def test_concurrent_corrections_against_actual_receipt(self):
        self.authorize()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(
                lambda _: self.correct(ledger=FictionalCorrectionLedger(self.path)),
                range(16),
            ))
        self.assertEqual(sum(not r["idempotent_replay"] for r in results), 1)
        self.assertEqual(sum(r["idempotent_replay"] for r in results), 15)
        self.assertEqual(self.original.receipt_count(), 1)
        self.assertEqual(self.corrections.correction_count(), 1)

    def test_second_correction_is_linear_not_a_fork(self):
        self.authorize()
        self.correct()
        second = fictional_correction(
            correction_id="C2", parent="C1", grant_nonce="correction-nonce-2",
        )
        self.assertEqual(self.correct(second)["parent_event_id"], "C1")
        with self.assertRaisesRegex(CorrectionContractError, "fork"):
            self.correct(fictional_correction(
                correction_id="C3", grant_nonce="correction-nonce-3",
            ))
        self.assertEqual(self.original.receipt_count(), 1)
        self.assertEqual(self.corrections.correction_count(), 2)


if __name__ == "__main__":
    unittest.main()
