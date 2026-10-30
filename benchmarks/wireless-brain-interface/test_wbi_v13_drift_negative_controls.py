"""Fictional-only negative controls; no EEG labels or physical measurements."""
import unittest
from dataclasses import replace
from pathlib import Path
from wbi_matched_coverage_v11 import frozen_module
from wbi_v13_drift_negative_controls import permute_drift, evaluate


class DriftControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = frozen_module(Path(__file__).with_name("synthetic_evaluator.py"))

    def test_permutation_is_deterministic(self):
        rows = self.frozen.fixture(123)
        self.assertEqual(permute_drift(rows, 7), permute_drift(rows, 7))

    def test_permutation_preserves_all_non_drift_fields(self):
        rows = self.frozen.fixture(123)
        shifted = permute_drift(rows, 7)
        self.assertEqual([replace(r, drift=0) for r in rows],
                         [replace(r, drift=0) for r in shifted])

    def test_permutation_preserves_drift_multiset(self):
        rows = self.frozen.fixture(123)
        self.assertEqual(sorted(r.drift for r in rows),
                         sorted(r.drift for r in permute_drift(rows, 7)))

    def test_permutation_changes_order(self):
        rows = self.frozen.fixture(123)
        self.assertNotEqual([r.drift for r in rows],
                            [r.drift for r in permute_drift(rows, 7)])

    def test_baseline_invariant(self):
        out = evaluate(self.frozen, 5)
        totals = [v["total_baseline_wrong"] for v in out["cases"].values()]
        self.assertEqual(totals, [totals[0]]*3)

    def test_exact_coverage_and_pair_counts(self):
        out = evaluate(self.frozen, 5)
        self.assertEqual(out["acted_per_pair"], 120)
        for case in out["cases"].values():
            self.assertEqual(len(case["records"]), 5)
            self.assertEqual(case["better"]+case["tied"]+case["worse"], 5)

    def test_original_200_pair_matches_v12(self):
        out = evaluate(self.frozen)
        orig = out["cases"]["informative_original"]
        self.assertEqual((orig["total_baseline_wrong"], orig["total_candidate_wrong"]), (3716, 3645))
        self.assertEqual((orig["better"], orig["tied"], orig["worse"]), (76, 86, 38))

    def test_invalid_pair_count(self):
        for n in (0, -1, 10001):
            with self.assertRaises(ValueError):
                evaluate(self.frozen, n)


if __name__ == "__main__":
    unittest.main()
