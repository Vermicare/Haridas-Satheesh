"""Synthetic-only WBI stress diagnostic regression checks (stdlib only)."""
import json
from dataclasses import replace
import unittest

from synthetic_evaluator import Row, fixture
from coverage_target_diagnostic import run
from synthetic_regime_stress import (
    REGIMES, ROWS_PER_SPLIT, SEED_PAIRS, TARGETS,
    experiment, summarize, transform,
)


class StressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = fixture(1103, 40)

    def test_only_drift_changes(self):
        for regime in REGIMES:
            new = transform(self.base, regime, 9)
            self.assertEqual(len(new), len(self.base))
            for old, changed in zip(self.base, new):
                self.assertEqual((old.y, old.p1, old.segment),
                                 (changed.y, changed.p1, changed.segment))

    def test_original_is_identity(self):
        self.assertEqual(self.base, transform(self.base, "original", 7))

    def test_permutation_preserves_scores(self):
        self.assertEqual(sorted(r.drift for r in self.base),
                         sorted(r.drift for r in transform(self.base, "permuted", 7)))

    def test_inverted_and_constant(self):
        self.assertEqual([1 - r.drift for r in self.base],
                         [r.drift for r in transform(self.base, "inverted", 7)])
        self.assertEqual({0.5}, {r.drift for r in transform(self.base, "constant", 7)})

    def test_transform_does_not_use_labels(self):
        inverted = [replace(r, y=1-r.y) for r in self.base]
        for regime in REGIMES:
            a, b = transform(self.base, regime, 99), transform(inverted, regime, 99)
            self.assertEqual([r.drift for r in a], [r.drift for r in b])

    def test_unknown_regime_fails(self):
        with self.assertRaises(ValueError):
            transform(self.base, "invented", 99)

    def test_fixed_design_and_counts(self):
        result = experiment()
        self.assertEqual(len(result["cases"]), len(SEED_PAIRS) * len(REGIMES) * len(TARGETS))
        self.assertEqual(result["rows_per_split"], ROWS_PER_SPLIT)
        for c in result["cases"]:
            self.assertEqual(c["confidence"]["n"], ROWS_PER_SPLIT)
            self.assertEqual(c["gate"]["n"], ROWS_PER_SPLIT)
            self.assertEqual(c["confidence"]["acted"], c["confidence"]["correct"] + c["confidence"]["incorrect"])
            self.assertEqual(c["gate"]["acted"], c["gate"]["correct"] + c["gate"]["incorrect"])
            self.assertEqual(c["gate_minus_confidence_risk"] is None, not c["comparable"])

    def test_deterministic_bytes(self):
        a = json.dumps(experiment(), sort_keys=True, allow_nan=False)
        b = json.dumps(experiment(), sort_keys=True, allow_nan=False)
        self.assertEqual(a, b)

    def test_summary_rejects_unmatched_risk_delta(self):
        bad = [{"regime": "original", "comparable": False, "gate_minus_confidence_risk": 0.1}]
        with self.assertRaises(ValueError):
            summarize(bad)

    def test_summary_rejects_missing_comparable_risk_delta(self):
        bad = [{"regime": "original", "comparable": True, "gate_minus_confidence_risk": None}]
        with self.assertRaises(ValueError):
            summarize(bad)

    def test_thresholds_ignore_held_out_labels(self):
        cal = fixture(1103)
        test = fixture(2103)
        flipped = [replace(r, y=1-r.y) for r in test]
        for regime in REGIMES:
            a = run(transform(cal, regime, 10103), transform(test, regime, 11103))
            b = run(transform(cal, regime, 10103), transform(flipped, regime, 11103))
            for x, y in zip(a["results"], b["results"]):
                for policy in ("confidence", "gate"):
                    self.assertEqual(x["policies"][policy]["selection"],
                                     y["policies"][policy]["selection"])


if __name__ == "__main__":
    unittest.main()
