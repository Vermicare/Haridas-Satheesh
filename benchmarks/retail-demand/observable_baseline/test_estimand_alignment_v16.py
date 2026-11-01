"""Fictional negative controls and a preserved v1.5 aggregate audit; no raw data."""
import copy
import json
import unittest
from pathlib import Path
from estimand_alignment_v16 import AuditError, audit_v15, toy_cluster_intervals

class AlignmentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preserved = json.loads((Path(__file__).parent / "STORE_DISJOINT_V15_RESULT.json").read_text(encoding="utf-8"))

    def test_preserved_v15_gate_remains_failed(self):
        result = audit_v15(self.preserved)
        self.assertFalse(result["preserved_predeclared_v15_gate_passed"])
        self.assertAlmostEqual(result["day_weighted_mae_delta_weekday_minus_last"], -0.0204538718929255)
        self.assertAlmostEqual(result["series_macro_mae_delta_weekday_minus_last"], -0.014229287574404765)
        self.assertEqual(result["day_weighted_store_cluster_ci95"].split(":")[0], "TBD")

    def test_fictional_false_confidence_from_mismatched_estimands(self):
        # 100 FICTIONAL independent stores, one series each. Both point
        # estimates favor weekday, but only the series-macro CI excludes zero.
        toy = toy_cluster_intervals([(1, -1.0)] * 80 + [(7, 0.5)] * 20)
        self.assertLess(toy["series_macro_ci95"][1], 0)
        self.assertLess(toy["day_weighted_ci95"][0], 0)
        self.assertGreater(toy["day_weighted_ci95"][1], 0)
        self.assertTrue(toy["fictional_only"])

    def test_invalid_and_missing_aggregate_rejected(self):
        for mutate in (lambda r: r.update(experiment_id="different"),
                       lambda r: r["metrics"].pop("weekday_median_last4_series_macro_mae"),
                       lambda r: r["metrics"].update(weekday_median_last4_day_weighted_mae=float("nan")),
                       lambda r: r["metrics"].update(weekday_median_minus_last_observed_series_macro_delta=123),
                       lambda r: r["primary_gate"].update(conditional_store_transfer_gate_passed="false")):
            with self.subTest(mutate=mutate):
                report = copy.deepcopy(self.preserved)
                mutate(report)
                with self.assertRaises(AuditError):
                    audit_v15(report)

    def test_toy_invalid_inputs_rejected(self):
        for rows in ([(0, 1.), (1, 0.)], [(1, float("nan")), (1, 0.)],
                     [(True, 0.), (1, 0.)], [(1, 0.)]):
            with self.subTest(rows=rows), self.assertRaises(AuditError):
                toy_cluster_intervals(rows)

if __name__ == "__main__":
    unittest.main()
