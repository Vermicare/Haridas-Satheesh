"""Fictional-only transfer tests: no publisher data, no claim of actual outcomes."""
import copy
import unittest
from unittest.mock import patch
import freshretail_lt_sales_floor_v25 as v25
import freshretail_lt_stockout_bounds_v24 as v24
import freshretail_lt_score_v21 as v21
from test_freshretail_lt_score_v21 import fictional_eval, predictions


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.keys = ((1, 10), (2, 20))
        self.rows = fictional_eval(self.keys[0]) + fictional_eval(self.keys[1])
        self.pred = predictions(self.keys)
        self.original = v21.score_frozen(self.keys, self.pred, self.rows)

    def score(self, rows=None, old=None):
        rows = self.rows if rows is None else rows
        original = v21.score_frozen(self.keys, self.pred, rows)
        old = v24.score_bounds(self.keys, self.pred, rows, original) if old is None else old
        return v25.score_floor(self.keys, self.pred, rows, old)

    def test_all_observed_floor_equals_original(self):
        r = self.score()
        for name in v24.COMPARATORS:
            self.assertEqual(r[name]["censored_days"], 0)
            self.assertEqual(r[name]["sales_floor_lower"], r[name]["nonnegative_only_lower"])
            self.assertEqual(r[name]["sales_floor_upper"], r[name]["nonnegative_only_upper"])

    def test_censored_sales_floor_nests_original_bounds(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["hours_stock_status"][8] = 1
        rows[0]["stock_hour6_22_cnt"] = 1
        r = self.score(rows)
        for name in v24.COMPARATORS:
            self.assertEqual(r[name]["censored_days"], 1)
            self.assertLessEqual(r[name]["nonnegative_only_lower"] - 1e-10,
                                 r[name]["sales_floor_lower"])
            self.assertLessEqual(r[name]["sales_floor_upper"],
                                 r[name]["nonnegative_only_upper"] + 1e-10)
            self.assertTrue(r[name]["no_censored_latent_demand_imputed"])

    def test_row_order_invariant(self):
        self.assertEqual(self.score(), self.score(list(reversed(self.rows))))

    def test_original_bounds_mismatch_fails(self):
        old = v24.score_bounds(self.keys, self.pred, self.rows, self.original)
        old["last_observed"]["full_period_paired_mae_delta_lower"] -= 0.5
        with self.assertRaisesRegex(v25.TransferError, "original v2.4"):
            self.score(old=old)

    def test_missing_eval_day_fails(self):
        with self.assertRaisesRegex(v21.ScoreError, "missing future days"):
            self.score(self.rows[:-1])

    def test_legacy_reproduction_failure_prevents_eval_read(self):
        with patch.object(v25.v24, "run", side_effect=v25.TransferError("v2.4 mismatch")), \
             patch.object(v25.v24.v21, "selected_eval_rows") as read:
            with self.assertRaisesRegex(v25.TransferError, "v2.4 mismatch"):
                v25.run("/fake/train.parquet", "/fake/eval.parquet")
            read.assert_not_called()

    def test_identical_source_path_rejected(self):
        with self.assertRaisesRegex(v25.TransferError, "identical"):
            v25.run("/fake/a.parquet", "/fake/a.parquet")


if __name__ == "__main__":
    unittest.main()
