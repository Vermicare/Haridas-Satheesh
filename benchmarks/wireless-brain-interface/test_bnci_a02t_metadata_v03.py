"""Synthetic structural tests. Never fetch upstream or inspect real labels."""
import io
import unittest
import numpy as np
from scipy.io import savemat
from bnci_a02t_metadata_v03 import inspect_bytes, validate_url


def fixture(baselines=3, tasks=6, cues=48, fs=250., invalid_trial=None):
    runs = []
    for i in range(baselines + tasks):
        trial = np.array([], dtype=np.float64) if i < baselines else np.arange(1, cues+1, dtype=np.float64)
        if i == baselines and invalid_trial is not None:
            trial = np.array(invalid_trial, dtype=np.float64)
        runs.append({'X': np.zeros((300, 25)), 'fs': fs, 'trial': trial})
    stream = io.BytesIO()
    savemat(stream, {'data': np.array(runs, dtype=object)})
    return stream.getvalue()


class TestA02T(unittest.TestCase):
    def test_expected_shape_and_no_labels(self):
        r = inspect_bytes(fixture())
        self.assertEqual((r['blocks'], r['cue_free_baseline_blocks'], r['cued_task_blocks'], r['cues_total']), (9, 3, 6, 288))
        self.assertTrue(r['six_task_runs_48_cues_each'])
        self.assertFalse(r['class_label_values_inspected'])
        self.assertFalse(r['raw_eeg_persisted_or_uploaded'])

    def test_wrong_run_count_is_not_rewritten(self):
        self.assertFalse(inspect_bytes(fixture(tasks=5))['six_task_runs_48_cues_each'])

    def test_wrong_cues_are_not_rewritten(self):
        self.assertFalse(inspect_bytes(fixture(cues=47))['six_task_runs_48_cues_each'])

    def test_nonfinite_frequency_rejected(self):
        for fs in (float('nan'), float('inf'), -1.):
            with self.subTest(fs=fs), self.assertRaisesRegex(ValueError, 'sample frequency'):
                inspect_bytes(fixture(fs=fs))

    def test_bad_trial_positions_rejected(self):
        for trials in ([1., 1.], [1., float('nan')], [1., 1.5], [1., 301.], [2., 1.]):
            with self.subTest(trials=trials), self.assertRaisesRegex(ValueError, 'cue sample positions'):
                inspect_bytes(fixture(invalid_trial=trials))

    def test_source_validation_rejects_wrong_sessions_and_hosts(self):
        for url in ('http://bnci-horizon-2020.eu/database/data-sets/001-2014/A02T.mat',
                    'https://bnci-horizon-2020.eu/database/data-sets/001-2014/A02E.mat',
                    'https://example.com/database/data-sets/001-2014/A02T.mat',
                    'https://bnci-horizon-2020.eu/database/data-sets/001-2014/A02T.mat?x=1'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_truncated_or_wrong_format_rejected(self):
        for raw in (b'', b'X' * 300):
            with self.assertRaises(ValueError):
                inspect_bytes(raw)


if __name__ == '__main__':
    unittest.main()
