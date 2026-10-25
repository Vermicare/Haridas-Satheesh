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

if __name__ == "__main__": unittest.main()
