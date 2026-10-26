"""Synthetic-only adversarial tests; no human reviewer results or PII."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reviewer_pair_preflight_v01 import compare_pair, check_files

CASE = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
        "meeting": {"utterances": [{"id": "b01", "text": "Fictional decision."},
                                   {"id": "b02", "text": "Fictional risk."}]}}
ARCHIVE = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
           "records": [{"record_ref": "ARC-1", "decision_id": "H-1", "text": "Fictional archive."}]}


def submission(code, *, objects=None, seconds=30, method="manual_structured_notes"):
    return {"synthetic": True, "case_sha256": "case-sha", "archive_sha256": "archive-sha",
            "reviewer_code": code, "method": method, "review_seconds": seconds,
            "correction_seconds": 0, "objects": objects if objects is not None else [
                {"kind": "decisions", "record_id": "D-1", "source": ["b01"],
                 "supersedes": "H-1", "archive_sources": ["ARC-1"]}]}


class ReviewerPairTests(unittest.TestCase):
    def run_pair(self, a=None, b=None):
        with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", "case-sha"), \
             patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", "archive-sha"):
            return compare_pair(CASE, ARCHIVE, a or submission("R01"), b or submission("R02"),
                                "case-sha", "archive-sha")

    def test_clean_synthetic_pair_aggregate_only(self):
        result = self.run_pair()
        self.assertTrue(result["pair_valid"])
        self.assertEqual(result["kind_counts"]["decisions"],
                         {"first_count": 1, "second_count": 1, "shared_source_signature_count": 1})
        self.assertEqual(result["semantic_agreement"], "TBD")
        self.assertNotIn("R01", json.dumps(result))
        self.assertNotIn("b01", json.dumps(result))
        self.assertNotIn("D-1", json.dumps(result))

    def test_unrecognized_frozen_packet_rejected(self):
        result = compare_pair(CASE, ARCHIVE, submission("R01"), submission("R02"),
                              "case-sha", "archive-sha")
        self.assertIn("pair:unrecognized_frozen_packet", result["errors"])

    def test_duplicate_reviewer_code_rejected(self):
        self.assertIn("pair:duplicate_pseudonym", self.run_pair(b=submission("R01"))["errors"])

    def test_unvalidated_archive_citation_rejected(self):
        b = submission("R02")
        del b["objects"][0]["archive_sources"]
        self.assertIn("reviewer[1]:invalid_submission", self.run_pair(b=b)["errors"])

    def test_dangling_source_rejected(self):
        b = submission("R02")
        b["objects"][0]["source"] = ["ghost"]
        self.assertFalse(self.run_pair(b=b)["pair_valid"])

    def test_mismatched_hash_rejected(self):
        b = submission("R02")
        b["case_sha256"] = "wrong"
        self.assertFalse(self.run_pair(b=b)["pair_valid"])

    def test_zero_time_rejected(self):
        self.assertIn("reviewer[1]:invalid_review_time",
                      self.run_pair(b=submission("R02", seconds=0))["errors"])

    def test_infinite_time_rejected(self):
        self.assertFalse(self.run_pair(b=submission("R02", seconds=float("inf")))["pair_valid"])

    def test_wrong_method_rejected(self):
        self.assertIn("reviewer[1]:requires_manual_notes",
                      self.run_pair(b=submission("R02", method="extractor_correction"))["errors"])

    def test_unexpected_correction_time_rejected(self):
        b = submission("R02")
        b["correction_seconds"] = 9
        self.assertIn("reviewer[1]:unexpected_correction_time", self.run_pair(b=b)["errors"])

    def test_no_semantic_equivalence_inferred(self):
        b = submission("R02")
        b["objects"][0]["source"] = ["b02"]
        result = self.run_pair(b=b)
        self.assertTrue(result["pair_valid"])
        self.assertEqual(result["kind_counts"]["decisions"]["shared_source_signature_count"], 0)
        self.assertEqual(result["semantic_agreement"], "TBD")

    def test_multiset_duplicate_sources_not_collapsed(self):
        a = submission("R01")
        a["objects"].append({"kind": "decisions", "record_id": "D-2", "source": ["b01"]})
        b = submission("R02")
        result = self.run_pair(a=a, b=b)
        self.assertTrue(result["pair_valid"])
        self.assertEqual(result["kind_counts"]["decisions"],
                         {"first_count": 2, "second_count": 1, "shared_source_signature_count": 1})

    def test_invalid_file_reports_no_private_content(self):
        with tempfile.TemporaryDirectory() as td:
            paths = [Path(td) / x for x in ("case.json", "archive.json", "a.json", "b.json")]
            for path in paths:
                path.write_text('{"sensitive": "private-secret", "bad":', encoding="utf-8")
            code, result = check_files(*(str(p) for p in paths))
            self.assertEqual(code, 1)
            self.assertNotIn("private-secret", json.dumps(result))
            self.assertNotIn(td, json.dumps(result))

    def test_oversized_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            paths = [Path(td) / x for x in ("case.json", "archive.json", "a.json", "b.json")]
            for path in paths:
                path.write_text("{}", encoding="utf-8")
            paths[3].write_bytes(b"x" * (1_048_576 + 1))
            code, result = check_files(*(str(p) for p in paths))
            self.assertEqual(code, 1)
            self.assertEqual(result["errors"], ["input:invalid_or_unreadable"])


if __name__ == "__main__":
    unittest.main()
