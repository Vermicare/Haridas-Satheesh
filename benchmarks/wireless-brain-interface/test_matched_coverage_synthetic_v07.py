"""Adversarial fictional contracts for WBI v0.7 exact-coverage evaluation."""
from __future__ import annotations

import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import matched_coverage_synthetic_v07 as v07
import synthetic_evaluator as frozen


class MatchedCoverageSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.cal = frozen.fixture(frozen.SEED_CAL)
        self.test = frozen.fixture(frozen.SEED_TEST)

    def test_original_evaluator_blob_is_unchanged(self):
        self.assertEqual(v07.frozen_identity()["git_blob"], v07.ORIGINAL_BLOB)

    def test_source_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "fake.py"
            bad.write_text("altered evaluator", encoding="utf-8")
            with patch.object(frozen, "__file__", str(bad)):
                with self.assertRaises(v07.GateError):
                    v07.frozen_identity()

    def test_exact_coverage_all_weights(self):
        for weight in v07.WEIGHTS:
            chosen = v07.rank_actions(self.test, weight)
            self.assertEqual(len(chosen), 120)
            self.assertEqual(len(set(chosen)), 120)

    def test_zero_weight_is_confidence_baseline(self):
        selected = v07.rank_actions(self.test, 0.0)
        self.assertEqual(selected, v07.rank_actions(self.test, v07.WEIGHTS[0]))

    def test_ties_are_resolved_by_original_index(self):
        rows = [frozen.Row(0, .9, .1, "nominal") for _ in range(5)]
        self.assertEqual(v07.rank_actions(rows, 0.2, 2), frozenset((0, 1)))

    def test_test_labels_cannot_affect_selected_actions(self):
        altered = [frozen.Row(1 - r.y, r.p1, r.drift, r.segment) for r in self.test]
        for weight in v07.WEIGHTS:
            self.assertEqual(v07.rank_actions(self.test, weight),
                             v07.rank_actions(altered, weight))

    def test_weight_selection_uses_calibration_only(self):
        chosen = v07.choose_weight(self.cal)
        self.assertIn(chosen, v07.WEIGHTS)
        self.assertEqual(chosen, v07.choose_weight(list(self.cal)))

    def test_reject_invalid_calibration_size(self):
        with self.assertRaises(v07.GateError):
            v07.choose_weight(self.cal[:-1])

    def test_reject_nan_and_invalid_count(self):
        with self.assertRaises(v07.GateError):
            v07.rank_actions(self.test, math.nan)
        with self.assertRaises(v07.GateError):
            v07.rank_actions(self.test, 0.0, 241)
        with self.assertRaises(v07.GateError):
            v07.rank_actions(self.test, -1.0)

    def test_reject_nonfinite_drift(self):
        bad = [frozen.Row(0, .9, math.nan, "drift")]
        with self.assertRaises(v07.GateError):
            v07.rank_actions(bad, 0.1, 1)

    def test_permutation_preserves_marginal_drift_and_labels(self):
        shuffled = v07.permute_test_drift(self.test, 12)
        self.assertEqual(sorted(r.drift for r in shuffled),
                         sorted(r.drift for r in self.test))
        self.assertEqual([(r.y, r.p1) for r in shuffled],
                         [(r.y, r.p1) for r in self.test])
        self.assertEqual(shuffled, v07.permute_test_drift(self.test, 12))

    def test_paired_counts_and_denominators(self):
        result = v07.evaluate_pair(self.test, .25)
        self.assertEqual(result["acted_each"], 120)
        self.assertEqual(result["total"], 240)
        self.assertEqual(result["coverage_each"], .5)
        self.assertEqual(result["candidate_minus_baseline_incorrect"],
                         result["candidate_incorrect"] - result["baseline_incorrect"])

    def test_no_weight_baseline_difference(self):
        result = v07.evaluate_pair(self.test, 0.0)
        self.assertEqual(result["candidate_minus_baseline_incorrect"], 0)
        self.assertEqual(result["different_action_decisions"], 0)

    def test_full_run_deterministic(self):
        a, b = v07.run(), v07.run()
        self.assertEqual(a, b)
        self.assertEqual(len(a["replicates"]), 12)
        self.assertEqual(a["aggregate"]["denominator_actions_each"], 1440)
        self.assertFalse(a["limitations"]["maturity_advanced"])
        for row in a["replicates"]:
            self.assertEqual(row["held_out"]["coverage_each"], .5)
            self.assertEqual(row["permuted_test_drift"]["coverage_each"], .5)


if __name__ == "__main__":
    unittest.main()
