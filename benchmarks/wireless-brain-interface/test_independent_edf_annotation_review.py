"""Fictional negative controls for the independent event comparator (no EEG data)."""
import unittest
from independent_edf_annotation_review import compare_events, AgreementError


def ev(label='T0', onset=0.0, duration=1.0):
    return {'label': label, 'onset_s': onset, 'duration_s': duration}


class IndependentAgreementContractTests(unittest.TestCase):
    def test_agreement(self):
        out = compare_events([ev('T0', 0), ev('T1', 1)], [ev('T1', 1), ev('T0', 0)])
        self.assertEqual(out['counts'], {'T0': 1, 'T1': 1})
        self.assertEqual(out['total_events'], 2)

    def test_within_predeclared_tolerance(self):
        self.assertEqual(compare_events([ev()], [ev(onset=0.00009)])['total_events'], 1)

    def test_event_count_mismatch(self):
        with self.assertRaisesRegex(AgreementError, 'count mismatch'):
            compare_events([ev()], [ev(), ev('T1', 1)])

    def test_same_total_wrong_labels(self):
        with self.assertRaisesRegex(AgreementError, 'label-count mismatch'):
            compare_events([ev()], [ev('T2')])

    def test_same_count_wrong_onset(self):
        with self.assertRaisesRegex(AgreementError, 'timing mismatch'):
            compare_events([ev()], [ev(onset=0.01)])

    def test_same_count_wrong_duration(self):
        with self.assertRaisesRegex(AgreementError, 'timing mismatch'):
            compare_events([ev()], [ev(duration=1.01)])

    def test_reject_duplicate(self):
        with self.assertRaisesRegex(AgreementError, 'duplicate'):
            compare_events([ev(), ev()], [ev(), ev()])

    def test_reject_unknown_label(self):
        with self.assertRaisesRegex(AgreementError, 'unknown'):
            compare_events([ev('T9')], [ev('T9')])

    def test_reject_nan(self):
        with self.assertRaisesRegex(AgreementError, 'invalid event timing'):
            compare_events([ev(onset=float('nan'))], [ev()])

    def test_reject_boolean_duration(self):
        with self.assertRaisesRegex(AgreementError, 'nonnumeric'):
            compare_events([ev(duration=True)], [ev()])

    def test_reject_missing_field(self):
        with self.assertRaisesRegex(AgreementError, 'malformed'):
            compare_events([{'label': 'T0', 'onset_s': 0}], [ev()])

    def test_reject_zero_duration(self):
        with self.assertRaisesRegex(AgreementError, 'invalid'):
            compare_events([ev(duration=0)], [ev()])


if __name__ == '__main__':
    unittest.main()
