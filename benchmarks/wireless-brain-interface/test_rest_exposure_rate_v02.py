"""Adversarial tests for fictional sample-time WBI rest exposure, no EEG data."""
import json
import unittest
from rest_exposure_rate_v02 import Action, Recording, Segment, demo, evaluate, validate


class RestExposureRateTests(unittest.TestCase):
    def setUp(self):
        self.rec = Recording(100, 6000)
        self.seg = (Segment(0, 2000, "T0"), Segment(2000, 4000, "T1"), Segment(4000, 6000, "T0"))
        self.actions = (Action(0, "ungated", "T1"), Action(1999, "ungated", "T2"),
                        Action(2000, "ungated", "T1"), Action(5999, "ungated", "T1"))

    def test_correct_rest_time_denominator(self):
        out = evaluate(self.rec, self.seg, self.actions)
        self.assertEqual(out["rest_samples"], 4000)
        self.assertEqual(out["policies"]["ungated"]["rest_actions"], 3)
        self.assertEqual(out["policies"]["ungated"]["rest_actions_per_minute"], 4.5)

    def test_segmentation_invariant(self):
        split = (Segment(0, 1000, "T0"), Segment(1000, 2000, "T0"), *self.seg[1:])
        self.assertEqual(evaluate(self.rec, self.seg, self.actions), evaluate(self.rec, split, self.actions))

    def test_half_open_boundary(self):
        out = evaluate(self.rec, self.seg, (Action(1999, "gate", "T1"), Action(2000, "gate", "T1")))
        self.assertEqual(out["policies"]["gate"]["rest_actions"], 1)
        self.assertEqual(out["policies"]["gate"]["imagery_actions"], 1)

    def test_gap_rejected(self):
        with self.assertRaisesRegex(ValueError, "gap"):
            validate(self.rec, (Segment(0, 1999, "T0"), *self.seg[1:]), ())

    def test_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            validate(self.rec, (Segment(0, 2001, "T0"), *self.seg[1:]), ())

    def test_out_of_order_rejected(self):
        with self.assertRaisesRegex(ValueError, "unordered"):
            validate(self.rec, self.seg[::-1], ())

    def test_missing_initial_rest_rejected_when_gap(self):
        with self.assertRaisesRegex(ValueError, "gap"):
            validate(self.rec, self.seg[1:], ())

    def test_truncated_final_annotation_rejected(self):
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate(self.rec, (*self.seg[:-1], Segment(4000, 5999, "T0")), ())

    def test_missing_rest_rejected(self):
        with self.assertRaisesRegex(ValueError, "exposure"):
            validate(self.rec, (Segment(0, 6000, "T1"),), ())

    def test_missing_imagery_rejected(self):
        with self.assertRaisesRegex(ValueError, "exposure"):
            validate(self.rec, (Segment(0, 6000, "T0"),), ())

    def test_zero_length_segment_rejected(self):
        with self.assertRaisesRegex(ValueError, "interval"):
            validate(self.rec, (Segment(0, 0, "T0"), *self.seg), ())

    def test_invalid_metadata_rejected(self):
        for rec in (Recording(0, 6000), Recording(True, 6000), Recording(100, 0), Recording(100, 1.5)):
            with self.subTest(rec=rec), self.assertRaisesRegex(ValueError, "metadata"):
                validate(rec, self.seg, ())

    def test_bad_action_timestamp_rejected(self):
        for sample in (-1, 6000, 1.5, True):
            with self.subTest(sample=sample), self.assertRaisesRegex(ValueError, "sample"):
                validate(self.rec, self.seg, (Action(sample, "gate", "T1"),))

    def test_duplicate_action_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(self.rec, self.seg, (Action(1, "gate", "T1"), Action(1, "gate", "T2")))

    def test_unknown_policy_and_direction_rejected(self):
        for action in (Action(1, "other", "T1"), Action(1, "gate", "T0")):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, "policy"):
                validate(self.rec, self.seg, (action,))

    def test_no_actions_zero_rate(self):
        self.assertEqual(evaluate(self.rec, self.seg, ())["policies"]["gate"]["rest_actions_per_minute"], 0)

    def test_demo_deterministic_and_no_real_claim(self):
        self.assertEqual(demo(), demo())
        data = json.loads(demo())
        self.assertFalse(data["real_eeg_evaluated"])
        self.assertFalse(data["decoder_trained"])
        self.assertEqual(data["evidence_class"], "FICTIONAL_TIMESTAMP_CONTRACT_ONLY")


if __name__ == "__main__":
    unittest.main()
