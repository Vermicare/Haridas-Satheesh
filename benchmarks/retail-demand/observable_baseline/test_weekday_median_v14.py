"""Fictional and adversarial contract tests for exploratory retail v1.4."""
import datetime as dt
import math
import unittest

from retail_gate import EvidenceError
from weekday_median_v14 import (
    finite_median, weekday_median_forecast, store_cluster_ci, evaluate_v14,
)


def training_rows():
    start = dt.date(2024, 3, 28)
    return [
        {"day": start + dt.timedelta(days=i), "y": float(1 + i % 7),
         "censored": False} for i in range(90)
    ]


def publisher_row(i, *, censored=False, y=None):
    start = dt.date(2024, 3, 28)
    sale = [0.0] * 24
    sale[6] = float(1 + i % 7 if y is None else y)
    flags = [0] * 24
    flags[6] = int(censored)
    return {
        "store_id": 1, "product_id": 2,
        "dt": (start + dt.timedelta(days=i)).isoformat(),
        "hours_sale": sale, "hours_stock_status": flags,
        "stock_hour6_22_cnt": int(censored),
    }


class WeekdayBaselineTests(unittest.TestCase):
    def test_known_weekday_median(self):
        tr = training_rows()
        day = dt.date(2024, 6, 26)
        forecast, counts = weekday_median_forecast(tr, [day])
        self.assertEqual(forecast, [7.0])
        self.assertEqual(counts, {"weekday": 1, "recent14": 0, "zero": 0})

    def test_censored_training_spike_cannot_influence_forecast(self):
        tr = training_rows()
        day = dt.date(2024, 6, 26)
        expected = weekday_median_forecast(tr, [day])[0]
        for row in tr:
            if row["day"].weekday() == day.weekday():
                row["y"] = 1e12
                row["censored"] = True
        observed, counts = weekday_median_forecast(tr, [day])
        self.assertNotEqual(observed, expected)
        self.assertEqual(counts["recent14"], 1)
        self.assertTrue(math.isfinite(observed[0]))

    def test_last14_fallback_ignores_old_and_censored(self):
        tr = training_rows()
        day = dt.date(2024, 6, 26)
        for row in tr:
            if row["day"].weekday() == day.weekday():
                row["censored"] = True
                row["y"] = 1e9
        value, counts = weekday_median_forecast(tr, [day])
        recent = [r["y"] for r in tr[-14:] if not r["censored"]]
        self.assertEqual(value, [finite_median(recent)])
        self.assertEqual(counts["recent14"], 1)

    def test_zero_fallback_is_explicit_not_inferred_demand(self):
        tr = training_rows()
        for row in tr:
            row["censored"] = True
        pred, counts = weekday_median_forecast(tr, [dt.date(2024, 6, 26)])
        self.assertEqual(pred, [0.0])
        self.assertEqual(counts["zero"], 1)

    def test_train_only_future_labels_not_passed_to_forecaster(self):
        tr = training_rows()
        dates = [dt.date(2024, 6, 26) + dt.timedelta(days=i) for i in range(7)]
        p1, c1 = weekday_median_forecast(tr, dates)
        # No evaluation labels or availability fields are supplied to the API.
        p2, c2 = weekday_median_forecast(tr, list(dates))
        self.assertEqual((p1, c1), (p2, c2))

    def test_bad_future_dates_rejected(self):
        tr = training_rows()
        with self.assertRaises(EvidenceError):
            weekday_median_forecast(tr, [tr[-1]["day"]])
        with self.assertRaises(EvidenceError):
            weekday_median_forecast(tr, [dt.date(2024, 6, 26)] * 2)
        with self.assertRaises(EvidenceError):
            weekday_median_forecast(tr[:-1], [dt.date(2024, 6, 26)])

    def test_finite_median_rejects_nonfinite_and_boolean(self):
        for values in ([], [float("nan")], [float("inf")], [True], [-1]):
            with self.subTest(values=values), self.assertRaises(EvidenceError):
                finite_median(values)
        self.assertEqual(finite_median([1e308, 1e308]), 1e308)

    def test_store_cluster_bootstrap_determinism_and_nonfinite_rejection(self):
        pairs = [(1, 0.3), (1, -0.1), (2, 0.2), (3, -0.4)]
        self.assertEqual(store_cluster_ci(pairs, reps=100), store_cluster_ci(pairs, reps=100))
        self.assertIsNone(store_cluster_ci([(1, 0.1)]))
        with self.assertRaises(EvidenceError):
            store_cluster_ci([(1, float("nan")), (2, 0.1)])
        with self.assertRaises(EvidenceError):
            store_cluster_ci(pairs, reps=0)

    def test_same_frozen_observable_denominator_on_fictional_fixture(self):
        train = [publisher_row(i) for i in range(90)]
        evaluation = [publisher_row(i, censored=(i % 3 == 0)) for i in range(90, 97)]
        result = evaluate_v14([(1, 2)], train, evaluation)
        self.assertEqual(result["scored_days"], sum(i % 3 != 0 for i in range(90, 97)))
        self.assertEqual(result["original_v12_metrics"]["uncensored_eval_days_scored"], result["scored_days"])
        self.assertEqual(sum(result["training_only_fallback_counts_all_7day_predictions"].values()), 7)

    def test_eval_label_mutation_does_not_change_frozen_training_forecast(self):
        tr = training_rows()
        days = [dt.date(2024, 6, 26) + dt.timedelta(days=i) for i in range(7)]
        predictions, _ = weekday_median_forecast(tr, days)
        # Changing future labels cannot enter weekday_median_forecast.
        changed_labels = [1e9] * 7
        self.assertEqual(len(predictions), len(changed_labels))
        self.assertEqual(predictions, weekday_median_forecast(tr, days)[0])

    def test_missing_eval_row_fails_without_cohort_replacement(self):
        train = [publisher_row(i) for i in range(90)]
        evaluation = [publisher_row(i) for i in range(90, 96)]
        with self.assertRaises(EvidenceError):
            evaluate_v14([(1, 2)], train, evaluation)

    def test_duplicate_cohort_fails(self):
        train = [publisher_row(i) for i in range(90)]
        evaluation = [publisher_row(i) for i in range(90, 97)]
        with self.assertRaises(EvidenceError):
            evaluate_v14([(1, 2), (1, 2)], train, evaluation)


if __name__ == "__main__":
    unittest.main()
