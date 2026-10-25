"""Adversarial structural checks; reviewer annotations here are invented TEST FIXTURES."""
import copy
import json
import unittest
from pathlib import Path
from blind_review_preflight import digest, validate_packet, validate_submission

ROOT = Path(__file__).resolve().parent
CASE_BYTES = (ROOT / "blind_case_20261024.json").read_bytes()
ARCHIVE_BYTES = (ROOT / "blind_archive_20261024.json").read_bytes()
CASE = json.loads(CASE_BYTES)
ARCHIVE = json.loads(ARCHIVE_BYTES)


def fake_submission():
    return {"synthetic": True, "case_sha256": digest(CASE_BYTES), "archive_sha256": digest(ARCHIVE_BYTES),
            "reviewer_code": "R01", "method": "manual_structured_notes", "review_seconds": 1,
            "correction_seconds": 0, "objects": [{"kind": "decisions", "record_id": "D1", "source": ["b07"], "supersedes": "H-12"}]}

class BlindReviewTests(unittest.TestCase):
    def test_packet_is_fictional_and_well_formed(self):
        self.assertEqual(validate_packet(CASE, ARCHIVE), [])
    def test_valid_invented_test_submission(self):
        self.assertEqual(validate_submission(CASE, ARCHIVE, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)), [])
    def test_missing_fictional_flag(self):
        c = copy.deepcopy(CASE); c["synthetic"] = False
        self.assertIn("case:not_explicitly_fictional", validate_packet(c, ARCHIVE))
    def test_duplicate_utterance(self):
        c = copy.deepcopy(CASE); c["meeting"]["utterances"].append(c["meeting"]["utterances"][0])
        self.assertIn("case:invalid_or_duplicate_utterance_id", validate_packet(c, ARCHIVE))
    def test_duplicate_archive(self):
        a = copy.deepcopy(ARCHIVE); a["records"].append(a["records"][0])
        self.assertIn("archive:invalid_or_duplicate_record_ref", validate_packet(CASE, a))
    def test_archive_blank_text(self):
        a = copy.deepcopy(ARCHIVE); a["records"][0]["text"] = ""
        self.assertIn("archive:empty_record_text", validate_packet(CASE, a))
    def test_hash_pin(self):
        s = fake_submission(); s["case_sha256"] = "0"*64
        self.assertIn("submission:source_hash_mismatch", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_pii_reviewer_name(self):
        s = fake_submission(); s["reviewer_code"] = "Alice Smith"
        self.assertIn("submission:invalid_pseudonym", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_fabricated_unknown_time(self):
        s = fake_submission(); s["review_seconds"] = "TBD"
        self.assertIn("submission:invalid_review_seconds", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_negative_time(self):
        s = fake_submission(); s["correction_seconds"] = -1
        self.assertIn("submission:invalid_correction_seconds", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_nonexistent_source(self):
        s = fake_submission(); s["objects"][0]["source"] = ["b999"]
        self.assertIn("object[0]:invalid_source", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_duplicate_source(self):
        s = fake_submission(); s["objects"][0]["source"] = ["b07", "b07"]
        self.assertIn("object[0]:invalid_source", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_unresolved_predecessor(self):
        s = fake_submission(); s["objects"][0]["supersedes"] = "H-999"
        self.assertIn("object[0]:unresolved_archived_predecessor", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_duplicate_record_id(self):
        s = fake_submission(); s["objects"].append(copy.deepcopy(s["objects"][0]))
        self.assertIn("object[1]:invalid_or_duplicate_record_id", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_missing_meeting_fails_closed(self):
        c = copy.deepcopy(CASE); c["meeting"] = None
        self.assertIn("case:missing_meeting", validate_packet(c, ARCHIVE))
    def test_bad_kind_list_fails_closed(self):
        s = fake_submission(); s["objects"][0]["kind"] = ["decisions"]
        self.assertIn("object[0]:unknown_kind", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_bool_time_rejected(self):
        s = fake_submission(); s["review_seconds"] = True
        self.assertIn("submission:invalid_review_seconds", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_no_wrong_method(self):
        s = fake_submission(); s["method"] = "production"
        self.assertIn("submission:invalid_method", validate_submission(CASE, ARCHIVE, s, digest(CASE_BYTES), digest(ARCHIVE_BYTES)))


    # Malformed reviewer packet inputs must be rejected, not crash the validator.
    # All records below are fictional negative controls, not human annotations.
    def test_submission_rejects_missing_meeting_without_exception(self):
        c = copy.deepcopy(CASE); c["meeting"] = None
        self.assertIn("case:missing_meeting", validate_submission(c, ARCHIVE, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_missing_archive_records_without_exception(self):
        a = copy.deepcopy(ARCHIVE); a["records"] = None
        self.assertIn("archive:missing_records", validate_submission(CASE, a, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_nonobject_case_without_exception(self):
        self.assertIn("case:not_explicitly_fictional", validate_submission([], ARCHIVE, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_nonobject_archive_without_exception(self):
        self.assertIn("archive:not_explicitly_fictional", validate_submission(CASE, [], fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_unhashable_utterance_id_without_exception(self):
        c = copy.deepcopy(CASE); c["meeting"]["utterances"][0]["id"] = ["b01"]
        self.assertIn("case:invalid_or_duplicate_utterance_id", validate_submission(c, ARCHIVE, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_unhashable_archive_decision_id_without_exception(self):
        a = copy.deepcopy(ARCHIVE); a["records"][0]["decision_id"] = {"id": "H-11"}
        self.assertIn("archive:invalid_or_duplicate_decision_id", validate_submission(CASE, a, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_nonlist_utterances_without_exception(self):
        c = copy.deepcopy(CASE); c["meeting"]["utterances"] = None
        self.assertIn("case:missing_utterances", validate_submission(c, ARCHIVE, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))
    def test_submission_rejects_nonlist_archive_records_without_exception(self):
        a = copy.deepcopy(ARCHIVE); a["records"] = {"H-11": "bad"}
        self.assertIn("archive:missing_records", validate_submission(CASE, a, fake_submission(), digest(CASE_BYTES), digest(ARCHIVE_BYTES)))


# CLI/file-parser integrity controls. All inputs are synthetic negative fixtures;
# no reviewer submissions or real human timings are created.
import io
import tempfile
from contextlib import redirect_stdout
from blind_review_preflight import main


class BlindReviewFileIntegrityTests(unittest.TestCase):
    def invoke(self, case_raw=None, archive_raw=None, submission_raw=None, mode="manifest"):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            case_file, archive_file = folder / "case.json", folder / "archive.json"
            case_file.write_bytes(CASE_BYTES if case_raw is None else case_raw)
            archive_file.write_bytes(ARCHIVE_BYTES if archive_raw is None else archive_raw)
            args = [mode, str(case_file), str(archive_file)]
            if mode == "check":
                submission_file = folder / "private_test_only.json"
                submission_file.write_bytes(
                    json.dumps(fake_submission()).encode("utf-8")
                    if submission_raw is None else submission_raw
                )
                args.append(str(submission_file))
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(args)
            return code, json.loads(output.getvalue())

    def test_manifest_rejects_null_meeting_without_exception(self):
        case = copy.deepcopy(CASE)
        case["meeting"] = None
        code, report = self.invoke(case_raw=json.dumps(case).encode("utf-8"))
        self.assertEqual(code, 1)
        self.assertIn("case:missing_meeting", report["errors"])

    def test_manifest_rejects_null_utterances_without_exception(self):
        case = copy.deepcopy(CASE)
        case["meeting"]["utterances"] = None
        code, report = self.invoke(case_raw=json.dumps(case).encode("utf-8"))
        self.assertEqual(code, 1)
        self.assertIn("case:missing_utterances", report["errors"])

    def test_manifest_rejects_null_archive_records_without_exception(self):
        archive = copy.deepcopy(ARCHIVE)
        archive["records"] = None
        code, report = self.invoke(archive_raw=json.dumps(archive).encode("utf-8"))
        self.assertEqual(code, 1)
        self.assertIn("archive:missing_records", report["errors"])

    def test_manifest_rejects_nonobject_case_without_exception(self):
        code, report = self.invoke(case_raw=b'[]')
        self.assertEqual(code, 1)
        self.assertIn("case:not_explicitly_fictional", report["errors"])

    def test_duplicate_json_key_cannot_override_fictional_flag(self):
        raw = CASE_BYTES.replace(b'"synthetic": true', b'"synthetic": false, "synthetic": true', 1)
        self.assertNotEqual(raw, CASE_BYTES)
        code, report = self.invoke(case_raw=raw)
        self.assertEqual(code, 1)
        self.assertIn("input:invalid_json_or_read", report["errors"])

    def test_duplicate_json_key_cannot_override_review_seconds(self):
        raw = json.dumps(fake_submission()).replace(
            '"review_seconds": 1', '"review_seconds": -99, "review_seconds": 1'
        ).encode("utf-8")
        code, report = self.invoke(submission_raw=raw, mode="check")
        self.assertEqual(code, 1)
        self.assertIn("input:invalid_json_or_read", report["errors"])

    def test_nonfinite_unused_submission_field_is_rejected(self):
        raw = json.dumps(fake_submission())[:-1] + ', "extra": NaN}'
        code, report = self.invoke(submission_raw=raw.encode("utf-8"), mode="check")
        self.assertEqual(code, 1)
        self.assertIn("input:invalid_json_or_read", report["errors"])

    def test_overflowing_unused_submission_number_is_rejected(self):
        raw = json.dumps(fake_submission())[:-1] + ', "extra": 1e400}'
        code, report = self.invoke(submission_raw=raw.encode("utf-8"), mode="check")
        self.assertEqual(code, 1)
        self.assertIn("input:invalid_json_or_read", report["errors"])

    def test_malformed_json_reports_error_without_traceback(self):
        code, report = self.invoke(archive_raw=b'{')
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"], ["input:invalid_json_or_read"])


if __name__ == "__main__": unittest.main()
