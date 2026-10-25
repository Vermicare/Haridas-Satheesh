"""Adversarial tests for fictional WBI rest-aware evaluation; no EEG data."""
import dataclasses
import math
import unittest
from rest_aware_evaluation_contract import (
    acts, choose_thresholds, demo, evaluate, fictional_rows, score, validate,
)

class RestAwareContractTests(unittest.TestCase):
    def setUp(self):
        self.cal = fictional_rows("calibration")
        self.test = fictional_rows("test")

    def test_demo_is_deterministic(self):
        self.assertEqual(demo(), demo())
        self.assertIn('"FICTIONAL_CONTRACT_ONLY"', demo())

    def test_rest_is_included_in_ungated_denominator(self):
        m = score(self.test, "ungated", .5)
        self.assertEqual((m["rest_events"], m["acted_rest"]), (6, 6))
        self.assertEqual(m["rest_false_action_per_event"], 1)
        self.assertEqual((m["imagery_events"], m["acted_total"]), (6, 12))

    def test_confidence_only_baseline_not_implicitly_rest_aware(self):
        m = score(self.test, "abstention", .75)
        self.assertEqual((m["acted_rest"], m["acted_imagery"]), (3, 6))

    def test_gate_can_reject_high_confidence_rest(self):
        m = score(self.test, "gate", .75, .3)
        self.assertEqual((m["acted_rest"], m["acted_imagery"]), (0, 6))

    def test_calibration_only_thresholds(self):
        changed = [dataclasses.replace(r, label="T2" if r.label == "T1" else r.label)
                   for r in self.test]
        self.assertEqual(choose_thresholds(self.cal), evaluate(self.cal, changed)["thresholds"])
        self.assertEqual(evaluate(self.cal, self.test)["thresholds"],
                         evaluate(self.cal, changed)["thresholds"])

    def test_disjoint_frozen_subject_membership(self):
        with self.assertRaisesRegex(ValueError, "leakage"):
            validate([dataclasses.replace(self.cal[0], split="test")] + self.test, "test")

    def test_missing_all_rest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "denominator"):
            validate([r for r in self.test if r.label != "T0"], "test")

    def test_partial_rest_omission_is_not_detectable_without_source_count(self):
        # Explicit known limitation: some rest events present != all rest events present.
        partial = [r for r in self.test if not (r.label == "T0" and r.event_id.endswith("-0"))]
        self.assertEqual(len(validate(partial, "test")), 9)

    def test_missing_all_imagery_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "denominator"):
            validate([r for r in self.test if r.label == "T0"], "test")

    def test_duplicate_event_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(self.test + [self.test[0]], "test")

    def test_unknown_label_rejected(self):
        with self.assertRaisesRegex(ValueError, "label"):
            validate([dataclasses.replace(self.test[0], label="T3")] + self.test[1:], "test")

    def test_invalid_scores_rejected(self):
        for value in (math.nan, math.inf, -math.inf, -0.1, 1.1, True, "0.9"):
            with self.subTest(value=value):
                for field in ("p_left", "drift"):
                    with self.assertRaisesRegex(ValueError, "score"):
                        validate([dataclasses.replace(self.test[0], **{field: value})]
                                 + self.test[1:], "test")

    def test_bad_threshold_rejected(self):
        for value in (math.nan, math.inf, -1, 2, True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "threshold"):
                    score(self.test, "gate", value, .3)

    def test_unknown_policy_rejected(self):
        with self.assertRaisesRegex(ValueError, "policy"):
            acts(self.test[0], "imaginary", .5)

    def test_null_risk_for_no_actions_not_nan(self):
        m = score(self.test, "gate", 1.0, 0.0)
        self.assertEqual(m["acted_total"], 0)
        self.assertIsNone(m["incorrect_action_risk"])

    def test_no_real_data_or_maturity_claim(self):
        out = evaluate(self.cal, self.test)
        self.assertFalse(out["real_eeg_evaluated"])
        self.assertFalse(out["trained_decoder"])
        self.assertFalse(out["clinical_validation"])
        self.assertIn("event-level", out["limitations"])

if __name__ == "__main__":
    unittest.main()
