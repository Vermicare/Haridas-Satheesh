"""Fictional-only adversarial controls; NO publisher EVAL labels in unit tests."""
import datetime as dt
import math
import random
import unittest
from unittest.mock import patch

import freshretail_lt_score_v21 as v21


def fictional_eval(key, *, sale=0.0, censored=False):
    result = []
    for day in v21.v20.FUTURE:
        flags = [0] * 24
        if censored:
            flags[8] = 1
        result.append({
            "store_id": key[0], "product_id": key[1], "dt": day.isoformat(),
            "hours_sale": [sale] * 24, "hours_stock_status": flags,
            "stock_hour6_22_cnt": 1 if censored else 0,
        })
    return result


def predictions(keys, *, candidate=0.0, baseline=2.0):
    return {key: {"last_observed": [baseline] * 7,
                  "seasonal_naive": [1.0] * 7,
                  "causal_stockout_history": [1.0] * 7,
                  "weekday_median_last4": [candidate] * 7}
            for key in keys}


class FictionalV21Scoring(unittest.TestCase):
    def setUp(self):
        self.keys = ((1, 10), (2, 20))
        self.rows = fictional_eval(self.keys[0]) + fictional_eval(self.keys[1])
        self.forecasts = predictions(self.keys)

    def test_fictional_strict_improvement_passes_matching_store_interval(self):
        r = v21.score_frozen(self.keys, self.forecasts, self.rows)
        self.assertEqual(r["decision"], "PASSED_PREREGISTERED_MAE_GATE")
        self.assertEqual(r["observed_in_stock_days_scored"], 14)
        self.assertEqual(r["primary_comparison"]["point_delta"], -2)
        self.assertEqual(r["primary_comparison"]["store_cluster_ci95"], [-2, -2])
        self.assertEqual(r["models"]["weekday_median_last4"]["wape"], "TBD")

    def test_worse_candidate_fails_even_with_complete_labels(self):
        r = v21.score_frozen(self.keys, predictions(self.keys, candidate=3), self.rows)
        self.assertEqual(r["decision"], "FAILED_PREREGISTERED_MAE_SUPERIORITY_GATE")
        self.assertGreater(r["primary_comparison"]["point_delta"], 0)

    def test_equal_candidate_fails(self):
        r = v21.score_frozen(self.keys, predictions(self.keys, candidate=2), self.rows)
        self.assertEqual(r["decision"], "FAILED_PREREGISTERED_MAE_SUPERIORITY_GATE")

    def test_eval_missing_one_selected_future_day_aborts_no_replacement(self):
        with self.assertRaisesRegex(v21.ScoreError, "missing future days"):
            v21.score_frozen(self.keys, self.forecasts, self.rows[:-1])

    def test_duplicate_selected_eval_day_aborts(self):
        with self.assertRaisesRegex(v21.ScoreError, "duplicate selected"):
            v21.score_frozen(self.keys, self.forecasts, self.rows + [dict(self.rows[0])])

    def test_selected_eval_outside_frozen_horizon_aborts(self):
        bad = dict(self.rows[0], dt="2025-07-21")
        with self.assertRaisesRegex(v21.ScoreError, "outside frozen"):
            v21.score_frozen(self.keys, self.forecasts, self.rows + [bad])

    def test_unknown_selected_row_is_not_substituted(self):
        with self.assertRaisesRegex(v21.ScoreError, "noncohort"):
            v21.score_frozen(self.keys, self.forecasts, self.rows + fictional_eval((9, 99))[:1])

    def test_censored_days_not_scored_but_denominator_reported(self):
        rows = fictional_eval(self.keys[0], censored=True) + fictional_eval(self.keys[1])
        r = v21.score_frozen(self.keys, self.forecasts, rows)
        self.assertEqual(r["observed_in_stock_days_scored"], 7)
        self.assertEqual(r["censored_stockout_days_excluded"], 7)
        self.assertEqual(r["scored_series"], 1)
        self.assertEqual(r["decision"], "INCONCLUSIVE_TOO_FEW_SCORED_STORES")

    def test_all_censored_is_inconclusive_not_success(self):
        rows = fictional_eval(self.keys[0], censored=True) + fictional_eval(self.keys[1], censored=True)
        r = v21.score_frozen(self.keys, self.forecasts, rows)
        self.assertEqual(r["decision"], "INCONCLUSIVE_NO_IN_STOCK_DAYS")
        self.assertIsNone(r["primary_comparison"])

    def test_nonfinite_forecast_rejected(self):
        broken = predictions(self.keys)
        broken[self.keys[0]]["weekday_median_last4"][0] = math.inf
        with self.assertRaisesRegex(v21.ScoreError, "nonfinite"):
            v21.score_frozen(self.keys, broken, self.rows)

    def test_invalid_stock_status_rejected(self):
        rows = [dict(x) for x in self.rows]
        rows[0]["stock_hour6_22_cnt"] = 2
        with self.assertRaises(ValueError):
            v21.score_frozen(self.keys, self.forecasts, rows)

    def test_eval_row_order_does_not_change_results(self):
        shuffled = list(self.rows)
        random.Random(21).shuffle(shuffled)
        a = v21.score_frozen(self.keys, self.forecasts, self.rows)
        b = v21.score_frozen(self.keys, self.forecasts, shuffled)
        self.assertEqual(a, b)

    def test_prediction_seal_mismatch_aborts_before_eval_file_access(self):
        with patch.object(v21, "reproduce_before_labels", side_effect=v21.ScoreError("seal mismatch")), \
             patch.object(v21, "verify_file") as verify, \
             patch.object(v21, "selected_eval_rows") as read_eval:
            with self.assertRaisesRegex(v21.ScoreError, "seal mismatch"):
                v21.run("/fake/train.parquet", "/fake/eval.parquet")
            verify.assert_not_called()
            read_eval.assert_not_called()

    def test_v20_mismatch_aborts_before_independent_training_read(self):
        bad = {"prediction_sha256": "0"*64,
               "cohort": {"selected_cohort_sha256": v21.PINNED_COHORT_SHA256},
               "evaluation_labels_read": False}
        with patch.object(v21.v20, "run", return_value=bad), \
             patch.object(v21.v19, "parquet_rows") as read_train:
            with self.assertRaisesRegex(v21.ScoreError, "original TRAIN-only"):
                v21.reproduce_before_labels("/fake/train")
            read_train.assert_not_called()

    def test_no_raw_ids_or_predictions_in_public_result(self):
        r = v21.score_frozen(self.keys, self.forecasts, self.rows)
        self.assertNotIn("predictions", r)
        self.assertNotIn("store_id", r)
        self.assertNotIn("product_id", r)


if __name__ == "__main__":
    unittest.main()
