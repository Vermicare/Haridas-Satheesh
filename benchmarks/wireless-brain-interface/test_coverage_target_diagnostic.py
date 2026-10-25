"""Synthetic contract checks for the coverage-target diagnostic (stdlib only)."""
import json
import unittest
from dataclasses import replace

from coverage_target_diagnostic import (
    TEST_COVERAGE_TOLERANCE, choose_thresholds, evaluate, run,
)
from synthetic_evaluator import Row, SEED_CAL, SEED_TEST, fixture


class DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal = fixture(SEED_CAL)
        cls.test = fixture(SEED_TEST)

    def test_selection_does_not_read_labels(self):
        inverted = [replace(r, y=1-r.y) for r in self.cal]
        for policy in ("confidence", "gate"):
            for target in (.30, .50, .70):
                self.assertEqual(choose_thresholds(self.cal, target, policy),
                                 choose_thresholds(inverted, target, policy))

    def test_selection_does_not_read_segment_names(self):
        renamed = [replace(r, segment="unknown") for r in self.cal]
        for policy in ("confidence", "gate"):
            self.assertEqual(choose_thresholds(self.cal, .50, policy),
                             choose_thresholds(renamed, .50, policy))

    def test_policy_selection_does_not_use_test_rows(self):
        other = fixture(999, 100)
        a = run(self.cal, self.test)
        b = run(self.cal, other)
        for left, right in zip(a["results"], b["results"]):
            for policy in ("confidence", "gate"):
                self.assertEqual(left["policies"][policy]["selection"],
                                 right["policies"][policy]["selection"])

    def test_repeat_determinism(self):
        self.assertEqual(json.dumps(run(self.cal, self.test), sort_keys=True),
                         json.dumps(run(self.cal, self.test), sort_keys=True))

    def test_counts_and_denominators(self):
        d = run(self.cal, self.test)
        for target in d["results"]:
            for policy in ("confidence", "gate"):
                item = target["policies"][policy]
                self.assertEqual(item["test"]["n"], 240)
                self.assertEqual(item["nominal"]["n"] + item["drift"]["n"], 240)
                self.assertEqual(item["test"]["acted"], item["nominal"]["acted"] + item["drift"]["acted"])
                self.assertEqual(item["test"]["incorrect"], item["nominal"]["incorrect"] + item["drift"]["incorrect"])
                self.assertEqual(item["test"]["acted"], item["test"]["incorrect"] + item["test"]["correct"])

    def test_comparability_flag_guards_risk_delta(self):
        for item in run(self.cal, self.test)["results"]:
            self.assertEqual(item["within_test_coverage_tolerance"],
                             item["test_coverage_gap"] <= TEST_COVERAGE_TOLERANCE and
                             all(item["policies"][p]["test"]["acted"] > 0 for p in ("confidence", "gate")))
            if not item["within_test_coverage_tolerance"]:
                self.assertIsNone(item["gate_minus_confidence_risk"])

    def test_no_acted_rows_have_no_defined_risk(self):
        self.assertIsNone(evaluate([Row(1, .9, .1, "nominal")], [False])["incorrect_action_risk"])

    def test_invalid_targets_rejected(self):
        for target in (-1, 0, 1.1):
            with self.assertRaises(ValueError):
                choose_thresholds(self.cal, target, "confidence")

    def test_empty_inputs_rejected(self):
        with self.assertRaises(ValueError):
            run([], self.test)
        with self.assertRaises(ValueError):
            run(self.cal, [])
        with self.assertRaises(ValueError):
            choose_thresholds([], .5, "gate")

    def test_unknown_policy_rejected(self):
        with self.assertRaises(ValueError):
            choose_thresholds(self.cal, .5, "invented")

    def test_held_out_labels_do_not_change_thresholds(self):
        inverted = [replace(r, y=1-r.y) for r in self.test]
        original, changed = run(self.cal, self.test), run(self.cal, inverted)
        for a, b in zip(original["results"], changed["results"]):
            for p in ("confidence", "gate"):
                self.assertEqual(a["policies"][p]["selection"], b["policies"][p]["selection"])
                self.assertEqual(a["policies"][p]["test"]["acted"], b["policies"][p]["test"]["acted"])


if __name__ == "__main__":
    unittest.main()
