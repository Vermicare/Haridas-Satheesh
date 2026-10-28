"""Fictional-only pinned-reacquisition adversarial contract tests."""
import hashlib
import unittest

from bnci_a04t_reacquire_v06 import ReacquisitionError, verify_reacquisition

RAW = b'FICTIONAL_A04T_BYTES_FOR_TESTS'
SHA = hashlib.sha256(RAW).hexdigest()


def valid_report(raw):
    return {
        'file': 'A04T.mat', 'source_sha256': hashlib.sha256(raw).hexdigest(),
        'source_bytes': len(raw), 'blocks': 7,
        'cue_free_baseline_blocks': 1, 'cued_task_blocks': 6, 'cues_total': 288,
        'sha256_is_provider_authenticated': False,
        'class_label_values_inspected': False,
        'raw_eeg_persisted_or_uploaded': False,
        'evaluation_session_or_labels_accessed': False,
        'a04t_eog_exception_allowed': True,
        'decode_accuracy': 'TBD', 'false_action_risk': 'TBD',
    }


class ReacquisitionTests(unittest.TestCase):
    def check(self, raw=RAW, inspect=valid_report, *, size=len(RAW), digest=SHA):
        return verify_reacquisition(raw, inspect, expected_size=size,
                                    expected_sha256=digest)

    def test_fictional_matching_bytes_remain_nonclinical(self):
        result = self.check()
        self.assertTrue(result['previous_observation_sha256_matched'])
        self.assertFalse(result['publisher_signature_authenticated'])
        self.assertFalse(result['maturity_advanced'])
        self.assertEqual(result['decoder_or_authorization_performance'], 'TBD')

    def test_changed_bytes_same_length_fail_before_inspection(self):
        def forbidden(_):
            self.fail('inspector must not run on mismatched source')
        with self.assertRaisesRegex(ReacquisitionError, 'SHA-256'):
            self.check(RAW[:-1] + b'X', forbidden)

    def test_truncated_source_fails(self):
        with self.assertRaisesRegex(ReacquisitionError, 'byte count'):
            self.check(RAW[:-1])

    def test_nonbytes_source_fails(self):
        with self.assertRaises(ReacquisitionError):
            self.check(bytearray(RAW))

    def test_wrong_inspector_digest_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'source_sha256': '0' * 64}
        with self.assertRaisesRegex(ReacquisitionError, 'source_sha256'):
            self.check(inspect=inspect)

    def test_exception_block_count_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'blocks': 9}
        with self.assertRaisesRegex(ReacquisitionError, 'blocks'):
            self.check(inspect=inspect)

    def test_baseline_count_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'cue_free_baseline_blocks': 3}
        with self.assertRaisesRegex(ReacquisitionError, 'cue_free_baseline_blocks'):
            self.check(inspect=inspect)

    def test_label_access_claim_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'class_label_values_inspected': True}
        with self.assertRaisesRegex(ReacquisitionError, 'class_label_values_inspected'):
            self.check(inspect=inspect)

    def test_evaluation_access_claim_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'evaluation_session_or_labels_accessed': True}
        with self.assertRaisesRegex(ReacquisitionError, 'evaluation_session_or_labels_accessed'):
            self.check(inspect=inspect)

    def test_fabricated_accuracy_claim_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'decode_accuracy': 0.9}
        with self.assertRaisesRegex(ReacquisitionError, 'decode_accuracy'):
            self.check(inspect=inspect)

    def test_missing_inspector_field_fails(self):
        def inspect(raw):
            r = valid_report(raw)
            del r['raw_eeg_persisted_or_uploaded']
            return r
        with self.assertRaisesRegex(ReacquisitionError, 'raw_eeg_persisted_or_uploaded'):
            self.check(inspect=inspect)

    def test_boolean_in_integer_count_fails(self):
        def inspect(raw):
            return {**valid_report(raw), 'cues_total': True}
        with self.assertRaisesRegex(ReacquisitionError, 'cues_total'):
            self.check(inspect=inspect)

    def test_malformed_inspector_result_fails(self):
        with self.assertRaisesRegex(ReacquisitionError, 'invalid report'):
            self.check(inspect=lambda _: [])


if __name__ == '__main__':
    unittest.main()
