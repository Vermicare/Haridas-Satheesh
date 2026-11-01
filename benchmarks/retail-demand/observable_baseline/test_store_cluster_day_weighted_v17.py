"""Fictional-only adversarial tests; real publisher outcomes are not fixtures."""
import unittest
from store_cluster_day_weighted_v17 import paired_store_cluster_day_ci
from retail_gate import EvidenceError


class DayWeightedClusterTests(unittest.TestCase):
    def test_exact_ratio_of_sums_not_series_macro(self):
        rows = [(1, 1, 1, 0., 1.), (1, 2, 1, 0., 1.), (2, 1, 7, 3.5, 0.)]
        result = paired_store_cluster_day_ci(rows, reps=100, seed=9)
        self.assertAlmostEqual(result['point_delta'], 1.5 / 9)
        self.assertEqual(result['store_count'], 2)
        self.assertEqual(result['series_count'], 3)
        self.assertEqual(result['scored_days'], 9)
        self.assertEqual(result['max_series_per_store'], 2)

    def test_cluster_dependence_and_seed_determinism(self):
        rows = [(s, p, 1, float(s % 3), float((s + 1) % 3)) for s in range(10) for p in range(4)]
        a = paired_store_cluster_day_ci(rows, reps=500, seed=17)
        b = paired_store_cluster_day_ci(list(reversed(rows)), reps=500, seed=17)
        self.assertEqual(a['store_cluster_ci95'], b['store_cluster_ci95'])
        self.assertEqual(a['point_delta'], b['point_delta'])
        self.assertEqual(a['series_count'], 40)
        self.assertEqual(a['store_count'], 10)

    def test_rejects_duplicate_and_single_cluster(self):
        with self.assertRaises(EvidenceError):
            paired_store_cluster_day_ci([(1, 1, 1, 1., 0.), (1, 1, 1, 1., 0.), (2, 1, 1, 0., 1.)], reps=100)
        with self.assertRaises(EvidenceError):
            paired_store_cluster_day_ci([(1, 1, 1, 1., 0.), (1, 2, 1, 0., 1.)], reps=100)

    def test_rejects_nonfinite_negative_boolean_and_zero_days(self):
        valid = [(1, 1, 1, 1., 0.), (2, 1, 1, 0., 1.)]
        invalid = [(1, 1, 0, 1., 0.), (1, 1, True, 1., 0.),
                   (1, 1, 1, float('nan'), 0.), (1, 1, 1, -1., 0.),
                   (1, 1, 1, 0., float('inf')), (1, 1, 1, 0., True)]
        for row in invalid:
            with self.subTest(row=row), self.assertRaises(EvidenceError):
                paired_store_cluster_day_ci([row, valid[1]], reps=100)

    def test_rejects_invalid_replicates(self):
        with self.assertRaises(EvidenceError):
            paired_store_cluster_day_ci([(1, 1, 1, 1., 0.), (2, 1, 1, 0., 1.)], reps=1)

if __name__ == '__main__':
    unittest.main()
