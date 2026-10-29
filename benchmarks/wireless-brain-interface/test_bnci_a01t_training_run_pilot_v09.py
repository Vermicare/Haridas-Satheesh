"""Fictional-only regression tests; never acquire or embed public EEG."""
import copy
from types import SimpleNamespace
import unittest

import numpy as np

import bnci_a01t_training_run_pilot_v09 as pilot


def fixture(seed=20261029):
    rng = np.random.default_rng(seed)
    blocks = [SimpleNamespace(trial=np.array([], dtype=int)) for _ in range(3)]
    # Six fictional 48-trial runs, with trial t=0 spaced 7.5 seconds apart.
    for _ in range(6):
        labels = np.tile(np.arange(1, 5), 12)
        onsets = 251 + 1875 * np.arange(48)
        n = int(onsets[-1] + 1500)
        x = rng.normal(size=(n, 25)).astype(np.float32)
        for onset, y in zip(onsets, labels):
            begin = onset - 1 + 625
            x[begin:begin + 500, y - 1] *= 3.0
        blocks.append(SimpleNamespace(X=x, fs=250., trial=onsets, y=labels))
    return blocks


class TrainingOnlyPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = fixture()
        cls.pairs = pilot.extract_run_features(cls.blocks)

    def test_six_runs_and_split_counts(self):
        train, cal, test = pilot.split_training_session(self.pairs)
        self.assertEqual((len(train[1]), len(cal[1]), len(test[1])), (144, 48, 96))
        self.assertEqual(train[0].shape, (144, 22))

    def test_frozen_thresholds_ignore_heldout_labels(self):
        train, cal, test = pilot.split_training_session(self.pairs)
        frozen = pilot.freeze_on_training_and_calibration(train, cal)
        changed = (test[0], np.roll(test[1], 1))
        frozen_again = pilot.freeze_on_training_and_calibration(train, cal)
        self.assertEqual(frozen[2], frozen_again[2])
        self.assertEqual(frozen[1].coef_.tolist(), frozen_again[1].coef_.tolist())
        self.assertEqual(pilot.score_frozen(frozen, test)['heldout_trials'], 96)
        self.assertEqual(pilot.score_frozen(frozen, changed)['heldout_trials'], 96)

    def test_eog_channels_do_not_affect_features(self):
        modified = copy.deepcopy(self.blocks)
        for block in modified[3:]:
            block.X[:, 22:] = 999999
        a = pilot.extract_run_features(modified)
        for x, y in zip(a, self.pairs):
            np.testing.assert_array_equal(x[0], y[0])

    def test_reject_cue_out_of_bounds(self):
        modified = copy.deepcopy(self.blocks)
        modified[3].trial[-1] = len(modified[3].X) + 1
        with self.assertRaisesRegex(ValueError, 'epoch out of bounds'):
            pilot.extract_run_features(modified)

    def test_reject_missing_trial(self):
        modified = copy.deepcopy(self.blocks)
        modified[3].trial = modified[3].trial[:-1]
        with self.assertRaisesRegex(ValueError, 'trial count'):
            pilot.extract_run_features(modified)

    def test_reject_missing_label(self):
        modified = copy.deepcopy(self.blocks)
        modified[3].y[0] = 9
        with self.assertRaisesRegex(ValueError, 'four-class labels'):
            pilot.extract_run_features(modified)

    def test_reject_eeg_nonfinite(self):
        modified = copy.deepcopy(self.blocks)
        modified[3].X[200, 0] = np.nan
        with self.assertRaisesRegex(ValueError, 'nonfinite EEG'):
            pilot.extract_run_features(modified)

    def test_reject_wrong_fs(self):
        modified = copy.deepcopy(self.blocks)
        modified[3].fs = 256
        with self.assertRaisesRegex(ValueError, 'sampling rate'):
            pilot.extract_run_features(modified)

    def test_reject_baseline_cue(self):
        modified = copy.deepcopy(self.blocks)
        modified[0].trial = np.array([1])
        with self.assertRaisesRegex(ValueError, 'baseline blocks'):
            pilot.extract_run_features(modified)

    def test_reject_wrong_block_count(self):
        with self.assertRaisesRegex(ValueError, 'block count'):
            pilot.extract_run_features(self.blocks[:-1])

    def test_source_pin_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'byte length'):
            pilot.verify_source_bytes(b'MATLAB 5.0 MAT-file')

    def test_reject_evaluation_source_url(self):
        with self.assertRaises(ValueError):
            pilot.validate_source_url('https://bnci-horizon-2020.eu/database/data-sets/001-2014/A01E.mat')

    def test_zero_acted_is_null_not_zero_risk(self):
        train, cal, test = pilot.split_training_session(self.pairs)
        scaler, model, _ = pilot.freeze_on_training_and_calibration(train, cal)
        result = pilot.score_frozen((scaler, model, {'0.50': 1.1}), test)
        self.assertEqual(result['confidence_only_abstention']['0.50']['heldout_acted_n'], 0)
        self.assertIsNone(result['confidence_only_abstention']['0.50']['heldout_incorrect_action_risk'])

    def test_ece_hand_check(self):
        p = np.array([[.8, .1, .05, .05], [.1, .7, .1, .1]])
        self.assertAlmostEqual(pilot.ece_max_confidence(p, np.array([1, 1])), .45)

    def test_no_test_labels_in_fit_signature(self):
        self.assertEqual(pilot.freeze_on_training_and_calibration.__code__.co_argcount, 2)


if __name__ == '__main__':
    unittest.main()
