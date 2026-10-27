"""Assumption-based software tests; no participant data."""
import random
import unittest
from reviewer_power_sensitivity_v10 import (ALPHA, ARM_SIZES, NEGATIVE_CASES,
    permutation_pvalue, reviewer_rate, run)


class PowerSensitivityTests(unittest.TestCase):
    def test_rate_bounds_and_grid(self):
        rng = random.Random(12)
        for _ in range(100):
            value = reviewer_rate(rng, 0.2)
            self.assertTrue(0 <= value <= 1)
            self.assertEqual(value * NEGATIVE_CASES, round(value * NEGATIVE_CASES))

    def test_rho_zero_supported(self):
        self.assertTrue(0 <= reviewer_rate(random.Random(1), 0.2, 0) <= 1)

    def test_invalid_model_rejected(self):
        for p, rho in ((0, 0.1), (1, 0.1), (0.2, -0.1), (0.2, 1)):
            with self.assertRaises(ValueError): reviewer_rate(random.Random(1), p, rho)

    def test_identical_constant_arms_not_significant(self):
        p = permutation_pvalue([0.2] * 12, [0.2] * 12, random.Random(1))
        self.assertEqual(p, 1)

    def test_permutation_reproducible(self):
        a, b = [0] * 12, [1] * 12
        self.assertEqual(permutation_pvalue(a, b, random.Random(3)),
                         permutation_pvalue(a, b, random.Random(3)))
        self.assertLessEqual(permutation_pvalue(a, b, random.Random(3)), ALPHA)

    def test_invalid_permutation_count_rejected(self):
        with self.assertRaises(ValueError):
            permutation_pvalue([0], [1], random.Random(1), 9)

    def test_deterministic_synthetic_simulation(self):
        a = run(seed=2, replications=20, permutations=19)
        self.assertEqual(a, run(seed=2, replications=20, permutations=19))
        self.assertEqual(len(a["results"]), 2 * len(ARM_SIZES))
        self.assertEqual(a["observed_human_participants"], 0)
        self.assertEqual(a["observed_effect"], "TBD")
        self.assertEqual(a["external_actions"], 0)

    def test_bad_replications_rejected(self):
        with self.assertRaises(ValueError): run(replications=0)


if __name__ == "__main__":
    unittest.main()
