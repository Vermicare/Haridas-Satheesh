"""Adversarial fictional-only contracts; no real EEG or labels."""
import unittest
from types import SimpleNamespace

import numpy as np

from bnci_a01t_artifact_audit_v10 import audit_flags, accuracy_identification_bounds, build_report


def fake_blocks(flagged_by_run=(0, 1, 2, 3, 4, 5)):
    blocks = [SimpleNamespace() for _ in range(3)]
    for n in flagged_by_run:
        flags = np.array([1] * n + [0] * (48 - n), dtype=int)
        blocks.append(SimpleNamespace(trial=np.arange(1, 49), artifacts=flags))
    return blocks


class ArtifactAuditContracts(unittest.TestCase):
    def test_split_accounting(self):
        per, splits = audit_flags(fake_blocks())
        self.assertEqual([r['artifact_flagged'] for r in per], list(range(6)))
        self.assertEqual(splits['training']['artifact_flagged'], 3)
        self.assertEqual(splits['calibration']['artifact_flagged'], 3)
        self.assertEqual(splits['heldout_within_day']['artifact_flagged'], 9)
        self.assertEqual(splits['heldout_within_day']['unflagged'], 87)

    def test_all_clean_bounds_equal_original(self):
        r = accuracy_identification_bounds(96, 43, 0)
        self.assertEqual(r['possible_unflagged_accuracy_min'], 43 / 96)
        self.assertEqual(r['possible_unflagged_accuracy_max'], 43 / 96)

    def test_nonzero_flag_bounds(self):
        r = accuracy_identification_bounds(96, 43, 9)
        self.assertEqual((r['possible_unflagged_correct_min'], r['possible_unflagged_correct_max']), (34, 43))
        self.assertEqual(r['possible_unflagged_accuracy_min'], 34 / 87)
        self.assertEqual(r['possible_unflagged_accuracy_max'], 43 / 87)

    def test_all_flagged_is_undefined(self):
        r = accuracy_identification_bounds(96, 43, 96)
        self.assertIsNone(r['possible_unflagged_accuracy_min'])
        self.assertIsNone(r['possible_unflagged_accuracy_max'])

    def test_possible_zero_clean_correct(self):
        self.assertEqual(accuracy_identification_bounds(96, 43, 50)['possible_unflagged_correct_min'], 0)

    def test_possible_all_clean_correct(self):
        self.assertEqual(accuracy_identification_bounds(96, 95, 10)['possible_unflagged_correct_max'], 86)

    def test_invalid_counts(self):
        for args in ((0, 0, 0), (96, -1, 0), (96, 97, 0), (96, 43, 97), (96, 43, -1), (96.0, 43, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                accuracy_identification_bounds(*args)

    def test_missing_flags_rejected(self):
        blocks = fake_blocks()
        del blocks[3].artifacts
        with self.assertRaisesRegex(ValueError, 'missing'):
            audit_flags(blocks)

    def test_wrong_length_rejected(self):
        blocks = fake_blocks()
        blocks[3].artifacts = np.zeros(47)
        with self.assertRaisesRegex(ValueError, '48'):
            audit_flags(blocks)

    def test_nonbinary_flag_rejected(self):
        blocks = fake_blocks()
        blocks[3].artifacts[0] = 2
        with self.assertRaisesRegex(ValueError, 'binary'):
            audit_flags(blocks)

    def test_nan_flag_rejected(self):
        blocks = fake_blocks()
        blocks[3].artifacts = np.zeros(48, dtype=float)
        blocks[3].artifacts[0] = np.nan
        with self.assertRaisesRegex(ValueError, 'binary'):
            audit_flags(blocks)

    def test_duplicate_trial_rejected(self):
        blocks = fake_blocks()
        blocks[3].trial[2] = blocks[3].trial[1]
        with self.assertRaisesRegex(ValueError, 'trial positions'):
            audit_flags(blocks)

    def test_zero_based_trial_rejected(self):
        blocks = fake_blocks()
        blocks[3].trial = np.arange(48)
        with self.assertRaisesRegex(ValueError, 'trial positions'):
            audit_flags(blocks)

    def test_wrong_block_count_rejected(self):
        with self.assertRaisesRegex(ValueError, 'three baseline'):
            audit_flags(fake_blocks()[:-1])

    def test_no_trial_level_output(self):
        report = build_report(fake_blocks())
        self.assertEqual(len(report['task_runs']), 6)
        self.assertTrue(all(set(r) == {'task_run', 'total_trials', 'artifact_flagged', 'unflagged'} for r in report['task_runs']))
        self.assertFalse(report['trial_level_flags_or_labels_persisted'])


if __name__ == '__main__':
    unittest.main()
