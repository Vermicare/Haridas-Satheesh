"""FICTIONAL negative controls: no nonfinite observed-sales evidence may enter a benchmark.

These tests do not use publisher data or assert forecast improvement.
"""
import datetime as dt
import json
import math
import tempfile
import unittest
from pathlib import Path

from parquet_export import ExportError, normalized_row
from retail_gate import EvidenceError, parse_row, benchmark
from retail_sqlite import benchmark_sqlite


def row(day=0):
    sales = [0.0] * 24
    sales[9] = 2.0
    flags = [0] * 24
    if day % 5 == 0:
        flags[11] = 1
    return {
        "store_id": 1, "product_id": 2,
        "dt": (dt.date(2024, 1, 1) + dt.timedelta(days=day)).isoformat(),
        "hours_sale": sales, "hours_stock_status": flags,
        "stock_hour6_22_cnt": sum(flags[6:22]),
    }


class NumericEvidenceBoundsTests(unittest.TestCase):
    def test_ordinary_large_finite_value_remains_valid(self):
        sample = row()
        sample["hours_sale"][9] = 1e300
        self.assertTrue(math.isfinite(parse_row(sample, 1)["y"]))
        self.assertEqual(normalized_row(sample, 1)["hours_sale"][9], 1e300)

    def test_business_hour_sum_overflow_rejected_at_both_boundaries(self):
        sample = row()
        for hour in range(6, 22):
            sample["hours_sale"][hour] = 1e308
        with self.assertRaises(EvidenceError):
            parse_row(sample, 1)
        with self.assertRaises(ExportError):
            normalized_row(sample, 1)

    def test_extreme_integer_is_validation_error_not_uncaught_overflow(self):
        sample = row()
        sample["hours_sale"][9] = 10 ** 400
        with self.assertRaises(EvidenceError):
            parse_row(sample, 1)
        with self.assertRaises(ExportError):
            normalized_row(sample, 1)

    def test_both_engines_reject_nonfinite_aggregate_in_fictional_jsonl(self):
        rows = [row(i) for i in range(84)]
        for hour in range(6, 22):
            rows[0]["hours_sale"][hour] = 1e308
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "FICTIONAL.jsonl"
            path.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
            for engine in (benchmark, benchmark_sqlite):
                with self.subTest(engine=engine.__name__):
                    with self.assertRaises(EvidenceError):
                        engine(path, synthetic=True)


if __name__ == "__main__":
    unittest.main()
