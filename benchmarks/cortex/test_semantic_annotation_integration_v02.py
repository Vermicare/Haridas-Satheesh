"""End-to-end fictional-only v0.2 intake integration; no actual reviewers."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from semantic_annotation_contract_v02 import VERSION, check_files


def packet():
    case = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
            "meeting": {"utterances": [{"id": "x01", "text": "Entirely fictional example."}]}}
    archive = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
               "records": [{"record_ref": "ARC-1", "decision_id": "H-1",
                            "text": "Fictional historical entry."}]}
    return case, archive


class SemanticAnnotationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paths = [Path(self.temp.name) / name for name in
                      ("case.json", "archive.json", "private.json")]
        case, archive = packet()
        self.paths[0].write_text(json.dumps(case), encoding="utf-8")
        self.paths[1].write_text(json.dumps(archive), encoding="utf-8")
        self.case_sha = hashlib.sha256(self.paths[0].read_bytes()).hexdigest()
        self.archive_sha = hashlib.sha256(self.paths[1].read_bytes()).hexdigest()
        self.submission = {
            "synthetic": True, "case_sha256": self.case_sha,
            "archive_sha256": self.archive_sha,
            "reviewer_code": "R01", "method": "manual_structured_notes",
            "review_seconds": 20, "correction_seconds": 0,
            "annotation_schema_version": VERSION,
            "objects": [{"kind": "decisions", "record_id": "D-1",
                         "source": ["x01"], "statement": "Entirely fictional decision.",
                         "status": None, "supersedes": "H-1",
                         "archive_sources": ["ARC-1"]}]
        }

    def check(self):
        self.paths[2].write_text(json.dumps(self.submission), encoding="utf-8")
        with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", self.case_sha), \
             patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", self.archive_sha):
            return check_files(*(str(p) for p in self.paths))

    def test_fictional_complete_packet_structurally_ready(self):
        code, result = self.check()
        self.assertEqual(code, 0)
        self.assertTrue(result["structurally_ready"])
        self.assertEqual(result["semantic_accuracy"], "TBD")

    def test_v01_structural_pass_but_v02_missing_semantics_fails(self):
        self.submission["objects"][0].pop("statement")
        code, result = self.check()
        self.assertEqual(code, 1)
        self.assertIn("v02:object[0]:missing_semantic_fields", result["errors"])

    def test_missing_archival_evidence_rejected_by_predecessor(self):
        self.submission["objects"][0].pop("archive_sources")
        code, result = self.check()
        self.assertEqual(code, 1)
        self.assertIn("object[0]:missing_matching_predecessor_archive_source", result["errors"])

    def test_unpinned_case_rejected(self):
        self.submission["case_sha256"] = "not-the-case"
        code, result = self.check()
        self.assertEqual(code, 1)
        self.assertIn("submission:source_hash_mismatch", result["errors"])

    def test_malformed_private_json_does_not_echo_text(self):
        self.paths[2].write_text('{"sensitive":"PRIVATE-DO-NOT-PRINT",', encoding="utf-8")
        with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", self.case_sha), \
             patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", self.archive_sha):
            code, result = check_files(*(str(p) for p in self.paths))
        self.assertEqual(code, 1)
        self.assertNotIn("PRIVATE-DO-NOT-PRINT", json.dumps(result))
        self.assertNotIn(self.temp.name, json.dumps(result))

    def test_source_unknown_rejected_by_predecessor(self):
        self.submission["objects"][0]["source"] = ["ghost"]
        code, result = self.check()
        self.assertEqual(code, 1)
        self.assertIn("object[0]:invalid_source", result["errors"])


if __name__ == "__main__":
    unittest.main()
