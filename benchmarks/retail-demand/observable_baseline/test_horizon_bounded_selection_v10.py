"""Fictional-only adversarial test: selection must not inspect dates beyond last forecast horizon."""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from retail_gate import EvidenceError, benchmark
from retail_sqlite import benchmark_sqlite

BASE = dt.date(2024, 1, 1)
ENGINES = (benchmark, benchmark_sqlite)


def row(day, store=1, sale=3.0):
    flags = [0] * 24
    if day % 5 == 0:
        flags[11] = 1
    sales = [0.0] * 24
    sales[8] = sale
    return {
        "store_id": store, "product_id": 2,
        "dt": (BASE + dt.timedelta(days=day)).isoformat(),
        "hours_sale": sales, "hours_stock_status": flags,
        "stock_hour6_22_cnt": sum(flags[6:22]),
    }


class HorizonBoundedSelectionTests(unittest.TestCase):
    def run_fixture(self, records):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "FICTIONAL.jsonl"
            p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")
            return [engine(p, synthetic=True) for engine in ENGINES]

    def test_missing_day_after_final_horizon_must_not_invalidate(self):
        # Last declared forecast: origin day 70 + seven days = days 70..76.
        control = self.run_fixture([row(i) for i in range(77)])
        # Day 81 is outside ALL three scoring windows; old code incorrectly rejects.
        extended = self.run_fixture([row(i) for i in range(84) if i != 81])
        for before, after in zip(control, extended):
            self.assertEqual(before["folds"], after["folds"])
            self.assertEqual(before["selected_store_id"], after["selected_store_id"])
        self.assertEqual(extended[0]["folds"], extended[1]["folds"])

    def test_tail_gap_must_not_trigger_future_based_cohort_switch_or_failure(self):
        first = [row(i, store=1) for i in range(84) if i != 81]
        second = [row(i, store=9) for i in range(84)]
        for report in self.run_fixture(first + second):
            self.assertEqual(report["selected_store_id"], "1")

    def test_missing_day_within_last_horizon_must_fail_closed(self):
        # Day 76 IS scored in the final horizon; day 77 must not stand in for it.
        rows = [row(i) for i in range(84) if i != 76]
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "FICTIONAL.jsonl"
            p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
            for engine in ENGINES:
                with self.subTest(engine=engine.__name__):
                    with self.assertRaisesRegex(EvidenceError, "preselected cohort"):
                        engine(p, synthetic=True)

    def test_post_horizon_values_do_not_change_scored_folds(self):
        control = self.run_fixture([row(i) for i in range(77)])
        changed = self.run_fixture([row(i, sale=(1e200 if i >= 77 else 3.0)) for i in range(84)])
        for before, after in zip(control, changed):
            self.assertEqual(before["folds"], after["folds"])


if __name__ == "__main__":
    unittest.main()
