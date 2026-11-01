"""Fictional-only metric arithmetic; no publisher data, model, or downloads."""
import copy
import unittest

from freshretail_lt_pooled_metric_contract_v31 import (
    MetricContractError, score_fictional,
)


class PooledMetricContractTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"dt": "2025-07-14", "prediction": 0, "sale_amount": 1,
             "psd": 0, "stock_hour6_22_cnt": 0},
            {"dt": "2025-07-15", "prediction": 9, "sale_amount": 9,
             "psd": 1, "stock_hour6_22_cnt": 0},
            {"dt": "2025-07-14", "prediction": 500, "sale_amount": 500,
             "psd": -1, "stock_hour6_22_cnt": 0},
            {"dt": "2025-07-15", "prediction": 100, "sale_amount": 100,
             "psd": 1, "stock_hour6_22_cnt": 1},
        ]

    def test_pooled_ratio_differs_from_average_daily_ratio(self):
        r = score_fictional(self.rows)
        self.assertEqual((r["eligible_fictional_rows"], r["excluded_fictional_rows"]), (2, 2))
        self.assertAlmostEqual(r["pooled"]["wape_ratio"], .1)
        self.assertAlmostEqual(r["pooled"]["wpe_ratio"], -.1)
        self.assertAlmostEqual(r["pooled"]["mae"], .5)
        self.assertAlmostEqual(r["pooled"]["mse"], .5)
        self.assertAlmostEqual(r["per_day_diagnostics"]["2025-07-14"]["wape_ratio"], 1)
        self.assertAlmostEqual(r["per_day_diagnostics"]["2025-07-15"]["wape_ratio"], 0)
        self.assertNotEqual(r["pooled"]["wape_ratio"], .5)
        self.assertEqual(r["official_browser_equivalence"], "TBD")
        self.assertFalse(r["publisher_eval_labels_used"])

    def test_input_order_does_not_change_aggregate(self):
        self.assertEqual(score_fictional(self.rows), score_fictional(list(reversed(self.rows))))

    def test_negative_psd_is_excluded(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["psd"] = -0.01
        self.assertEqual(score_fictional(rows)["eligible_fictional_rows"], 1)

    def test_positive_stockout_is_excluded(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["stock_hour6_22_cnt"] = 1
        self.assertEqual(score_fictional(rows)["eligible_fictional_rows"], 1)

    def test_no_eligible_rows_rejected(self):
        with self.assertRaisesRegex(MetricContractError, "no eligible"):
            score_fictional(self.rows[2:])

    def test_zero_actual_denominator_rejected(self):
        rows = copy.deepcopy(self.rows[:2])
        for row in rows:
            row["sale_amount"] = 0
        with self.assertRaisesRegex(MetricContractError, "denominator"):
            score_fictional(rows)

    def test_per_day_zero_denominator_is_explicitly_undefined(self):
        rows = copy.deepcopy(self.rows[:2])
        rows[0]["sale_amount"] = 0
        result = score_fictional(rows)
        self.assertIsNone(result["per_day_diagnostics"]["2025-07-14"])
        self.assertEqual(result["pooled"]["scored_rows"], 2)

    def test_negative_prediction_or_label_rejected(self):
        for field in ("prediction", "sale_amount"):
            with self.subTest(field=field), self.assertRaisesRegex(MetricContractError, "negative"):
                rows = copy.deepcopy(self.rows)
                rows[0][field] = -0.1
                score_fictional(rows)

    def test_nonfinite_numeric_rejected(self):
        for bad in (float("nan"), float("inf"), "-inf", True, None, " 1"):
            with self.subTest(bad=bad), self.assertRaises(MetricContractError):
                rows = copy.deepcopy(self.rows)
                rows[0]["prediction"] = bad
                score_fictional(rows)

    def test_bad_stock_count_rejected(self):
        for bad in (True, -1, 25, 0.5, "01", "-1", None):
            with self.subTest(bad=bad), self.assertRaises(MetricContractError):
                rows = copy.deepcopy(self.rows)
                rows[0]["stock_hour6_22_cnt"] = bad
                score_fictional(rows)

    def test_forbidden_extra_eval_fields_rejected(self):
        for field in ("hours_sale", "hours_stock_status", "store_id"):
            with self.subTest(field=field), self.assertRaisesRegex(MetricContractError, "exact"):
                rows = copy.deepcopy(self.rows)
                rows[0][field] = 42
                score_fictional(rows)

    def test_missing_label_rejected(self):
        rows = copy.deepcopy(self.rows)
        del rows[0]["sale_amount"]
        with self.assertRaisesRegex(MetricContractError, "exact"):
            score_fictional(rows)

    def test_out_of_horizon_date_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["dt"] = "2025-07-21"
        with self.assertRaisesRegex(MetricContractError, "horizon"):
            score_fictional(rows)

    def test_noncanonical_date_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["dt"] = "2025-7-14"
        with self.assertRaisesRegex(MetricContractError, "date"):
            score_fictional(rows)

    def test_output_aggregate_only(self):
        result = score_fictional(self.rows)
        self.assertEqual(result["total_fictional_rows"], 4)
        self.assertNotIn("prediction", result)
        self.assertNotIn("sale_amount", result)
        self.assertFalse(result["full_target_coverage_verified"])


if __name__ == "__main__":
    unittest.main()
