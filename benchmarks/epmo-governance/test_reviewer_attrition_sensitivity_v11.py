"""Fictional selection-bias negative controls; no human data."""
import json
import pathlib
import random
import unittest
from reviewer_attrition_sensitivity_v11 import (CASES, SCENARIOS, permutation_pvalue,
    retained, reviewer_rate, run)


class ReviewerAttritionSensitivityTests(unittest.TestCase):
    def test_finite_grid(self):
        rng = random.Random(4)
        for _ in range(50):
            value = reviewer_rate(rng, 0.2)
            self.assertTrue(0 <= value <= 1)
            self.assertAlmostEqual(value * CASES, round(value * CASES))

    def test_invalid_probabilities_and_icc_fail_closed(self):
        for p, icc in [(0, .1), (1, .1), (float('nan'), .1), (.2, -1),
                       (.2, 1), (.2, float('inf'))]:
            with self.assertRaises(ValueError): reviewer_rate(random.Random(1), p, icc)

    def test_selective_missingness_is_treatment_and_outcome_dependent(self):
        rng = random.Random(0)
        high = sum(not retained(rng, "null_selective_treatment_dropout", "treatment", 5 / CASES)
                   for _ in range(2000))
        rng = random.Random(0)
        low = sum(not retained(rng, "null_selective_treatment_dropout", "treatment", 1 / CASES)
                  for _ in range(2000))
        self.assertGreater(high, 1400)
        self.assertLess(low, 200)

    def test_random_dropout_same_arm_logic(self):
        self.assertEqual(
            [retained(random.Random(i), "null_random_25pct", "control", 0) for i in range(50)],
            [retained(random.Random(i), "null_random_25pct", "treatment", 1) for i in range(50)])

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError): retained(random.Random(1), "wrong", "control", .2)

    def test_permutation_invariant_under_identical_arms(self):
        self.assertEqual(permutation_pvalue([.2]*12, [.2]*12, random.Random(2)), 1)

    def test_invalid_permutation_inputs(self):
        for a,b in [([], [.2]), ([float('nan')], [.2]), ([.2], [float('inf')]), ([-.1], [.2])]:
            with self.assertRaises(ValueError): permutation_pvalue(a, b, random.Random(1))
        with self.assertRaises(ValueError): permutation_pvalue([.2], [.2], random.Random(1), 18)

    def test_small_run_deterministic(self):
        a = run(seed=8, replications=20, permutations=19, reviewers_per_arm=12)
        self.assertEqual(a, run(seed=8, replications=20, permutations=19, reviewers_per_arm=12))
        self.assertEqual([r['scenario'] for r in a['results']], list(SCENARIOS))
        self.assertEqual(a['observed_human_participants'], 0)
        self.assertEqual(a['observed_effect'], 'TBD')
        self.assertEqual(a['external_actions'], 0)

    def test_committed_default_result_reproduces_exactly(self):
        path = pathlib.Path(__file__).with_name("REVIEWER_ATTRITION_V11_RESULT.json")
        self.assertEqual(run(), json.loads(path.read_text(encoding="utf-8")))

    def test_invalid_run_parameters(self):
        for kwargs in ({'seed': 1.5}, {'replications': 19}, {'permutations': 18},
                       {'reviewers_per_arm': 11}):
            with self.assertRaises(ValueError): run(**kwargs)


if __name__ == '__main__': unittest.main()
