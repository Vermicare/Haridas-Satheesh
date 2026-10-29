"""Fictional-only adversarial tests for the prospective A01E baseline.

No public EEG is loaded by these tests; no clinical or safety claims.
"""
import copy
import hashlib
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

import bnci_a01e_temporal_baseline_v12 as m


def fake_probs():
    y = np.tile(np.arange(1, 5), 72).astype(int)
    p = np.full((288, 4), 0.025, dtype=float)
    pred = y.copy()
    pred[:12] = (pred[:12] % 4) + 1
    p[np.arange(288), pred - 1] = 0.925
    return p, y


class TestEUrl(unittest.TestCase):
    def test_allowlist(self):
        m.validate_e_url(m.E_URL)
        m.validate_e_url('https://lampx.tugraz.at/~bci/database/001-2014/A01E.mat')

    def test_reject_http(self):
        with self.assertRaises(ValueError):
            m.validate_e_url(m.E_URL.replace('https:', 'http:'))

    def test_reject_other_subject(self):
        with self.assertRaises(ValueError):
            m.validate_e_url(m.E_URL.replace('A01E', 'A02E'))

    def test_reject_query(self):
        with self.assertRaises(ValueError):
            m.validate_e_url(m.E_URL + '?token=abc')

    def test_reject_host_confusion(self):
        with self.assertRaises(ValueError):
            m.validate_e_url('https://bnci-horizon-2020.eu.evil.test/database/data-sets/001-2014/A01E.mat')

    def test_source_pin_accepts_exact_fictional_bytes(self):
        raw = b'MATLAB 5.0 MAT-file' + b'x' * 256
        with patch.object(m, 'PINNED_E_BYTES', len(raw)):
            with patch.object(m, 'PINNED_E_SHA256', hashlib.sha256(raw).hexdigest()):
                m.verify_e_source_identity(raw)

    def test_source_pin_rejects_one_byte_mutation(self):
        raw = b'MATLAB 5.0 MAT-file' + b'x' * 256
        changed = raw[:-1] + b'y'
        with patch.object(m, 'PINNED_E_BYTES', len(raw)):
            with patch.object(m, 'PINNED_E_SHA256', hashlib.sha256(raw).hexdigest()):
                with self.assertRaisesRegex(ValueError, 'SHA-256 changed'):
                    m.verify_e_source_identity(changed)


class TestScore(unittest.TestCase):
    def setUp(self):
        self.p, self.y = fake_probs()
        self.t = {'0.30': 0.8, '0.50': 0.8, '0.70': 0.8}

    def test_known_negative_control(self):
        r = m.score_e(self.p, self.y, self.t)
        self.assertEqual((r['trials'], r['correct_n']), (288, 276))
        self.assertAlmostEqual(r['accuracy'], 276 / 288)
        for row in r['confidence_only_abstention'].values():
            self.assertEqual((row['acted_n'], row['incorrect_acted_n']), (288, 12))

    def test_no_action_safe_denominator(self):
        r = m.score_e(self.p, self.y, {k: 0.99 for k in m.TARGETS})
        for row in r['confidence_only_abstention'].values():
            self.assertEqual(row['acted_n'], 0)
            self.assertIsNone(row['incorrect_action_risk'])

    def test_reject_nonfinite_probability(self):
        p = self.p.copy()
        p[0, 0] = np.nan
        with self.assertRaises(ValueError):
            m.score_e(p, self.y, self.t)

    def test_reject_non_normalized_probability(self):
        p = self.p.copy()
        p[0, 0] = 0.5
        with self.assertRaises(ValueError):
            m.score_e(p, self.y, self.t)

    def test_reject_wrong_trial_count(self):
        with self.assertRaises(ValueError):
            m.score_e(self.p[:287], self.y[:287], self.t)

    def test_reject_invalid_class(self):
        y = self.y.copy()
        y[0] = 5
        with self.assertRaises(ValueError):
            m.score_e(self.p, y, self.t)

    def test_reject_missing_frozen_threshold(self):
        with self.assertRaises(ValueError):
            m.score_e(self.p, self.y, {'0.30': 0.8})

    def test_reject_invalid_threshold(self):
        t = self.t.copy()
        t['0.70'] = float('nan')
        with self.assertRaises(ValueError):
            m.score_e(self.p, self.y, t)


class TestLabelFirewall(unittest.TestCase):
    def test_absent_labels_remain_unavailable(self):
        blocks = [SimpleNamespace(y=np.array([], dtype=int)) for _ in range(3)]
        blocks += [SimpleNamespace() for _ in range(6)]
        labels, flags = m.extract_e_labels_after_prediction(blocks)
        self.assertIsNone(labels)
        self.assertIsNone(flags)

    def test_invalid_labels_fail_closed(self):
        blocks = [SimpleNamespace() for _ in range(3)]
        blocks += [SimpleNamespace(y=np.full(48, 0)) for _ in range(6)]
        with self.assertRaises(ValueError):
            m.extract_e_labels_after_prediction(blocks)

    def test_valid_labels_and_flags(self):
        blocks = [SimpleNamespace() for _ in range(3)]
        blocks += [SimpleNamespace(y=np.tile(np.arange(1, 5), 12),
                                   artifacts=np.zeros(48)) for _ in range(6)]
        labels, flags = m.extract_e_labels_after_prediction(blocks)
        self.assertEqual((labels.shape, flags.shape), ((288,), (288,)))
        self.assertEqual(int(flags.sum()), 0)

    def test_invalid_artifact_flag_fails(self):
        blocks = [SimpleNamespace() for _ in range(3)]
        blocks += [SimpleNamespace(y=np.tile(np.arange(1, 5), 12),
                                   artifacts=np.zeros(48)) for _ in range(6)]
        blocks[4].artifacts[0] = 2
        with self.assertRaises(ValueError):
            m.extract_e_labels_after_prediction(blocks)

    def test_bad_T_identity_stops_before_E_fetch(self):
        with patch.object(m, 'check_frozen_training_blob', side_effect=ValueError('changed')):
            with patch.object(m, 'fetch_e_bytes') as fetch_e:
                with self.assertRaisesRegex(ValueError, 'changed'):
                    m.run()
                fetch_e.assert_not_called()

    def test_wrong_E_structure_rejected(self):
        with self.assertRaises(ValueError):
            m.extract_e_features_unlabeled([SimpleNamespace()] * 8)


if __name__ == '__main__':
    unittest.main()
