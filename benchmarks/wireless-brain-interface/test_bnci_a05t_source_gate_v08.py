"""Fictional metadata-only adversarial controls; no real EEG is opened."""
import hashlib
import unittest
from unittest.mock import patch

import bnci_a05t_source_gate_v08 as gate

RAW = b'fictional-not-eeg-' * 16


def fixture():
    return {
        'dataset': 'BNCI2014_001', 'session': 'T_training',
        'source_sha256': hashlib.sha256(RAW).hexdigest(), 'source_bytes': len(RAW),
        'sha256_is_provider_authenticated': False,
        'class_label_values_inspected': False,
        'raw_eeg_persisted_or_uploaded': False,
        'evaluation_session_or_labels_accessed': False,
        'decode_accuracy': 'TBD', 'false_action_risk': 'TBD',
        'blocks': 9, 'cue_free_baseline_blocks': 3,
        'cued_task_blocks': 6, 'cues_total': 288,
        'six_task_runs_48_cues_each': True,
        'block_metadata': [
            {'block_index_zero_based': i, 'samples': 100,
             'channels': 25, 'sampling_rate_hz': 250.0,
             'cue_count': 0 if i < 3 else 48} for i in range(9)],
    }


class A05TStructureTests(unittest.TestCase):
    def test_control(self):
        self.assertEqual(gate.validate_report(fixture(), RAW)['blocks'], 9)

    def test_inspection_relabels_only_after_validation(self):
        with patch.object(gate.base, 'inspect_bytes', return_value=fixture()):
            result = gate.inspect_training_bytes(RAW)
        self.assertEqual(result['file'], 'A05T.mat')
        self.assertTrue(result['training_only'])
        self.assertFalse(result['class_label_values_inspected'])

    def test_reject_modified_bytes(self):
        with self.assertRaisesRegex(ValueError, 'source_sha256'):
            gate.validate_report(fixture(), RAW + b'changed')

    def test_reject_false_label_inspection(self):
        report = fixture()
        report['class_label_values_inspected'] = True
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_false_performance(self):
        report = fixture()
        report['decode_accuracy'] = 0.99
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_false_source_authentication(self):
        report = fixture()
        report['sha256_is_provider_authenticated'] = True
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_eval_session(self):
        report = fixture()
        report['session'] = 'E_evaluation'
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_wrong_blocks(self):
        report = fixture()
        report['block_metadata'].pop()
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_wrong_task_cues(self):
        report = fixture()
        report['block_metadata'][3]['cue_count'] = 47
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_wrong_channel_count(self):
        report = fixture()
        report['block_metadata'][5]['channels'] = 22
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_reordered_blocks(self):
        report = fixture()
        report['block_metadata'][2]['block_index_zero_based'] = 3
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_boolean_as_integer(self):
        report = fixture()
        report['blocks'] = True
        with self.assertRaises(ValueError):
            gate.validate_report(report, RAW)

    def test_reject_unapproved_host(self):
        with self.assertRaises(ValueError):
            gate.validate_url('https://example.com/database/data-sets/001-2014/A05T.mat')

    def test_reject_eval_filename(self):
        with self.assertRaises(ValueError):
            gate.validate_url('https://bnci-horizon-2020.eu/database/data-sets/001-2014/A05E.mat')

    def test_reject_url_credentials_and_query(self):
        for url in (
            'https://user@bnci-horizon-2020.eu/database/data-sets/001-2014/A05T.mat',
            gate.SOURCE + '?secret=1',
            gate.SOURCE + '#fragment',
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                gate.validate_url(url)

    def test_allowlisted_training_urls(self):
        gate.validate_url(gate.SOURCE)
        gate.validate_url('https://lampx.tugraz.at/~bci/database/001-2014/A05T.mat')


if __name__ == '__main__':
    unittest.main()
