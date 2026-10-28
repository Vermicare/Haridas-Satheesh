"""Synthetic-only adversarial tests: a perfect matched-only score can hide omissions."""
import copy
import json
from pathlib import Path
import unittest

from baseline import baseline
from evaluator import evaluate
from source_span_gold_coverage_v02 import audit_gold_coverage, demo


FIXTURE = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))


class GoldDenominatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = copy.deepcopy(FIXTURE)
        self.candidate = baseline(self.fixture)

    def test_original_all_seven_exact(self):
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual((r["gold_records"], r["exact_citation_records"]), (7, 7))
        self.assertEqual(r["gold_denominator_exact_ratio"], 1.0)
        self.assertTrue(r["complete_clean_gate"])

    def test_omitted_decision_keeps_legacy_and_matched_only_perfect(self):
        self.candidate["decisions"].pop()
        self.assertEqual(evaluate(self.fixture, self.candidate)["metrics"]["source_span_traceability"], 1.0)
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(r["matched_only_exact_ratio"], 1.0)
        self.assertEqual(r["omitted_gold_records"], 1)
        self.assertEqual(r["gold_denominator_exact_ratio"], 0.857143)
        self.assertFalse(r["complete_clean_gate"])

    def test_omitted_entire_category(self):
        self.candidate["decisions"] = []
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(r["omitted_gold_records"], 2)
        self.assertEqual(r["gold_denominator_exact_ratio"], 0.714286)
        self.assertFalse(r["complete_clean_gate"])

    def test_duplicate_candidate_not_silently_clean(self):
        self.candidate["decisions"].append(copy.deepcopy(self.candidate["decisions"][0]))
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(r["gold_denominator_exact_ratio"], 1.0)
        self.assertEqual(r["unsupported_or_duplicate_candidates"], 1)
        self.assertFalse(r["complete_clean_gate"])

    def test_missing_one_citation_not_complete(self):
        self.candidate["decisions"][1]["source"] = ["u06"]
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(r["gold_denominator_exact_ratio"], 0.857143)
        self.assertEqual(r["omitted_gold_records"], 0)
        self.assertFalse(r["complete_clean_gate"])

    def test_unsupported_candidate_fails_gate(self):
        self.candidate["decisions"].append({
            "statement": "Entirely fictional unsupported claim", "status": "active", "source": ["u01"]
        })
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(r["unsupported_or_duplicate_candidates"], 1)
        self.assertFalse(r["complete_clean_gate"])

    def test_empty_candidate_zero_coverage(self):
        self.candidate = {kind: [] for kind in self.candidate}
        r = audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(r["gold_denominator_exact_ratio"], 0.0)
        self.assertEqual(r["omitted_gold_records"], 7)
        self.assertFalse(r["complete_clean_gate"])

    def test_duplicate_gold_signature_fails_closed(self):
        self.fixture["ground_truth"]["decisions"].append(copy.deepcopy(self.fixture["ground_truth"]["decisions"][0]))
        with self.assertRaises(ValueError):
            audit_gold_coverage(self.fixture, self.candidate)

    def test_nonsynthetic_fixture_fails_closed(self):
        self.fixture["synthetic"] = False
        with self.assertRaises(ValueError):
            audit_gold_coverage(self.fixture, self.candidate)

    def test_no_input_mutation(self):
        before = json.dumps([self.fixture, self.candidate], sort_keys=True)
        audit_gold_coverage(self.fixture, self.candidate)
        self.assertEqual(before, json.dumps([self.fixture, self.candidate], sort_keys=True))

    def test_demo_deterministic_aggregate_only(self):
        d = demo()
        self.assertEqual(json.dumps(d, sort_keys=True), json.dumps(demo(), sort_keys=True))
        self.assertEqual(d["frozen_traceability_omitted"], 1.0)
        self.assertFalse(d["omitted"]["complete_clean_gate"])
        self.assertFalse(d["duplicate"]["complete_clean_gate"])
        self.assertNotIn("u06", json.dumps(d))
        self.assertNotIn("Asha", json.dumps(d))


if __name__ == "__main__":
    unittest.main()
