"""Fictional-only regression tests for common WBI decision opportunities."""
import json
import unittest
from dataclasses import replace
from rest_exposure_rate_v02 import Recording, Segment
from matched_opportunity_contract_v03 import Decision, evaluate, demo


class MatchedOpportunityContractTests(unittest.TestCase):
    def setUp(self):
        self.rec = Recording(100, 6000)
        self.segments = (Segment(0, 2000, "T0"), Segment(2000, 4000, "T1"), Segment(4000, 6000, "T0"))
        self.stamps = (0, 1000, 2000, 3000, 4000, 5000)
        self.grid = [Decision(s, p, None) for p in ("ungated", "abstention", "gate") for s in self.stamps]

    def run_grid(self, grid=None, stamps=None, segments=None, tolerance=0.05):
        return evaluate(self.rec, self.segments if segments is None else segments,
                        self.stamps if stamps is None else stamps,
                        self.grid if grid is None else grid, tolerance)

    def set_choice(self, policy, sample, direction):
        return [replace(d, direction=direction) if d.policy == policy and d.sample == sample else d for d in self.grid]

    def test_zero_action_not_comparable(self):
        out = self.run_grid()
        self.assertFalse(out["comparison"]["comparable"])
        self.assertIsNone(out["comparison"]["gate_minus_abstention_incorrect_action_risk"])
        self.assertIsNone(out["policies"]["gate"]["incorrect_action_risk"])

    def test_rest_action_rate_uses_seconds_not_event_count(self):
        out = self.run_grid(self.set_choice("gate", 0, "T1"))
        self.assertEqual(out["policies"]["gate"]["rest_false_actions_per_minute"], 1.5)
        self.assertEqual(out["policies"]["gate"]["rest_rate_exact_denominator"], 4000)

    def test_wrong_direction_is_incorrect_even_during_imagery(self):
        out = self.run_grid(self.set_choice("gate", 2000, "T2"))
        self.assertEqual(out["policies"]["gate"]["imagery_wrong_direction_actions"], 1)
        self.assertEqual(out["policies"]["gate"]["incorrect_action_risk"], 1)
        self.assertEqual(out["policies"]["gate"]["rest_false_actions_per_minute"], 0)

    def test_correct_direction_is_counted(self):
        out = self.run_grid(self.set_choice("gate", 2000, "T1"))
        self.assertEqual(out["policies"]["gate"]["correct_action_recall"], 0.5)
        self.assertEqual(out["policies"]["gate"]["incorrect_action_risk"], 0)

    def test_matched_coverage_enables_comparison(self):
        grid = self.set_choice("gate", 2000, "T1")
        grid = [replace(d, direction="T2") if d.policy == "abstention" and d.sample == 2000 else d for d in grid]
        out = self.run_grid(grid)
        self.assertTrue(out["comparison"]["comparable"])
        self.assertEqual(out["comparison"]["gate_minus_abstention_incorrect_action_risk"], -1)

    def test_unmatched_coverage_withholds_risk_delta(self):
        grid = self.set_choice("gate", 2000, "T1")
        grid = [replace(d, direction="T1") if d.policy == "abstention" and d.sample in (2000, 3000) else d for d in grid]
        out = self.run_grid(grid)
        self.assertFalse(out["comparison"]["comparable"])
        self.assertIsNone(out["comparison"]["gate_minus_abstention_incorrect_action_risk"])

    def test_segmentation_invariance(self):
        split = (Segment(0, 1000, "T0"), Segment(1000, 2000, "T0"), *self.segments[1:])
        self.assertEqual(self.run_grid(), self.run_grid(segments=split))

    def test_half_open_boundary_label(self):
        out = self.run_grid(self.set_choice("gate", 2000, "T1"))
        self.assertEqual(out["policies"]["gate"]["rest_false_actions"], 0)

    def test_missing_policy_decision_rejected(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.run_grid(self.grid[:-1])

    def test_duplicate_decision_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_grid(self.grid + self.grid[:1])

    def test_extra_timestamp_decision_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            self.run_grid(self.grid + [Decision(1, "gate", "T1")])

    def test_unsorted_and_duplicate_opportunities_rejected(self):
        for stamps in ((0, 2000, 1000), (0, 0, 2000)):
            with self.subTest(stamps=stamps), self.assertRaisesRegex(ValueError, "increasing"):
                self.run_grid(stamps=stamps)

    def test_out_of_range_and_bool_opportunities_rejected(self):
        for stamps in ((-1,), (6000,), (True,), (1.5,), ()):
            with self.subTest(stamps=stamps), self.assertRaisesRegex(ValueError, "opportunity"):
                self.run_grid(stamps=stamps)

    def test_invalid_policy_and_direction_rejected(self):
        for bad in (Decision(0, "other", None), Decision(0, "gate", "T0"), Decision(0, "gate", 0)):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "policy or direction"):
                self.run_grid(self.grid + [bad])

    def test_invalid_tolerance_rejected(self):
        for bad in (-0.01, 1.01, float("nan"), True, "0.05"):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "tolerance"):
                self.run_grid(tolerance=bad)

    def test_rest_only_opportunity_grid_rejected(self):
        stamps = (0, 1000, 4000, 5000)
        grid = [d for d in self.grid if d.sample in stamps]
        with self.assertRaisesRegex(ValueError, "both rest and imagery"):
            self.run_grid(grid=grid, stamps=stamps)

    def test_annotation_gap_rejected(self):
        with self.assertRaisesRegex(ValueError, "gap"):
            self.run_grid(segments=(Segment(0, 1999, "T0"), *self.segments[1:]))

    def test_demo_is_deterministic_and_explicitly_fictional(self):
        self.assertEqual(demo(), demo())
        report = json.loads(demo())
        self.assertFalse(report["real_eeg_evaluated"])
        self.assertFalse(report["decoder_trained"])
        self.assertIn("FICTIONAL", report["evidence_class"])
        self.assertFalse(report["comparison"]["comparable"])


if __name__ == "__main__":
    unittest.main()
