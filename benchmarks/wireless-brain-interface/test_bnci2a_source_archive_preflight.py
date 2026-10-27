"""Synthetic ZIP contract tests only. No public EEG downloaded or processed."""
from __future__ import annotations

import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from bnci2a_source_archive_preflight import EXPECTED, inspect_archive


def fixture(path, *, omit=None, extra=None, override=None):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(EXPECTED - ({omit} if omit else set())):
            archive.writestr(name, (override or {}).get(name, b"GDF 2.20\x00" + name.encode()))
        if extra:
            for name, data in extra:
                archive.writestr(name, data)


class TestSourceArchivePreflight(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "source.zip"
        fixture(self.path)

    def test_valid_source_hashes_and_no_labels(self):
        result = inspect_archive(self.path)
        self.assertEqual(result["gdf_file_count"], 18)
        self.assertEqual(len(result["gdf"]), 18)
        self.assertEqual(len(result["source_archive_sha256"]), 64)
        self.assertFalse(result["evaluation_labels_accessed"])
        self.assertFalse(result["trial_counts_verified"])
        self.assertEqual(result["real_eeg_signal_or_outcome_metrics"], "TBD")
        self.assertNotIn("GDF 2.20", str(result))

    def test_repeat_determinism(self):
        self.assertEqual(inspect_archive(self.path), inspect_archive(self.path))

    def test_missing_session_rejected(self):
        fixture(self.path, omit="A09E.gdf")
        with self.assertRaisesRegex(ValueError, "missing expected"):
            inspect_archive(self.path)

    def test_unexpected_gdf_rejected(self):
        fixture(self.path, extra=[("A10T.gdf", b"GDF 2.20")])
        with self.assertRaisesRegex(ValueError, "unexpected GDF"):
            inspect_archive(self.path)

    def test_hidden_eval_label_file_rejected(self):
        fixture(self.path, extra=[("labels/A01E.mat", b"test labels")])
        with self.assertRaisesRegex(ValueError, "label firewall"):
            inspect_archive(self.path)

    def test_traversal_rejected(self):
        fixture(self.path, extra=[("../A01E.mat", b"test labels")])
        with self.assertRaisesRegex(ValueError, "traversal"):
            inspect_archive(self.path)

    def test_duplicate_gdf_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            fixture(self.path, extra=[("A01T.gdf", b"GDF 2.20")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            inspect_archive(self.path)

    def test_case_variant_duplicate_rejected(self):
        fixture(self.path, extra=[("a01t.gdf", b"GDF 2.20")])
        with self.assertRaisesRegex(ValueError, "duplicate|unexpected"):
            inspect_archive(self.path)

    def test_bad_gdf_magic_rejected(self):
        fixture(self.path, override={"A01T.gdf": b"not a GDF"})
        with self.assertRaisesRegex(ValueError, "GDF signature"):
            inspect_archive(self.path)

    def test_bad_crc_rejected(self):
        # Use a stored ZIP for deterministic byte corruption.
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_STORED) as archive:
            for name in sorted(EXPECTED):
                archive.writestr(name, b"GDF 2.20" + name.encode())
        raw = bytearray(self.path.read_bytes())
        idx = raw.index(b"GDF 2.20")
        raw[idx] = ord("X")
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "archive integrity failure"):
            inspect_archive(self.path)

    def test_zip_symlink_rejected(self):
        with zipfile.ZipFile(self.path, "a") as archive:
            item = zipfile.ZipInfo("link.txt")
            item.create_system = 3
            item.external_attr = (0o120777 << 16)
            archive.writestr(item, b"target")
        with self.assertRaisesRegex(ValueError, "symlink"):
            inspect_archive(self.path)

    def test_member_size_cap_rejected(self):
        with self.assertRaisesRegex(ValueError, "size limit"):
            inspect_archive(self.path, max_gdf_bytes=4)

    def test_benign_document_allowed(self):
        fixture(self.path, extra=[("README.txt", b"Publisher notes")])
        self.assertEqual(inspect_archive(self.path)["additional_document_members"], ["README.txt"])

    def test_not_zip_rejected(self):
        self.path.write_bytes(b"not zip")
        with self.assertRaisesRegex(ValueError, "archive integrity failure"):
            inspect_archive(self.path)


if __name__ == "__main__":
    unittest.main()
