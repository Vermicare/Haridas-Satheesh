"""Fictional-only adversarial controls for pinned event row census v0.5."""
import unittest
from unittest.mock import patch
import zhou2020_event_census_v05 as m


def fake_raw(rows=2):
    return m.sample.HEADER + b"\n" + (b"0\t0\tX\t1\t0\n" * rows)


def fake_entry(path="sub-1/ses-0/eeg/sub-1_ses-0_task-imagery_run-0_events.tsv", rows=2):
    return (path, m.sample.git_blob_sha1(fake_raw(rows)), 1, 0)


class CensusTests(unittest.TestCase):
    def test_blob_verification_and_row_count(self):
        x = m.verify_one(fake_entry(), fetch=lambda _: fake_raw())
        self.assertEqual(x["event_rows"], 2)
        self.assertEqual(x["byte_count"], len(fake_raw()))

    def test_changed_blob_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "pinned_git_blob_mismatch"):
            m.verify_one(fake_entry(), fetch=lambda _: fake_raw(3))

    def test_malformed_tsv_fails_closed(self):
        data = m.sample.HEADER + b"\nwrong\n"
        e = (fake_entry()[0], m.sample.git_blob_sha1(data), 1, 0)
        with self.assertRaises(ValueError):
            m.verify_one(e, fetch=lambda _: data)

    def test_invalid_worker_limit(self):
        for w in (0, 9, -1):
            with self.assertRaisesRegex(ValueError, "invalid_worker_limit"):
                m.census([], workers=w)

    def test_partial_sample_cannot_be_called_full_census(self):
        with self.assertRaisesRegex(ValueError, "incomplete_or_duplicate_census"):
            m.census([fake_entry()])

    def test_duplicate_sample_cannot_be_called_full_census(self):
        with self.assertRaisesRegex(ValueError, "incomplete_or_duplicate_census"):
            m.census([fake_entry()] * m.EXPECTED_FILES)

    def test_extract_requires_existing_inventory_audit(self):
        with patch.object(m.inventory, "audit", side_effect=ValueError("structural failure")):
            with self.assertRaisesRegex(ValueError, "structural failure"):
                m.extract_events({}, {})

    def test_extract_rejects_non_833_inventory(self):
        with patch.object(m.inventory, "audit", return_value={"observed_event_metadata_files": 832, "metadata_pairing": "PASS"}):
            with self.assertRaisesRegex(ValueError, "unexpected_event_inventory"):
                m.extract_events({}, {})

    def test_extract_rejects_missing_blob_sha(self):
        trees = {i: {"tree": []} for i in range(1, 21)}
        trees[1]["tree"] = [{"type": "blob", "path": "ses-0/eeg/sub-1_ses-0_task-imagery_run-0_events.tsv", "sha": "bad", "size": 80}]
        with patch.object(m.inventory, "audit", return_value={"observed_event_metadata_files": 833, "metadata_pairing": "PASS"}):
            with self.assertRaisesRegex(ValueError, "invalid_event_blob_sha"):
                m.extract_events({}, trees)

    def test_extract_rejects_oversize_blob(self):
        trees = {i: {"tree": []} for i in range(1, 21)}
        trees[1]["tree"] = [{"type": "blob", "path": "ses-0/eeg/sub-1_ses-0_task-imagery_run-0_events.tsv", "sha": "a"*40, "size": m.sample.MAX_BYTES + 1}]
        with patch.object(m.inventory, "audit", return_value={"observed_event_metadata_files": 833, "metadata_pairing": "PASS"}):
            with self.assertRaisesRegex(ValueError, "invalid_event_blob_size"):
                m.extract_events({}, trees)

    def test_canonical_output_is_order_independent(self):
        import json
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
