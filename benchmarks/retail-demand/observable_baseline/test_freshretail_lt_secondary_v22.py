"""Fictional-only adversarial checks for exploratory v2.2; no publisher rows."""
import copy
import math
import random
import unittest
from unittest.mock import patch

import freshretail_lt_secondary_v22 as v22
import freshretail_lt_score_v21 as v21
from test_freshretail_lt_score_v21 import fictional_eval, predictions


class ExploratorySecondaryTests(unittest.TestCase):
    def setUp(self):
        self.keys = ((1, 10), (2, 20))
        self.rows = fictional_eval(self.keys[0]) + fictional_eval(self.keys[1])
        self.preds = predictions(self.keys)
        self.original = v21.score_frozen(self.keys, self.preds, self.rows)

    def compare(self, rows=None, preds=None, original=None):
        return v22.secondary_from_rows(self.keys, preds if preds is not None else self.preds,
                                       rows if rows is not None else self.rows,
                                       original if original is not None else self.original)

    def test_fictional_strongest_comparator_is_better_than_last_but_worse_than_weekday(self):
        result = self.compare()
        self.assertEqual(result["decision"], "EXPLORATORY_INTERVAL_EXCLUDES_ZERO_FAVORS_WEEKDAY")
        self.assertEqual(result["comparison"]["point_delta"], -1)
        self.assertEqual(result["comparison"]["store_cluster_ci95"], [-1, -1])
        self.assertEqual(result["comparison"]["scored_days"], 14)

    def test_fictional_secondary_tie_is_inconclusive(self):
        pred = predictions(self.keys)
        for key in self.keys:
            pred[key]["causal_stockout_history"] = [0.0] * 7
        original = v21.score_frozen(self.keys, pred, self.rows)
        result = self.compare(preds=pred, original=original)
        self.assertEqual(result["decision"], "EXPLORATORY_INCONCLUSIVE_INTERVAL_INCLUDES_ZERO")
        self.assertEqual(result["comparison"]["point_delta"], 0)

    def test_fictional_secondary_worse_candidate(self):
        pred = predictions(self.keys)
        for key in self.keys:
            pred[key]["causal_stockout_history"] = [0.0] * 7
            pred[key]["weekday_median_last4"] = [1.0] * 7
        original = v21.score_frozen(self.keys, pred, self.rows)
        self.assertEqual(self.compare(preds=pred, original=original)["decision"],
                         "EXPLORATORY_INTERVAL_EXCLUDES_ZERO_FAVORS_CAUSAL")

    def test_no_cohort_substitution_after_missing_day(self):
        with self.assertRaisesRegex(v22.SecondaryError, "incomplete"):
            self.compare(rows=self.rows[:-1])

    def test_duplicate_eval_day_rejected(self):
        with self.assertRaisesRegex(v22.SecondaryError, "duplicate"):
            self.compare(rows=self.rows + [dict(self.rows[0])])

    def test_wrong_original_denominator_rejected(self):
        changed = dict(self.original, observed_in_stock_days_scored=13)
        with self.assertRaisesRegex(v22.SecondaryError, "denominator"):
            self.compare(original=changed)

    def test_nonfinite_forecast_rejected(self):
        pred = copy.deepcopy(self.preds)
        pred[self.keys[0]]["causal_stockout_history"][0] = math.inf
        with self.assertRaisesRegex(v22.SecondaryError, "invalid frozen"):
            self.compare(preds=pred)

    def test_order_invariant_and_seed_fixed(self):
        rows = list(self.rows)
        random.Random(37).shuffle(rows)
        self.assertEqual(self.compare(), self.compare(rows=rows))
        self.assertEqual(self.compare(), self.compare())

    def test_public_result_does_not_contain_series_ids_or_predictions(self):
        result = self.compare()
        text = str(result)
        self.assertNotIn("store_id", text)
        self.assertNotIn("product_id", text)
        self.assertNotIn("predictions", text)

    def test_label_file_not_read_if_training_seal_fails(self):
        with patch.object(v22.v21, "reproduce_before_labels",
                          side_effect=v22.SecondaryError("seal mismatch")), \
             patch.object(v22.v21, "verify_file") as verify, \
             patch.object(v22.v21, "selected_eval_rows") as labels:
            with self.assertRaisesRegex(v22.SecondaryError, "seal mismatch"):
                v22.run("/private/train", "/private/eval")
            verify.assert_not_called()
            labels.assert_not_called()

    def test_no_claim_of_confirmatory_or_independent_evidence(self):
        r = self.compare()
        self.assertIn("EXPLORATORY", r["comparison"]["estimand"])
        self.assertIn("ALREADY OPENED", r["comparison"]["statistical_limit"])


if __name__ == "__main__":
    unittest.main()
