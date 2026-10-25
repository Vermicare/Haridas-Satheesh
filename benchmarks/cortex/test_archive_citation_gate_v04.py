"""Fictional-only tests. No human submissions, employer data or reviewers."""
import copy
import unittest
from archive_citation_gate_v04 import validate_archive_citations, demo

ARCHIVE = {"records": [
    {"record_ref": "SYN-ARC-11", "decision_id": "H-11", "text": "Fictional public hold"},
    {"record_ref": "SYN-ARC-12", "decision_id": "H-12", "text": "Fictional checklist"},
]}
SUBMISSION = {"objects": [{"kind": "decisions", "record_id": "D1", "source": ["b07"],
                           "supersedes": "H-12", "archive_sources": ["SYN-ARC-12"]}]}


class ArchiveCitationTests(unittest.TestCase):
    def run_case(self, change=None, archive=None):
        s = copy.deepcopy(SUBMISSION)
        if change:
            change(s["objects"][0])
        return validate_archive_citations(ARCHIVE if archive is None else archive, s)

    def test_fictional_demo_deterministic_and_negative(self):
        import json
        self.assertEqual(demo(), demo())
        report = json.loads(demo())
        self.assertEqual(report["corrected_citation_issues"], [])
        self.assertIn("object[0]:missing_matching_predecessor_archive_source",
                      report["old_missing_citation_issues"])
        self.assertEqual(report["semantic_validity"], "TBD")

    def test_valid_exact_archive_record(self):
        self.assertEqual(self.run_case(), [])

    def test_missing_citation_fails(self):
        issues = self.run_case(lambda o: o.pop("archive_sources"))
        self.assertIn("object[0]:missing_matching_predecessor_archive_source", issues)

    def test_empty_citation_fails(self):
        self.assertIn("object[0]:missing_matching_predecessor_archive_source",
                      self.run_case(lambda o: o.update(archive_sources=[])))

    def test_wrong_valid_archive_citation_fails(self):
        self.assertIn("object[0]:missing_matching_predecessor_archive_source",
                      self.run_case(lambda o: o.update(archive_sources=["SYN-ARC-11"])))

    def test_unknown_archive_record_fails(self):
        issues = self.run_case(lambda o: o.update(archive_sources=["SYN-ARC-999"]))
        self.assertIn("object[0]:unknown_archive_source", issues)
        self.assertIn("object[0]:missing_matching_predecessor_archive_source", issues)

    def test_duplicate_archive_citation_fails(self):
        self.assertIn("object[0]:duplicate_archive_source",
                      self.run_case(lambda o: o.update(archive_sources=["SYN-ARC-12"] * 2)))

    def test_nonlist_citation_fails(self):
        for value in ("SYN-ARC-12", None, {}, True):
            with self.subTest(value=value):
                self.assertIn("object[0]:invalid_archive_sources",
                              self.run_case(lambda o: o.update(archive_sources=value)))

    def test_unhashable_citation_fails_without_exception(self):
        self.assertIn("object[0]:invalid_archive_sources",
                      self.run_case(lambda o: o.update(archive_sources=[{"ref": "SYN-ARC-12"}])))

    def test_blank_citation_fails(self):
        self.assertIn("object[0]:invalid_archive_sources",
                      self.run_case(lambda o: o.update(archive_sources=["  "])))

    def test_valid_predecessor_and_other_context_allowed(self):
        self.assertEqual([], self.run_case(lambda o: o.update(
            archive_sources=["SYN-ARC-11", "SYN-ARC-12"])))

    def test_non_supersession_without_archive_citation_allowed(self):
        self.assertEqual([], self.run_case(lambda o: (o.pop("supersedes"), o.pop("archive_sources"))))

    def test_non_decision_with_known_archive_context_allowed(self):
        self.assertEqual([], self.run_case(lambda o: o.update(kind="risks", archive_sources=["SYN-ARC-11"])))

    def test_malformed_archive_and_submission_fail_closed(self):
        self.assertEqual(["archive_citation:invalid_archive"],
                         validate_archive_citations(None, SUBMISSION))
        self.assertEqual(["archive_citation:invalid_submission"],
                         validate_archive_citations(ARCHIVE, {"objects": {}}))

    def test_duplicate_archive_record_refs_fail_closed(self):
        a = copy.deepcopy(ARCHIVE)
        a["records"].append({"record_ref": "SYN-ARC-12", "decision_id": "H-11"})
        self.assertEqual(["archive_citation:duplicate_archive_record_ref"],
                         validate_archive_citations(a, SUBMISSION))

    def test_nonstring_predecessor_fails_without_exception(self):
        self.assertIn("object[0]:invalid_predecessor",
                      self.run_case(lambda o: o.update(supersedes=["H-12"])))

    def test_multiple_objects_independent_errors(self):
        s = copy.deepcopy(SUBMISSION)
        s["objects"].append({"kind": "decisions", "supersedes": "H-11"})
        self.assertEqual(["object[1]:missing_matching_predecessor_archive_source"],
                         validate_archive_citations(ARCHIVE, s))


# The integration cases run in repository CI against the exact existing
# v0.1 intake and frozen fictional packet. No actual reviewer data is used.
import importlib.util
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec("blind_review_preflight") is not None,
                     "v0.1 intake available in repository CI only")
class FrozenPacketIntegrationTests(unittest.TestCase):
    def setUp(self):
        from blind_review_preflight import digest
        root = Path(__file__).resolve().parent
        self.case_bytes = (root / "blind_case_20261024.json").read_bytes()
        self.archive_bytes = (root / "blind_archive_20261024.json").read_bytes()
        self.case = json.loads(self.case_bytes)
        self.archive = json.loads(self.archive_bytes)
        self.submission = {
            "synthetic": True, "case_sha256": digest(self.case_bytes),
            "archive_sha256": digest(self.archive_bytes),
            "reviewer_code": "R01", "method": "manual_structured_notes",
            "review_seconds": 1, "correction_seconds": 0,
            "objects": [{"kind": "decisions", "record_id": "D1",
                         "source": ["b07"], "supersedes": "H-12"}]
        }

    def test_original_intake_accepts_missing_archive_citation_negative_control(self):
        from blind_review_preflight import validate_submission
        self.assertEqual([], validate_submission(
            self.case, self.archive, self.submission,
            self.submission["case_sha256"], self.submission["archive_sha256"]))
        self.assertIn("object[0]:missing_matching_predecessor_archive_source",
                      validate_archive_citations(self.archive, self.submission))

    def test_correct_archive_record_passes_both_gates(self):
        from blind_review_preflight import validate_submission
        self.submission["objects"][0]["archive_sources"] = ["SYN-ARC-12"]
        self.assertEqual([], validate_submission(
            self.case, self.archive, self.submission,
            self.submission["case_sha256"], self.submission["archive_sha256"]))
        self.assertEqual([], validate_archive_citations(self.archive, self.submission))

    def test_cli_fails_closed_without_echoing_private_submission(self):
        from archive_citation_gate_v04 import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "case.json").write_bytes(self.case_bytes)
            (root / "archive.json").write_bytes(self.archive_bytes)
            (root / "submission.json").write_text(json.dumps(self.submission), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                status = main(["check", str(root / "case.json"), str(root / "archive.json"),
                               str(root / "submission.json")])
            report = json.loads(output.getvalue())
            self.assertEqual(status, 1)
            self.assertIn("object[0]:missing_matching_predecessor_archive_source", report["errors"])
            self.assertNotIn("b07", output.getvalue())
            self.assertNotIn(str(root), output.getvalue())
            self.assertNotIn("R01", output.getvalue())

    def test_cli_valid_submission_passes(self):
        from archive_citation_gate_v04 import main
        self.submission["objects"][0]["archive_sources"] = ["SYN-ARC-12"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "case.json").write_bytes(self.case_bytes)
            (root / "archive.json").write_bytes(self.archive_bytes)
            (root / "submission.json").write_text(json.dumps(self.submission), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                status = main(["check", str(root / "case.json"), str(root / "archive.json"),
                               str(root / "submission.json")])
            self.assertEqual(status, 0)
            self.assertTrue(json.loads(output.getvalue())["submission_valid"])


if __name__ == "__main__":
    unittest.main()
