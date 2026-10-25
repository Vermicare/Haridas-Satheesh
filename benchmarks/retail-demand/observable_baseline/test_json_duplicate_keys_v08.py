"""FICTIONAL ONLY: fail closed on ambiguous JSONL objects.

Python's default json.loads silently uses the last value for duplicate keys.
These tests prevent conflicting evidence from being accepted by either engine.
No publisher Parquet was downloaded or evaluated.
"""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from retail_gate import EvidenceError, benchmark
from retail_sqlite import benchmark_sqlite


def row(i):
    return {
        "store_id": 1,
        "product_id": 2,
        "dt": (dt.date(2024, 1, 1) + dt.timedelta(days=i)).isoformat(),
        "hours_sale": [1.0] * 24,
        "hours_stock_status": [int(i % 5 == 0 and h == 11) for h in range(24)],
        "stock_hour6_22_cnt": int(i % 5 == 0),
    }


class AmbiguousJSONEvidenceTests(unittest.TestCase):
    def run_fixture(self, modify=None, expect_reject=True):
        records = [json.dumps(row(i)) for i in range(84)]
        if modify is not None:
            records[13] = modify(records[13])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "FICTIONAL.jsonl"
            path.write_text("\n".join(records) + "\n", encoding="utf-8")
            for engine in (benchmark, benchmark_sqlite):
                with self.subTest(engine=engine.__name__):
                    if expect_reject:
                        with self.assertRaises(EvidenceError):
                            engine(path, synthetic=True)
                    else:
                        self.assertEqual(len(engine(path, synthetic=True)["folds"]), 3)

    def test_valid_fixture_is_accepted_by_both_engines(self):
        self.run_fixture(expect_reject=False)

    def test_conflicting_duplicate_store_id_is_rejected(self):
        self.run_fixture(lambda s: s.replace('"store_id": 1,',
                                              '"store_id": 999, "store_id": 1,', 1))

    def test_conflicting_duplicate_stock_status_is_rejected(self):
        self.run_fixture(lambda s: s.replace('"hours_stock_status": ',
                                              '"hours_stock_status": [0], "hours_stock_status": ', 1))

    def test_unused_nonfinite_json_constant_is_rejected(self):
        self.run_fixture(lambda s: s[:-1] + ', "unused_metadata": NaN}')


if __name__ == "__main__":
    unittest.main()
