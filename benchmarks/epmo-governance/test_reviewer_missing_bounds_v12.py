"""Fictional-only adversarial checks for no-assumption reviewer bounds."""
import json
import unittest
from fractions import Fraction
from pathlib import Path

from reviewer_missing_bounds_v12 import (
    ASSIGNED_PER_ARM, CASES, SCENARIOS, arm_bounds, contrast_bounds,
    fictional_scenario, run,
)


def f(value):
    n, d = value["exact"].split("/")
    return Fraction(int(n), int(d))


class MissingBoundsContract(unittest.TestCase):
    def test_no_missing_is_point_identified(self):
        x = arm_bounds(3, [0, 7, 13])
        self.assertEqual(f(x["assigned_mean_lower"]), f(x["assigned_mean_upper"]))
        self.assertEqual(f(x["assigned_mean_lower"]), Fraction(20, 39))

    def test_all_missing_is_unidentified(self):
        x = arm_bounds(4, [])
        self.assertEqual((f(x["assigned_mean_lower"]), f(x["assigned_mean_upper"])), (0, 1))
        self.assertIsNone(x["complete_case_rate"])

    def test_one_missing_widens_by_one_over_assigned(self):
        x = arm_bounds(5, [1, 2, 3, 4])
        self.assertEqual(f(x["assigned_mean_upper"]) - f(x["assigned_mean_lower"]), Fraction(1, 5))

    def test_extremes_are_attainable(self):
        x = arm_bounds(4, [1, 13])
        self.assertEqual(f(x["assigned_mean_lower"]), Fraction(14, 52))
        self.assertEqual(f(x["assigned_mean_upper"]), Fraction(40, 52))

    def test_contrast_extremes(self):
        c, t = arm_bounds(2, [13]), arm_bounds(2, [0])
        d = contrast_bounds(c, t)
        self.assertEqual(f(d["assigned_difference_lower"]), -1)
        self.assertEqual(f(d["assigned_difference_upper"]), 0)
        self.assertTrue(d["zero_in_identification_interval"])

    def test_no_completers_contrast_does_not_invent_complete_case(self):
        d = contrast_bounds(arm_bounds(2, []), arm_bounds(2, [1]))
        self.assertIsNone(d["complete_case_difference"])

    def test_reject_invalid_assigned(self):
        for n in (0, -1, True, 1.2, "2"):
            with self.subTest(n=n), self.assertRaises(ValueError):
                arm_bounds(n, [])

    def test_reject_invalid_counts(self):
        for v in ([14], [-1], [True], [2.0], ["3"], (2,)):
            with self.subTest(v=v), self.assertRaises(ValueError):
                arm_bounds(2, v)

    def test_reject_overfilled_arm(self):
        with self.assertRaises(ValueError):
            arm_bounds(1, [0, 0])

    def test_reject_invalid_scenarios_and_seed(self):
        for scenario in ("unknown", "hypothetical_effect_complete"):
            with self.assertRaises(ValueError):
                fictional_scenario(1, scenario)
        with self.assertRaises(ValueError):
            fictional_scenario(True, SCENARIOS[0])

    def test_repeatability(self):
        self.assertEqual(run(), run())
        self.assertEqual(run()["assigned_per_arm"], ASSIGNED_PER_ARM)

    def test_different_missingness_mechanisms(self):
        a, b = run()["scenarios"]
        self.assertNotEqual(a["observed_fixture_sha256"], b["observed_fixture_sha256"])
        self.assertEqual(a["manual"]["assigned"], b["manual"]["assigned"])

    def test_sharp_bounds_contain_complete_case_when_defined(self):
        for seed in range(12):
            for scenario in SCENARIOS:
                z = fictional_scenario(seed, scenario, 12)
                for arm in ("manual", "worksheet"):
                    x = z[arm]
                    if x["complete_case_rate"] is not None:
                        self.assertLessEqual(f(x["assigned_mean_lower"]), f(x["complete_case_rate"]))
                        self.assertLessEqual(f(x["complete_case_rate"]), f(x["assigned_mean_upper"]))

    def test_result_is_aggregate_and_explicitly_fictional(self):
        out = run()
        self.assertEqual(out["observed_human_reviewers"], 0)
        self.assertEqual(out["external_actions"], 0)
        self.assertEqual(out["human_treatment_effect"], "TBD")
        for scenario in out["scenarios"]:
            self.assertEqual(len(scenario["observed_fixture_sha256"]), 64)
            self.assertNotIn("reviewer_id", json.dumps(scenario))
            self.assertNotIn("participant", json.dumps(scenario))

    def test_frozen_result_exact(self):
        expected = json.loads(Path(__file__).with_name("REVIEWER_MISSING_BOUNDS_V12_RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(run(), expected)


if __name__ == "__main__":
    unittest.main()
