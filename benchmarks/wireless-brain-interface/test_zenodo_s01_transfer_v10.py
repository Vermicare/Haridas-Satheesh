"""Fictional, network-free adversarial tests; no original EEG bytes."""
import hashlib
import io
import json
import unittest
import zipfile

from zenodo_s01_transfer_v10 import transfer_and_audit


class Response(io.BytesIO):
    def __init__(self, data, headers=None):
        super().__init__(data)
        self.headers = headers or {}


def fictional_zip(member="session_1/run_01.npz", contents=b"fictional, not an NPZ"):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(member, contents)
    return b.getvalue()


class TransferTests(unittest.TestCase):
    def run_case(self, data, **kwargs):
        return transfer_and_audit(
            opener=lambda url, timeout: Response(data, kwargs.pop("headers", {})),
            expected_bytes=kwargs.pop("expected_bytes", len(data)),
            expected_md5=kwargs.pop("expected_md5", hashlib.md5(data).hexdigest()),
            max_bytes=kwargs.pop("max_bytes", 500000),
        )

    def test_fictional_transfer_pass_is_not_eeg_validation(self):
        result = self.run_case(fictional_zip())
        self.assertEqual(result["status"], "PASS_TRANSFER_AND_ZIP_STRUCTURE_ONLY")
        self.assertEqual(result["original_ieee_equivalence"], "TBD")
        self.assertEqual(result["bids_event_mapping"], "TBD")
        self.assertEqual(result["held_out_decoding"], "NOT_PERFORMED")
        self.assertEqual(result["member_count"], 1)
        self.assertNotIn("fictional, not an NPZ", json.dumps(result))

    def test_wrong_publisher_md5_fails(self):
        r = self.run_case(fictional_zip(), expected_md5="0" * 32)
        self.assertEqual(r["failure_code"], "publisher_md5_mismatch")
        self.assertNotIn("zip_preflight_status", r)

    def test_incomplete_transfer_fails(self):
        r = self.run_case(fictional_zip(), expected_bytes=len(fictional_zip()) + 1)
        self.assertEqual(r["failure_code"], "incomplete_transfer")

    def test_header_size_disagreement_fails(self):
        data = fictional_zip()
        r = self.run_case(data, headers={"Content-Length": str(len(data) + 1)})
        self.assertEqual(r["failure_code"], "content_length_disagrees_with_pinned_size")

    def test_oversize_expected_rejected_before_open(self):
        r = self.run_case(fictional_zip(), max_bytes=1)
        self.assertEqual(r["failure_code"], "invalid_expected_size")

    def test_unsafe_zip_member_fails(self):
        r = self.run_case(fictional_zip("../escape.npz"))
        self.assertEqual(r["failure_code"], "zip_preflight_failed")

    def test_nonzip_fails(self):
        r = self.run_case(b"not a zip")
        self.assertEqual(r["failure_code"], "zip_preflight_failed")

    def test_invalid_md5_rejected(self):
        r = self.run_case(fictional_zip(), expected_md5="not-md5")
        self.assertEqual(r["failure_code"], "invalid_expected_md5")

    def test_hash_deterministic_without_timestamps(self):
        data = fictional_zip()
        self.assertEqual(self.run_case(data), self.run_case(data))

    def test_transfer_error_redacts_private_exception(self):
        def fail(url, timeout):
            raise OSError("signed-private-redirect-secret")
        r = transfer_and_audit(opener=fail, expected_bytes=12, expected_md5="0" * 32)
        self.assertEqual(r["failure_code"], "download_error_OSError")
        self.assertNotIn("signed-private", json.dumps(r))


if __name__ == "__main__":
    unittest.main()
