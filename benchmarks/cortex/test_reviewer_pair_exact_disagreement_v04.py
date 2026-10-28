"""Fictional-only exact-disagreement triage; no human reviewer data."""
import copy
import json
import unittest
from unittest.mock import patch

from reviewer_pair_exact_disagreement_v04 import compare_exact_disagreement
from test_reviewer_pair_semantic_gate_v03 import CASE, ARCHIVE, submission


class ExactDisagreementTests(unittest.TestCase):
    def pair(self, first=None, second=None):
        a = submission("R01") if first is None else first
        b = submission("R02") if second is None else second
        with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", "case-sha"), \
             patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", "archive-sha"):
            return compare_exact_disagreement(CASE, ARCHIVE, a, b, "case-sha", "archive-sha")

    def test_same_sources_different_statement_is_flagged_not_semantic_scored(self):
        b = submission("R02")
        b["objects"][0]["statement"] = "A different fictional interpretation"
        r = self.pair(second=b)
        self.assertTrue(r["pair_ready"])
        self.assertTrue(r["exact_disagreement_detected"])
        self.assertEqual(r["field_mismatch_counts"]["statement"], 1)
        self.assertEqual(r["semantic_agreement"], "TBD")

    def test_exact_match_still_requires_independent_adjudication(self):
        r = self.pair()
        self.assertTrue(r["pair_ready"])
        self.assertEqual(r["exact_field_match_groups"], 1)
        self.assertFalse(r["exact_disagreement_detected"])
        self.assertFalse(r["exact_match_is_semantic_agreement"])
        self.assertTrue(r["independent_adjudication_still_required"])

    def test_missing_source_group_not_falsely_paired(self):
        b = submission("R02")
        b["objects"] = []
        r = self.pair(second=b)
        self.assertEqual(r["matched_unique_source_groups"], 0)
        self.assertEqual(r["unmatched_source_groups"], 1)
        self.assertTrue(r["exact_disagreement_detected"])

    def test_both_empty_is_valid_without_inventing_records(self):
        a, b = submission("R01"), submission("R02")
        a["objects"] = []
        b["objects"] = []
        r = self.pair(a, b)
        self.assertTrue(r["pair_ready"])
        self.assertEqual(r["matched_unique_source_groups"], 0)
        self.assertFalse(r["exact_disagreement_detected"])
        self.assertEqual(r["semantic_agreement"], "TBD")

    def test_archive_source_order_is_set_equivalent(self):
        a, b = submission("R01"), submission("R02")
        self.assertEqual(self.pair(a, b)["field_mismatch_counts"]["archive_sources"], 0)

    def test_duplicate_source_signatures_are_ambiguous_not_greedily_matched(self):
        a, b = submission("R01"), submission("R02")
        a["objects"].append({**copy.deepcopy(a["objects"][0]), "record_id": "D-2"})
        r = self.pair(a, b)
        self.assertTrue(r["pair_ready"])
        self.assertEqual(r["ambiguous_duplicate_source_groups"], 1)
        self.assertEqual(r["matched_unique_source_groups"], 0)
        self.assertTrue(r["exact_disagreement_detected"])

    def test_different_supersedes_key_is_unmatched_not_same_decision(self):
        b = submission("R02")
        b["objects"][0]["supersedes"] = "NOT-IN-ARCHIVE"
        r = self.pair(second=b)
        self.assertFalse(r["pair_ready"])
        self.assertEqual(r["exact_disagreement_detected"], "TBD")

    def test_different_status_is_counted(self):
        b = submission("R02")
        b["objects"][0]["status"] = "superseded"
        r = self.pair(second=b)
        self.assertTrue(r["pair_ready"])
        self.assertEqual(r["field_mismatch_counts"]["status"], 1)

    def test_missing_semantic_field_fails_before_comparison(self):
        b = submission("R02")
        del b["objects"][0]["statement"]
        r = self.pair(second=b)
        self.assertFalse(r["pair_ready"])
        self.assertEqual(r["exact_disagreement_detected"], "TBD")
        self.assertNotIn("field_mismatch_counts", r)

    def test_invalid_source_hash_fails_closed(self):
        b = submission("R02")
        b["case_sha256"] = "different"
        self.assertFalse(self.pair(second=b)["pair_ready"])

    def test_private_text_never_leaks(self):
        b = submission("R02")
        b["objects"][0]["statement"] = "PRIVATE-DO-NOT-PRINT"
        result = self.pair(second=b)
        rendered = json.dumps(result)
        for secret in ("PRIVATE-DO-NOT-PRINT", "D-1", "H-1", "R02", "b01"):
            self.assertNotIn(secret, rendered)

    def test_does_not_mutate_input_submissions(self):
        a, b = submission("R01"), submission("R02")
        before = copy.deepcopy((a, b))
        self.pair(a, b)
        self.assertEqual((a, b), before)


if __name__ == "__main__":
    unittest.main()
