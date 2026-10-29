"""Fictional-only tests for A01T v1.1; never download or embed EEG."""
import unittest
import numpy as np
from wbi_a01t_clean_subset_v11 import (
    score_clean_subset, require_frozen_v09_and_v10_match,
)


def fixture():
    # 96 fictional examples; 43 correct, 53 incorrect. Five flagged.
    prediction = np.arange(96) % 4 + 1
    labels = prediction.copy()
    labels[43:] = labels[43:] % 4 + 1
    p = np.full((96, 4), .1)
    p[np.arange(96), prediction - 1] = .7
    flags = np.zeros(96, dtype=int)
    flags[[0, 1, 44, 50, 90]] = 1
    return p, labels, flags, {'0.30': .7, '0.50': .8, '0.70': .9}


class CleanSubsetTests(unittest.TestCase):
    def test_hand_count_correct_and_flagged(self):
        p, y, f, t = fixture()
        r = score_clean_subset(p, y, f, t)
        self.assertEqual((r['all_trials_n'], r['all_trials_correct_n']), (96, 43))
        self.assertEqual((r['source_flagged_n'], r['source_unflagged_n']), (5, 91))
        self.assertEqual(r['source_unflagged_correct_n'], 41)
        self.assertAlmostEqual(r['source_unflagged_accuracy_observed'], 41 / 91)

    def test_thresholds_are_not_mutated(self):
        p, y, f, t = fixture()
        original = t.copy()
        score_clean_subset(p, y, f, t)
        self.assertEqual(t, original)

    def test_labels_change_accuracy_not_coverage(self):
        p, y, f, t = fixture()
        a = score_clean_subset(p, y, f, t)
        b = score_clean_subset(p, np.roll(y, 1), f, t)
        self.assertNotEqual(a['all_trials_correct_n'], b['all_trials_correct_n'])
        self.assertEqual(a['frozen_confidence_only']['0.30']['all_acted_n'],
                         b['frozen_confidence_only']['0.30']['all_acted_n'])

    def test_flagged_predictions_change_clean_result_not_primary(self):
        p, y, f, t = fixture()
        a = score_clean_subset(p, y, f, t)
        f2 = np.zeros(96, dtype=int)
        f2[[44, 45, 46, 47, 48]] = 1
        b = score_clean_subset(p, y, f2, t)
        self.assertEqual(a['all_trials_correct_n'], b['all_trials_correct_n'])
        self.assertNotEqual(a['source_unflagged_correct_n'], b['source_unflagged_correct_n'])

    def test_all_flagged_returns_null_not_zero(self):
        p, y, f, t = fixture()
        r = score_clean_subset(p, y, np.ones(96), t)
        self.assertIsNone(r['source_unflagged_accuracy_observed'])
        self.assertIsNone(r['frozen_confidence_only']['0.30']['unflagged_incorrect_action_risk'])

    def test_zero_acted_returns_null(self):
        p, y, f, _ = fixture()
        r = score_clean_subset(p, y, f, {'0.50': .95})
        self.assertEqual(r['frozen_confidence_only']['0.50']['unflagged_acted_n'], 0)
        self.assertIsNone(r['frozen_confidence_only']['0.50']['unflagged_incorrect_action_risk'])

    def test_reject_flag_length_mismatch(self):
        p, y, f, t = fixture()
        with self.assertRaisesRegex(ValueError, 'alignment'):
            score_clean_subset(p, y, f[:-1], t)

    def test_reject_nonbinary_flags(self):
        p, y, f, t = fixture()
        f[0] = 2
        with self.assertRaisesRegex(ValueError, 'source flags'):
            score_clean_subset(p, y, f, t)

    def test_reject_nonfinite_flags(self):
        p, y, f, t = fixture()
        f = f.astype(float)
        f[0] = np.nan
        with self.assertRaisesRegex(ValueError, 'source flags'):
            score_clean_subset(p, y, f, t)

    def test_reject_malformed_probabilities(self):
        p, y, f, t = fixture()
        p[0, 0] = .6
        with self.assertRaisesRegex(ValueError, 'simplex'):
            score_clean_subset(p, y, f, t)

    def test_reject_nonfinite_probabilities(self):
        p, y, f, t = fixture()
        p[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, 'simplex'):
            score_clean_subset(p, y, f, t)

    def test_reject_bad_labels(self):
        p, y, f, t = fixture()
        y[0] = 5
        with self.assertRaisesRegex(ValueError, 'labels'):
            score_clean_subset(p, y, f, t)

    def test_reject_unfrozen_threshold(self):
        p, y, f, t = fixture()
        t['0.50'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'threshold'):
            score_clean_subset(p, y, f, t)

    def test_frozen_result_mismatch_is_rejected(self):
        p, y, f, t = fixture()
        with self.assertRaisesRegex(ValueError, 'selective result mismatch'):
            require_frozen_v09_and_v10_match(score_clean_subset(p, y, f, t))


if __name__ == '__main__':
    unittest.main()
