"""Fictional-only contract tests; do not assert a real parquet file was read."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from parquet_export import ExportError, PINNED_REVISION, export_batches, normalized_row


def fictional_row(day="2024-03-28"):
    sales = [0.0] * 24
    sales[9] = 2.25
    flags = [0] * 24
    flags[12] = 1
    return {"store_id": 2, "product_id": 3, "dt": day, "hours_sale": sales,
            "hours_stock_status": flags, "stock_hour6_22_cnt": 1,
            "irrelevant_private_column": "ignored"}


class ExportContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.source = self.dir / "fictional-not-parquet.bin"
        self.source.write_bytes(b"FICTIONAL BYTES, NOT PARQUET")
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def convert(self, batches, prefix="out", sha=None):
        out = self.dir / (prefix + ".jsonl")
        manifest = self.dir / (prefix + ".manifest.json")
        report = export_batches(batches, out, manifest, source_path=self.source,
                                expected_source_sha256=sha or self.sha,
                                source_revision=PINNED_REVISION, synthetic=True)
        return out, manifest, report

    def test_deterministic_bytes_and_manifest(self):
        first = self.convert([[fictional_row(), fictional_row("2024-03-29")]], "one")
        second = self.convert([[fictional_row()], [fictional_row("2024-03-29")]], "two")
        self.assertEqual(first[0].read_bytes(), second[0].read_bytes())
        self.assertEqual(first[1].read_bytes(), second[1].read_bytes())
        self.assertEqual(first[2]["export_sha256"], hashlib.sha256(first[0].read_bytes()).hexdigest())
        self.assertEqual(first[2]["export_rows"], 2)
        self.assertEqual(first[2]["data_kind"], "FICTIONAL_TEST_ONLY")
        self.assertNotIn("irrelevant_private_column", first[0].read_text())

    def test_hash_mismatch_rejected_before_output(self):
        with self.assertRaisesRegex(ExportError, "SHA256 mismatch"):
            self.convert([[fictional_row()]], sha="0" * 64)
        self.assertFalse((self.dir / "out.jsonl").exists())

    def test_failure_leaves_no_partial_files(self):
        bad = fictional_row("2024-03-29")
        bad["hours_stock_status"][6] = 1
        with self.assertRaisesRegex(ExportError, "stockout count mismatch"):
            self.convert([[fictional_row(), bad]])
        self.assertFalse((self.dir / "out.jsonl").exists())
        self.assertFalse((self.dir / "out.manifest.json").exists())

    def test_source_mutation_during_export_rejected(self):
        def mutate_source():
            yield [fictional_row()]
            self.source.write_bytes(b"CHANGED WHILE EXPORTING")
            yield [fictional_row("2024-03-29")]
        with self.assertRaisesRegex(ExportError, "source changed"):
            self.convert(mutate_source())
        self.assertFalse((self.dir / "out.jsonl").exists())
        self.assertFalse((self.dir / "out.manifest.json").exists())

    def test_empty_export_rejected(self):
        with self.assertRaisesRegex(ExportError, "empty export"):
            self.convert([])

    def test_existing_output_never_overwritten(self):
        out, manifest, _ = self.convert([[fictional_row()]])
        before = (out.read_bytes(), manifest.read_bytes())
        with self.assertRaisesRegex(ExportError, "refusing to overwrite"):
            self.convert([[fictional_row()]])
        self.assertEqual(before, (out.read_bytes(), manifest.read_bytes()))

    def test_date_suffix_and_impossible_date_rejected(self):
        for date in ("2024-03-28T09:00:00", "2024-02-30", "2024-3-28"):
            with self.subTest(date=date):
                with self.assertRaisesRegex(ExportError, "date"):
                    normalized_row(fictional_row(date), 1)

    def test_boolean_and_nan_sale_rejected(self):
        for value in (True, float("nan"), float("inf"), -1.0):
            with self.subTest(value=str(value)):
                row = fictional_row()
                row["hours_sale"][1] = value
                with self.assertRaisesRegex(ExportError, "sales"):
                    normalized_row(row, 1)

    def test_invalid_flags_and_short_arrays_rejected(self):
        for flag in (True, 2, "1"):
            with self.subTest(flag=str(flag)):
                row = fictional_row()
                row["hours_stock_status"][1] = flag
                with self.assertRaisesRegex(ExportError, "stock flag"):
                    normalized_row(row, 1)
        row = fictional_row()
        row["hours_sale"] = row["hours_sale"][:23]
        with self.assertRaisesRegex(ExportError, "24"):
            normalized_row(row, 1)

    def test_missing_required_fields_rejected(self):
        row = fictional_row()
        del row["store_id"]
        with self.assertRaisesRegex(ExportError, "missing"):
            normalized_row(row, 1)

    def test_revision_and_source_hash_format_gated(self):
        with self.assertRaisesRegex(ExportError, "revision"):
            export_batches([[fictional_row()]], self.dir/"x", self.dir/"y", source_path=self.source,
                           expected_source_sha256=self.sha, source_revision="main", synthetic=True)
        with self.assertRaisesRegex(ExportError, "64 hex"):
            export_batches([[fictional_row()]], self.dir/"x", self.dir/"y", source_path=self.source,
                           expected_source_sha256="bad", source_revision=PINNED_REVISION, synthetic=True)


if __name__ == "__main__":
    unittest.main()
