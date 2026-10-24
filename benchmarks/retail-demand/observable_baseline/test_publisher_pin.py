"""FICTIONAL negative controls: reject misleading external-source pin declarations.

These tests do not acquire, open, or benchmark the real publisher Parquet file.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

from parquet_export import (
    ExportError, PINNED_REVISION, PUBLISHER_REPORTED_TRAIN_SHA256,
    export_batches,
)


def fictional_row():
    return {
        "store_id": 1, "product_id": 2, "dt": "2024-01-01",
        "hours_sale": [0.0] * 24,
        "hours_stock_status": [0] * 24,
        "stock_hour6_22_cnt": 0,
    }


class PublisherPinTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "FICTIONAL-NOT-PARQUET.bin"
        self.source.write_bytes(b"NOT REAL DATA")
        self.fake_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def export(self, *, revision=PINNED_REVISION, sha=None, synthetic=False):
        return export_batches(
            [[fictional_row()]],
            self.root / "output.jsonl",
            self.root / "output.manifest.json",
            source_path=self.source,
            expected_source_sha256=sha or self.fake_hash,
            source_revision=revision,
            synthetic=synthetic,
        )

    def test_external_rejects_arbitrary_revision_even_with_matching_local_hash(self):
        with self.assertRaisesRegex(ExportError, "publisher-pinned revision"):
            self.export(revision="f" * 40)
        self.assertFalse((self.root / "output.jsonl").exists())

    def test_external_rejects_arbitrary_hash_even_with_correct_revision(self):
        self.assertNotEqual(self.fake_hash, PUBLISHER_REPORTED_TRAIN_SHA256)
        with self.assertRaisesRegex(ExportError, "publisher-reported train SHA256"):
            self.export()
        self.assertFalse((self.root / "output.manifest.json").exists())

    def test_fictional_injection_remains_possible_but_explicitly_labeled(self):
        report = self.export(revision="f" * 40, synthetic=True)
        self.assertEqual(report["data_kind"], "FICTIONAL_TEST_ONLY")
        self.assertFalse(report["source_origin_independently_attested"])
        self.assertEqual(report["local_source_sha256"], self.fake_hash)


if __name__ == "__main__":
    unittest.main()
