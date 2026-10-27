"""Fictional-only negative controls for the read-only EPMO evidence bridge."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from durable_receipt_sandbox import initialize, record_simulated_receipt, record_simulated_correction
from reconcile_fictional_replay import ReconciliationError, reconcile

SCENARIO = json.loads(Path(__file__).with_name("synthetic_scenario.json").read_text(encoding="utf-8"))


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "fictional.sqlite3"
        initialize(self.path)
        self.kwargs = dict(request_id="fictional-RAID-01", receipt_id="r1", approval_id="e3",
                           action="publish_status", scope="fictional-program")
        self.scenario = copy.deepcopy(SCENARIO)

    def seed(self, *, correct=True):
        record_simulated_receipt(self.path, **self.kwargs)
        if correct:
            record_simulated_correction(self.path, request_id="fictional-RAID-01",
                                        receipt_id="r1", reason="fictional status correction")

    def test_original_six_event_replay_matches_corrected_ledger(self):
        self.seed()
        report = reconcile(self.scenario, self.path)
        self.assertTrue(report["reconciled"])
        self.assertEqual((report["accepted_events"], report["rejected_events"],
                          report["accepted_executions"], report["corrected_receipts"]), (4, 2, 1, 1))
        self.assertFalse(report["identity_authenticated"])
        self.assertEqual(report["external_actions"], 0)

    def test_report_is_deterministic(self):
        self.seed()
        self.assertEqual(reconcile(self.scenario, self.path), reconcile(self.scenario, self.path))

    def test_missing_receipt_rejected(self):
        with self.assertRaisesRegex(ReconciliationError, "missing"):
            reconcile(self.scenario, self.path)

    def test_uncorrected_receipt_rejected(self):
        self.seed(correct=False)
        with self.assertRaisesRegex(ReconciliationError, "changed"):
            reconcile(self.scenario, self.path)

    def test_extra_receipt_rejected(self):
        self.seed()
        record_simulated_receipt(self.path, request_id="fictional-RAID-02",
                                 receipt_id="r-extra", approval_id="a2",
                                 action="publish_status", scope="fictional-program")
        with self.assertRaisesRegex(ReconciliationError, "extra"):
            reconcile(self.scenario, self.path)

    def test_changed_scope_rejected(self):
        record_simulated_receipt(self.path, **{**self.kwargs, "scope": "wrong-scope"})
        record_simulated_correction(self.path, request_id="fictional-RAID-01",
                                    receipt_id="r1", reason="fictional status correction")
        with self.assertRaisesRegex(ReconciliationError, "changed"):
            reconcile(self.scenario, self.path)

    def test_changed_approval_rejected(self):
        record_simulated_receipt(self.path, **{**self.kwargs, "approval_id": "forged-approval"})
        record_simulated_correction(self.path, request_id="fictional-RAID-01",
                                    receipt_id="r1", reason="fictional status correction")
        with self.assertRaises(ReconciliationError):
            reconcile(self.scenario, self.path)

    def test_changed_correction_reason_rejected(self):
        record_simulated_receipt(self.path, **self.kwargs)
        record_simulated_correction(self.path, request_id="fictional-RAID-01",
                                    receipt_id="r1", reason="different reason")
        with self.assertRaises(ReconciliationError):
            reconcile(self.scenario, self.path)

    def test_rejected_early_execute_not_counted(self):
        self.seed()
        self.assertEqual(reconcile(self.scenario, self.path)["accepted_executions"], 1)

    def test_modified_scenario_detected_against_original_ledger(self):
        self.seed()
        self.scenario["events"][3]["payload"]["scope"] = "altered-scope"
        with self.assertRaises(ReconciliationError):
            reconcile(self.scenario, self.path)

    def test_nonfictional_origin_rejected(self):
        self.seed()
        self.scenario["origin"] = "REAL"
        with self.assertRaises(ReconciliationError):
            reconcile(self.scenario, self.path)

    def test_replay_with_no_accepted_execution_requires_empty_ledger(self):
        self.scenario["events"] = self.scenario["events"][:3]
        self.assertEqual(reconcile(self.scenario, self.path)["accepted_executions"], 0)


if __name__ == "__main__":
    unittest.main()
