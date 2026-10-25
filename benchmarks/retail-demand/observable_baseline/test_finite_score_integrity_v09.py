"""FICTIONAL ONLY: regression controls for finite forecast scores and medians.

No publisher Parquet, real retail observations, or commercial uplift are tested.
"""
import datetime as dt
import json
import math
import tempfile
import unittest
from pathlib import Path

from retail_gate import benchmark, corrected_training_history, mae
from retail_sqlite import benchmark_sqlite


class FiniteScoreIntegrityTests(unittest.TestCase):
    def test_large_finite_mae_does_not_overflow_during_sum(self):
        result = mae([(1e308, 0.0)] * 7)
        self.assertTrue(math.isfinite(result))
        self.assertEqual(result, 1e308)

    def test_large_finite_same_weekday_median_does_not_overflow(self):
        start = dt.date(2024, 1, 1)
        rows = [
            {"day": start + dt.timedelta(days=i),
             "y": 1e308, "censored": i == 14}
            for i in range(15)
        ]
        corrected = corrected_training_history(rows, 15)
        self.assertTrue(math.isfinite(corrected[14]))
        self.assertEqual(corrected[14], 1e308)

    def test_small_score_unchanged(self):
        self.assertEqual(mae([(1.0, 2.0), (3.0, 5.0)]), 1.5)
        self.assertIsNone(mae([]))

    def test_extreme_but_finite_fixture_produces_strict_json_both_engines(self):
        start = dt.date(2024, 1, 1)
        records = []
        for i in range(84):
            sales = [0.0] * 24
            if 42 <= i < 49:
                sales[6] = 1e308
            status = [0] * 24
            if i == 0:
                status[6] = 1
            records.append({
                "store_id": 1, "product_id": 2,
                "dt": (start + dt.timedelta(days=i)).isoformat(),
                "hours_sale": sales, "hours_stock_status": status,
                "stock_hour6_22_cnt": sum(status[6:22])
            })
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "FICTIONAL.jsonl"
            path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
                            encoding="utf-8")
            for engine in (benchmark, benchmark_sqlite):
                with self.subTest(engine=engine.__name__):
                    report = engine(path, synthetic=True)
                    self.assertEqual(len(report["folds"]), 3)
                    # json.dumps default silently serializes Infinity: reject that.
                    json.dumps(report, allow_nan=False)
                    first = report["folds"][0]["models"]["seasonal_naive"]["mae_uncensored_only"]
                    self.assertTrue(math.isfinite(first))
                    self.assertEqual(first, 1e308)


if __name__ == "__main__":
    unittest.main()
