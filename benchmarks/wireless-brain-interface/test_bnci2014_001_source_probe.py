"""Synthetic byte-stream contract tests; no external network or EEG used."""
import hashlib
import io
import unittest

from bnci2014_001_source_probe import (
    SOURCE_URL, MAX_BYTES, fingerprint_stream, validate_source_url,
)

GRAZ = "https://lampx.tugraz.at/~bci/database/001-2014/A01T.mat"
DATA = b"MATLAB 5.0 MAT-file" + b" " * 110 + b"synthetic-not-EEG"


class SourceProbeTests(unittest.TestCase):
    def test_pinned_source_routes(self):
        for url in (SOURCE_URL, GRAZ):
            validate_source_url(url)

    def test_reject_untrusted_redirect(self):
        for url in (
            "http://lampx.tugraz.at/~bci/database/001-2014/A01T.mat",
            "https://evil.example/001-2014/A01T.mat",
            "https://lampx.tugraz.at/~bci/database/001-2014/A01E.mat",
            "https://lampx.tugraz.at/~bci/database/001-2014/A01T.mat?token=secret",
            "https://user:password@lampx.tugraz.at/~bci/database/001-2014/A01T.mat",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_source_url(url)

    def test_hash_and_boundary(self):
        out = fingerprint_stream(io.BytesIO(DATA), final_url=GRAZ, declared_length=len(DATA))
        self.assertEqual(out["source_sha256"], hashlib.sha256(DATA).hexdigest())
        self.assertEqual(out["source_bytes"], len(DATA))
        self.assertEqual(out["source_format"], "MATLAB_5")
        self.assertFalse(out["raw_eeg_or_labels_saved"])
        self.assertEqual(out["decoding_metrics"], "TBD")
        self.assertNotIn("synthetic-not-EEG", str(out))

    def test_reject_html_instead_of_mat(self):
        with self.assertRaisesRegex(ValueError, "signature"):
            fingerprint_stream(io.BytesIO(b"<html>" + b"x" * 128), final_url=GRAZ)

    def test_reject_truncated_transfer(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            fingerprint_stream(io.BytesIO(DATA), final_url=GRAZ, declared_length=len(DATA) + 1)

    def test_reject_overdeclared_size(self):
        with self.assertRaisesRegex(ValueError, "declared"):
            fingerprint_stream(io.BytesIO(DATA), final_url=GRAZ, declared_length=MAX_BYTES + 1)

    def test_reject_stream_exceeding_limit(self):
        class LargeStream:
            def read(self, n):
                return b"x" * n
        with self.assertRaisesRegex(ValueError, "exceeds"):
            fingerprint_stream(LargeStream(), final_url=GRAZ)

    def test_short_reads_do_not_break_signature_detection(self):
        class TinyChunks(io.BytesIO):
            def read(self, n=-1):
                return super().read(min(n, 3))
        out = fingerprint_stream(TinyChunks(DATA), final_url=GRAZ)
        self.assertEqual(out["source_sha256"], hashlib.sha256(DATA).hexdigest())

    def test_hdf5_signature_is_explicitly_distinct(self):
        data = b"\x89HDF\r\n\x1a\n" + b"x" * 130
        out = fingerprint_stream(io.BytesIO(data), final_url=GRAZ)
        self.assertEqual(out["source_format"], "HDF5_MAT_7_3")

    def test_reject_empty_and_short_headers(self):
        for data in (b"", b"MATLAB 5.0 MAT-file"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                fingerprint_stream(io.BytesIO(data), final_url=GRAZ)


if __name__ == "__main__":
    unittest.main()
