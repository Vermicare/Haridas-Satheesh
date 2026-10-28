"""Fictional-only red/green tests for the additive v0.3 pair gate.

No human participants, employer content, or private submissions.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reviewer_pair_preflight_v01 import compare_pair
from reviewer_pair_semantic_gate_v03 import compare_semantic_pair, check_files
from semantic_annotation_contract_v02 import VERSION

CASE = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
        "meeting": {"utterances": [{"id": "b01", "text": "Fictional decision."}]}}
ARCHIVE = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
           "records": [{"record_ref": "ARC-1", "decision_id": "H-1",
                        "text": "Fictional historical record."}]}


def submission(code, semantic=True):
    obj = {"kind": "decisions", "record_id": "D-1", "source": ["b01"],
           "supersedes": "H-1", "archive_sources": ["ARC-1"]}
    if semantic:
        obj.update(statement="Fictional decision supersedes H-1", status="active")
    return {"synthetic": True, "case_sha256": "case-sha",
            "archive_sha256": "archive-sha", "reviewer_code": code,
            "method": "manual_structured_notes", "review_seconds": 30,
            "correction_seconds": 0, "annotation_schema_version": VERSION,
            "objects": [obj]}


class PairSemanticGateTests(unittest.TestCase):
    def run_pair(self, a=None, b=None):
        a = submission("R01") if a is None else a
        b = submission("R02") if b is None else b
        with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", "case-sha"), \
             patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", "archive-sha"):
            return compare_semantic_pair(CASE, ARCHIVE, a, b, "case-sha", "archive-sha")

    def test_red_control_v01_accepts_source_only_pair_but_v03_denies(self):
        a, b = submission("R01", False), submission("R02", False)
        with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", "case-sha"), \
             patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", "archive-sha"):
            self.assertTrue(compare_pair(CASE, ARCHIVE, a, b, "case-sha", "archive-sha")["pair_valid"])
        result = self.run_pair(a, b)
        self.assertFalse(result["pair_ready"])
        self.assertIn("reviewer[0]:semantic_shape_invalid", result["errors"])
        self.assertIn("reviewer[1]:semantic_shape_invalid", result["errors"])

    def test_complete_fictional_pair_structurally_ready_only(self):
        result = self.run_pair()
        self.assertTrue(result["pair_ready"])
        self.assertEqual(result["kind_counts"]["decisions"]["shared_source_signature_count"], 1)
        self.assertEqual(result["semantic_agreement"], "TBD")
        self.assertEqual(result["human_independence"], "TBD")
        self.assertFalse(result["source_signature_overlap_is_semantic_agreement"])

    def test_missing_semantics_on_second_reviewer_fails(self):
        b = submission("R02")
        b["objects"][0].pop("statement")
        self.assertEqual(self.run_pair(b=b)["errors"],
                         ["reviewer[1]:semantic_shape_invalid"])

    def test_missing_schema_on_first_reviewer_fails(self):
        a = submission("R01")
        a.pop("annotation_schema_version")
        self.assertIn("reviewer[0]:semantic_shape_invalid", self.run_pair(a=a)["errors"])

    def test_unknown_semantic_field_fails(self):
        b = submission("R02")
        b["objects"][0]["hallucinated_field"] = "fake"
        self.assertFalse(self.run_pair(b=b)["pair_ready"])

    def test_invalid_status_fails(self):
        b = submission("R02")
        b["objects"][0]["status"] = "closed"
        self.assertFalse(self.run_pair(b=b)["pair_ready"])

    def test_duplicate_reviewer_code_still_fails(self):
        self.assertIn("pair:duplicate_pseudonym",
                      self.run_pair(b=submission("R01"))["errors"])

    def test_missing_archive_citation_still_fails(self):
        b = submission("R02")
        b["objects"][0].pop("archive_sources")
        self.assertIn("reviewer[1]:invalid_submission", self.run_pair(b=b)["errors"])

    def test_wrong_source_hash_still_fails(self):
        b = submission("R02")
        b["case_sha256"] = "tampered"
        self.assertFalse(self.run_pair(b=b)["pair_ready"])

    def test_empty_annotation_lists_are_not_forced_to_fabricate(self):
        a, b = submission("R01"), submission("R02")
        a["objects"], b["objects"] = [], []
        result = self.run_pair(a, b)
        self.assertTrue(result["pair_ready"])
        self.assertEqual(result["kind_counts"]["decisions"]["first_count"], 0)
        self.assertEqual(result["adjudicated_gold"], "TBD")

    def test_wrong_method_fails(self):
        b = submission("R02")
        b["method"] = "extractor_correction"
        self.assertFalse(self.run_pair(b=b)["pair_ready"])

    def test_unrecognized_packet_fails(self):
        a, b = submission("R01"), submission("R02")
        result = compare_semantic_pair(CASE, ARCHIVE, a, b, "other", "other")
        self.assertFalse(result["pair_ready"])
        self.assertIn("pair:unrecognized_frozen_packet", result["errors"])

    def test_no_private_values_appear_in_error_codes(self):
        b = submission("R02")
        b["objects"][0]["statement"] = "PRIVATE-DO-NOT-PRINT"
        b["objects"][0]["status"] = "invalid"
        result = self.run_pair(b=b)
        rendered = json.dumps(result)
        self.assertNotIn("PRIVATE-DO-NOT-PRINT", rendered)
        self.assertNotIn("R02", rendered)
        self.assertNotIn("b01", rendered)

    def test_malformed_files_fail_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as td:
            paths = [Path(td) / n for n in ("case.json", "archive.json", "a.json", "b.json")]
            for p in paths:
                p.write_text('{"PRIVATE-DO-NOT-PRINT":', encoding="utf-8")
            code, result = check_files(*(str(p) for p in paths))
            self.assertEqual(code, 1)
            self.assertFalse(result["pair_ready"])
            self.assertEqual(result["errors"], ["input:invalid_or_unreadable"])
            self.assertNotIn("PRIVATE-DO-NOT-PRINT", json.dumps(result))
            self.assertNotIn(td, json.dumps(result))

    def test_oversized_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            paths = [Path(td) / n for n in ("case.json", "archive.json", "a.json", "b.json")]
            for p in paths:
                p.write_text("{}", encoding="utf-8")
            paths[3].write_bytes(b"x" * (1_048_576 + 1))
            code, result = check_files(*(str(p) for p in paths))
            self.assertEqual(code, 1)
            self.assertEqual(result["errors"], ["input:invalid_or_unreadable"])


if __name__ == "__main__":
    unittest.main()
