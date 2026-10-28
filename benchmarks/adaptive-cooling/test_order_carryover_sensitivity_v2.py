"""Fictional-only deterministic tests; zero physical cooling observations."""
import json
import unittest

from order_carryover_sensitivity_v2 import analyze


class CarryoverSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zero = analyze(0.0)
        cls.warming = analyze(0.6)
        cls.cooling = analyze(-0.6)

    def test_all_six_factorial_schedules_enumerated(self):
        for case in (self.zero, self.warming, self.cooling):
            self.assertEqual(case['unique_balanced_block_orderings'], 720)
            for summary in case['bias_by_comparator'].values():
                self.assertEqual(sum(summary['rounded_bias_histogram'].values()), 720)

    def test_linear_drift_cancels_when_carryover_zero(self):
        for summary in self.zero['bias_by_comparator'].values():
            self.assertAlmostEqual(summary['min_c'], 0.0, places=10)
            self.assertAlmostEqual(summary['max_c'], 0.0, places=10)
            self.assertEqual(summary['zero_bias_schedule_count'], 720)

    def test_warming_carryover_can_create_false_cooling_advantage(self):
        for summary in self.warming['bias_by_comparator'].values():
            self.assertLess(summary['min_c'], -0.39)
            self.assertLessEqual(summary['max_c'], 1e-9)
            self.assertLess(summary['zero_bias_schedule_count'], 720)

    def test_cooling_carryover_can_create_false_disadvantage(self):
        for summary in self.cooling['bias_by_comparator'].values():
            self.assertGreater(summary['max_c'], 0.39)
            self.assertGreaterEqual(summary['min_c'], -1e-9)

    def test_sign_symmetry_and_seeded_schedule_bias(self):
        for key in self.warming['bias_by_comparator']:
            a = self.warming['bias_by_comparator'][key]
            b = self.cooling['bias_by_comparator'][key]
            self.assertAlmostEqual(a['min_c'], -b['max_c'], places=10)
            self.assertAlmostEqual(a['max_c'], -b['min_c'], places=10)
            self.assertAlmostEqual(self.warming['seeded_order_bias_c'][key],
                                   -self.cooling['seeded_order_bias_c'][key], places=10)

    def test_fail_closed_on_nonfinite_or_boolean_input(self):
        for invalid in (float('nan'), float('inf'), -float('inf'), True, '0.6', None):
            with self.subTest(invalid=repr(invalid)), self.assertRaises(ValueError):
                analyze(invalid)

    def test_no_physical_claims_and_strict_json(self):
        for case in (self.zero, self.warming, self.cooling):
            self.assertEqual(case['physical_measurements'], 0)
            self.assertFalse(case['physical_origin_authenticated'])
            self.assertFalse(case['performance_claim_permitted'])
            json.dumps(case, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
