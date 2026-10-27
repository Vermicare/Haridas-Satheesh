"""Fictional contract tests for store-disjoint selection; no publisher data loaded."""
import copy
import unittest
from unittest.mock import patch

import official_holdout_v12 as frozen
from retail_gate import EvidenceError
import store_disjoint_v15 as target


def fictional_ids():
    # 1000 distinct stores, two products each; deliberately independent of real IDs.
    return [(store, product) for store in range(1000) for product in range(2)]


class StoreDisjointTests(unittest.TestCase):
    def setUp(self):
        self.ids = fictional_ids()
        self.original = frozen.select_train_only(self.ids)
        self.pin = patch.object(target, "ORIGINAL_COHORT_SHA256",
                                target.digest_cohort(self.original))
        self.pin.start()
        self.addCleanup(self.pin.stop)

    def test_selection_excludes_all_original_stores(self):
        original, new = target.select_disjoint_training_cohort(self.ids)
        self.assertEqual(original, self.original)
        self.assertEqual(len(new), 512)
        self.assertEqual(len(set(new)), 512)
        self.assertFalse({s for s, _ in original} & {s for s, _ in new})

    def test_train_order_and_duplicates_do_not_change_selection(self):
        baseline = target.select_disjoint_training_cohort(self.ids)
        self.assertEqual(baseline, target.select_disjoint_training_cohort(
            list(reversed(self.ids)) + self.ids[:40]))

    def test_selected_ids_are_from_training_only(self):
        _, new = target.select_disjoint_training_cohort(self.ids)
        self.assertTrue(set(new).issubset(set(self.ids)))
        # The API takes no eval labels, stock flags, dates or test identifiers.
        self.assertNotIn((1001, 9), new)

    def test_fails_closed_when_too_few_unseen_stores(self):
        with self.assertRaisesRegex(EvidenceError, "insufficient store-disjoint"):
            target.select_disjoint_training_cohort(self.ids, count=2000)

    def test_invalid_count_rejected(self):
        for count in (0, -1, True, 1.2):
            with self.subTest(count=count), self.assertRaises(EvidenceError):
                target.select_disjoint_training_cohort(self.ids, count=count)

    def test_original_pin_mutation_rejected(self):
        with patch.object(target, "ORIGINAL_COHORT_SHA256", "0" * 64):
            with self.assertRaisesRegex(EvidenceError, "identity changed"):
                target.select_disjoint_training_cohort(self.ids)

    def test_bad_train_identifiers_rejected(self):
        with self.assertRaises(EvidenceError):
            target.select_disjoint_training_cohort(self.ids + [(True, 1)])
        with self.assertRaises(EvidenceError):
            target.select_disjoint_training_cohort(self.ids + [(-1, 1)])

    @staticmethod
    def fictional_metrics(interval, weekday=0.46, last=0.48):
        return {
            "weekday_median_minus_last_observed_store_cluster_ci95": interval,
            "weekday_median_last4_day_weighted_mae": weekday,
            "original_v12_metrics": {"day_weighted_mae": {"last_observed": last}},
        }

    def test_favorable_point_with_interval_crossing_zero_fails_gate(self):
        report = target.interpret_primary_gate(self.fictional_metrics([-0.04, 0.02]))
        self.assertTrue(report["point_mae_better"])
        self.assertFalse(report["conditional_store_transfer_gate_passed"])

    def test_favorable_point_and_interval_below_zero_passes_conditional_gate(self):
        report = target.interpret_primary_gate(self.fictional_metrics([-0.04, -0.01]))
        self.assertTrue(report["conditional_store_transfer_gate_passed"])
        self.assertIn("not an independent temporal", report["interpretation_limit"])

    def test_unfavorable_point_fails_even_if_interval_favorable(self):
        report = target.interpret_primary_gate(self.fictional_metrics([-0.04, -0.01], weekday=0.49))
        self.assertFalse(report["conditional_store_transfer_gate_passed"])

    def test_invalid_intervals_rejected(self):
        for interval in (None, [], [-0.01], [0.2, -0.1], [float("nan"), 0.1],
                         [float("-inf"), 0.1], [True, False]):
            with self.subTest(interval=interval), self.assertRaises(EvidenceError):
                target.interpret_primary_gate(self.fictional_metrics(interval))


if __name__ == "__main__":
    unittest.main()
