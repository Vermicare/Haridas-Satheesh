"""Fictional negative controls for pinned Zhou2020 event-row structural sampler."""
import unittest
from zhou2020_event_row_sample_v04 import (
    HEADER, PINS, audit, count_event_rows, git_blob_sha1, verify_bytes,
)

def fixture(rows=2, newline=b"\n", bom=False):
    head = (b"\xef\xbb\xbf" if bom else b"") + HEADER
    return newline.join([head] + [b"1\t2\tfictional\t3\t4"] * rows) + newline


class EventRowSampleTests(unittest.TestCase):
    def test_lf_with_bom(self):
        self.assertEqual(count_event_rows(fixture(bom=True)), 2)

    def test_crlf(self):
        self.assertEqual(count_event_rows(fixture(newline=b"\r\n")), 2)

    def test_no_final_newline(self):
        self.assertEqual(count_event_rows(fixture()[:-1]), 2)

    def test_bad_header(self):
        with self.assertRaises(ValueError):
            count_event_rows(b"wrong\n1\t2\t3\t4\t5\n")

    def test_blank_middle_row(self):
        with self.assertRaises(ValueError):
            count_event_rows(HEADER + b"\n\n1\t2\t3\t4\t5\n")

    def test_extra_trailing_blank(self):
        with self.assertRaises(ValueError):
            count_event_rows(fixture() + b"\n")

    def test_bad_field_count(self):
        with self.assertRaises(ValueError):
            count_event_rows(HEADER + b"\n1\t2\t3\t4\n")

    def test_nul_rejected(self):
        with self.assertRaises(ValueError):
            count_event_rows(fixture() + b"\0")

    def test_oversize_rejected(self):
        with self.assertRaises(ValueError):
            count_event_rows(b"x" * 131073)

    def test_wrong_git_blob_rejected(self):
        with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
            verify_bytes(fixture(), "0" * 40, 2)

    def test_wrong_expected_rows_rejected(self):
        raw = fixture()
        with self.assertRaisesRegex(ValueError, "event-row count mismatch"):
            verify_bytes(raw, git_blob_sha1(raw), 3)

    def test_pinned_samples_unique(self):
        self.assertEqual(len(PINS), 3)
        self.assertEqual(len({x[0] for x in PINS}), 3)
        self.assertEqual([x[2] for x in PINS], [40, 80, 40])

    def test_audit_fails_closed_on_mock_mismatch(self):
        with self.assertRaises(ValueError):
            audit(lambda path: fixture())

if __name__ == "__main__":
    unittest.main()
