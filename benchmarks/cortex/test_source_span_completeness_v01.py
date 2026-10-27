"""Synthetic-only CORTEX negative controls; frozen evaluator remains untouched."""
import copy
import json
from pathlib import Path
import unittest

from baseline import baseline
from evaluator import evaluate
from source_span_completeness_v01 import audit_sources, demo

FIXTURE = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))


class SourceSpanCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.fixture = copy.deepcopy(FIXTURE)
        self.candidate = baseline(self.fixture)

    def test_original_seven_objects_exact(self):
        result = audit_sources(self.fixture, self.candidate)
        self.assertEqual(result["matched_objects"], 7)
        self.assertEqual(result["counts"]["exact"], 7)
        self.assertEqual(result["strict_exact_source_ratio"], 1.0)

    def test_missing_required_source_gets_legacy_credit_but_not_strict(self):
        self.candidate["decisions"][1]["source"] = ["u06"]
        self.assertEqual(evaluate(self.fixture, self.candidate)["metrics"]["source_span_traceability"], 1.0)
        result = audit_sources(self.fixture, self.candidate)
        self.assertEqual(result["counts"]["partial"], 1)
        self.assertEqual(result["strict_exact_source_ratio"], 0.857143)
        self.assertEqual(result["legacy_nonempty_subset_credit_ratio"], 1.0)

    def test_extra_source_rejected_by_strict(self):
        self.candidate["decisions"][0]["source"] = ["u01", "u02"]
        self.assertEqual(audit_sources(self.fixture, self.candidate)["counts"]["extra"], 1)

    def test_mixed_sources_rejected(self):
        self.candidate["decisions"][1]["source"] = ["u06", "u02"]
        self.assertEqual(audit_sources(self.fixture, self.candidate)["counts"]["mixed"], 1)

    def test_missing_source_rejected(self):
        self.candidate["decisions"][0]["source"] = []
        self.assertEqual(audit_sources(self.fixture, self.candidate)["counts"]["missing"], 1)

    def test_unknown_source_invalid(self):
        self.candidate["decisions"][0]["source"] = ["not-a-source"]
        self.assertEqual(audit_sources(self.fixture, self.candidate)["counts"]["invalid"], 1)

    def test_duplicate_source_invalid(self):
        self.candidate["decisions"][0]["source"] = ["u01", "u01"]
        self.assertEqual(audit_sources(self.fixture, self.candidate)["counts"]["invalid"], 1)

    def test_duplicate_candidate_not_double_matched(self):
        self.candidate["decisions"].append(copy.deepcopy(self.candidate["decisions"][0]))
        result = audit_sources(self.fixture, self.candidate)
        self.assertEqual(result["matched_objects"], 7)
        self.assertEqual(result["counts"]["unsupported_or_duplicate"], 1)

    def test_duplicate_gold_signature_fails_closed(self):
        self.fixture["ground_truth"]["decisions"].append(copy.deepcopy(self.fixture["ground_truth"]["decisions"][0]))
        with self.assertRaises(ValueError):
            audit_sources(self.fixture, self.candidate)

    def test_nonfictional_fixture_fails_closed(self):
        self.fixture["synthetic"] = False
        with self.assertRaises(ValueError):
            audit_sources(self.fixture, self.candidate)

    def test_no_input_mutation(self):
        before = json.dumps([self.fixture, self.candidate], sort_keys=True)
        audit_sources(self.fixture, self.candidate)
        self.assertEqual(before, json.dumps([self.fixture, self.candidate], sort_keys=True))

    def test_demo_deterministic_and_aggregate_only(self):
        a = json.dumps(demo(), sort_keys=True)
        self.assertEqual(a, json.dumps(demo(), sort_keys=True))
        self.assertNotIn("u06", a)
        self.assertNotIn("u07", a)
        self.assertEqual(demo()["omitted_source"]["counts"]["partial"], 1)


if __name__ == "__main__":
    unittest.main()
