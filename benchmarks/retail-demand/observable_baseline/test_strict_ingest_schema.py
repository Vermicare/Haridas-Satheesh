"""FICTIONAL ONLY: ingestion must honor the same canonical row contract as export.

These negative controls prevent silently changing row identity/date at the
JSONL boundary. They do not exercise the publisher's real Parquet bytes.
"""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from retail_gate import EvidenceError, parse_row, benchmark
from retail_sqlite import benchmark_sqlite


def fictional_row(i=0):
    return {
        "store_id": 1, "product_id": 2,
        "dt": (dt.date(2024, 1, 1) + dt.timedelta(days=i)).isoformat(),
        "hours_sale": [0.0] * 24,
        "hours_stock_status": [1 if h == 11 and i % 5 == 0 else 0 for h in range(24)],
        "stock_hour6_22_cnt": 1 if i % 5 == 0 else 0,
    }


class StrictIngestSchemaTests(unittest.TestCase):
    def test_valid_canonical_row_preserves_identity(self):
        parsed = parse_row(fictional_row(), 1)
        self.assertEqual(parsed["key"], ("1", "2"))
        self.assertEqual(parsed["day"].isoformat(), "2024-01-01")

    def test_string_store_id_rejected(self):
        row = fictional_row()
        row["store_id"] = "1"
        with self.assertRaises(EvidenceError):
            parse_row(row, 1)

    def test_boolean_store_id_rejected(self):
        row = fictional_row()
        row["store_id"] = True
        with self.assertRaises(EvidenceError):
            parse_row(row, 1)

    def test_negative_store_id_rejected(self):
        row = fictional_row()
        row["store_id"] = -1
        with self.assertRaises(EvidenceError):
            parse_row(row, 1)

    def test_float_product_id_rejected(self):
        row = fictional_row()
        row["product_id"] = 2.0
        with self.assertRaises(EvidenceError):
            parse_row(row, 1)

    def test_timestamp_not_silently_truncated(self):
        row = fictional_row()
        row["dt"] = "2024-01-01T12:00:00"
        with self.assertRaises(EvidenceError):
            parse_row(row, 1)

    def test_date_with_suffix_not_silently_truncated(self):
        row = fictional_row()
        row["dt"] = "2024-01-01garbage"
        with self.assertRaises(EvidenceError):
            parse_row(row, 1)

    def test_both_engines_reject_same_noncanonical_input(self):
        rows = [fictional_row(i) for i in range(84)]
        rows[43]["dt"] += "T23:59:59"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "FICTIONAL.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            for engine in (benchmark, benchmark_sqlite):
                with self.subTest(engine=engine.__name__):
                    with self.assertRaises(EvidenceError):
                        engine(path, synthetic=True)


if __name__ == "__main__":
    unittest.main()
