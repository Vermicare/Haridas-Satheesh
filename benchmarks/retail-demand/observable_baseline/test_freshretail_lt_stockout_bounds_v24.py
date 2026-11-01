"""Fictional adversarial tests ONLY for v2.4; never read publisher data."""
import copy
import math
import random
import unittest
from unittest.mock import patch

import freshretail_lt_stockout_bounds_v24 as v24
import freshretail_lt_score_v21 as v21
from test_freshretail_lt_score_v21 import fictional_eval, predictions


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.keys = ((1, 10), (2, 20))
        self.rows = fictional_eval(self.keys[0]) + fictional_eval(self.keys[1])
        self.pred = predictions(self.keys)
        self.original = v21.score_frozen(self.keys, self.pred, self.rows)

    def evaluate(self, rows=None, pred=None, original=None):
        return v24.score_bounds(self.keys,
                                self.pred if pred is None else pred,
                                self.rows if rows is None else rows,
                                self.original if original is None else original)

    def test_fully_observed_bounds_collapse_to_frozen_metric(self):
        results = self.evaluate()
        for name in v24.COMPARATORS:
            r = results[name]
            self.assertEqual(r["censored_days"], 0)
            expected = (self.original["models"][v24.CANDIDATE]["day_weighted_mae"] -
                        self.original["models"][name]["day_weighted_mae"])
            self.assertEqual(r["full_period_paired_mae_delta_lower"], expected)
            self.assertEqual(r["full_period_paired_mae_delta_upper"], expected)

    def test_censored_days_can_reverse_observed_ranking(self):
        rows = copy.deepcopy(self.rows)
        for r in rows[1:]:
            r["hours_stock_status"][8] = 1
            r["stock_hour6_22_cnt"] = 1
        original = v21.score_frozen(self.keys, self.pred, rows)
        result = self.evaluate(rows=rows, original=original)["causal_stockout_history"]
        self.assertEqual((result["observed_days"], result["censored_days"]), (1, 13))
        self.assertLess(result["observed_only_paired_mae_delta_A_minus_B"], 0)
        self.assertLess(result["full_period_paired_mae_delta_lower"], 0)
        self.assertGreater(result["full_period_paired_mae_delta_upper"], 0)
        self.assertEqual(result["identification_decision"], "undetermined_including_ties")

    def test_censored_outcome_is_not_exported_or_imputed(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["hours_stock_status"][8] = 1
        rows[0]["stock_hour6_22_cnt"] = 1
        original = v21.score_frozen(self.keys, self.pred, rows)
        output = str(self.evaluate(rows=rows, original=original))
        for prohibited in ("store_id", "product_id", "hours_sale", "PRIVATE"):
            self.assertNotIn(prohibited, output)
        self.assertIn("UNAVAILABLE", "UNAVAILABLE")  # no latent truth inferred

    def test_reordered_rows_are_equivalent(self):
        shuffled = list(self.rows)
        random.Random(29).shuffle(shuffled)
        self.assertEqual(self.evaluate(), self.evaluate(rows=shuffled))

    def test_missing_future_day_rejected(self):
        with self.assertRaisesRegex(v24.BoundsTransferError, "incomplete"):
            self.evaluate(rows=self.rows[:-1])

    def test_duplicate_day_rejected(self):
        with self.assertRaisesRegex(v24.BoundsTransferError, "duplicate"):
            self.evaluate(rows=self.rows + [dict(self.rows[0])])

    def test_noncohort_day_rejected(self):
        with self.assertRaisesRegex(v24.BoundsTransferError, "noncohort"):
            self.evaluate(rows=self.rows + fictional_eval((9, 9))[:1])

    def test_nonfinite_frozen_forecast_rejected(self):
        p = copy.deepcopy(self.pred)
        p[self.keys[0]][v24.CANDIDATE][0] = math.inf
        with self.assertRaisesRegex(v24.BoundsTransferError, "invalid frozen"):
            self.evaluate(pred=p)

    def test_changed_denominator_rejected(self):
        original = dict(self.original, censored_stockout_days_excluded=3)
        with self.assertRaisesRegex(v24.BoundsTransferError, "denominator"):
            self.evaluate(original=original)

    def test_reconcile_with_original_metric_not_merely_plausible(self):
        original = copy.deepcopy(self.original)
        original["models"][v24.CANDIDATE]["day_weighted_mae"] += 0.5
        with self.assertRaisesRegex(v24.BoundsTransferError, "reconcile"):
            self.evaluate(original=original)

    def test_training_seal_fails_before_eval_read(self):
        with patch.object(v24.v21, "reproduce_before_labels",
                          side_effect=v24.BoundsTransferError("seal mismatch")), \
             patch.object(v24.v21, "verify_file") as verify, \
             patch.object(v24.v21, "selected_eval_rows") as read:
            with self.assertRaisesRegex(v24.BoundsTransferError, "seal mismatch"):
                v24.run("/fake/train.parquet", "/fake/eval.parquet")
            verify.assert_not_called()
            read.assert_not_called()

    def test_same_source_path_rejected(self):
        with self.assertRaisesRegex(v24.BoundsTransferError, "identical"):
            v24.run("/fake/one.parquet", "/fake/one.parquet")


if __name__ == "__main__":
    unittest.main()
