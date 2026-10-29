"""Fictional, deterministic contract tests. No human EEG is loaded."""
import json
import unittest
from zhou2020_bids_channel_gate_v01 import COMMON, EXTRA, inspect_text

META = json.dumps({'Version': '1.1.0', 'DatasetType': 'derivative'})


def fixture(subject):
    pairs = ([(n, 'EEG') for n in COMMON + EXTRA] +
             [('hEOG', 'EOG'), ('vEOG', 'EOG'), ('M1', 'MISC'), ('M2', 'MISC')]
             if subject <= 12 else
             [(n, 'EEG') for n in COMMON] + [('hEOG', 'EOG'), ('vEOG', 'EOG')])
    return 'name\ttype\tsampling_frequency\n' + ''.join(f'{n}\t{t}\t500.0\n' for n, t in pairs)


class GateTests(unittest.TestCase):
    def gate(self, subject, text=None, meta=META):
        return inspect_text(meta, fixture(subject) if text is None else text,
                            f'sub-{subject}_ses-1_task-imagery_run-0_channels.tsv')

    def test_s_cohort(self):
        self.assertEqual(self.gate(1)['channels'], 45)

    def test_a_cohort(self):
        self.assertEqual(self.gate(13)['channels'], 28)

    def test_old_version_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Version'):
            self.gate(1, meta=json.dumps({'Version': '1.0.3', 'DatasetType': 'derivative'}))

    def test_generic_eeg_rejected(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.gate(1, fixture(1).replace('F3\tEEG', 'EEG1\tEEG'))

    def test_eog_mislabeled_rejected(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.gate(1, fixture(1).replace('hEOG\tEOG', 'hEOG\tEEG'))

    def test_missing_electrode_rejected(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.gate(1, fixture(1).replace('POz\tEEG\t500.0\n', ''))

    def test_wrong_order_rejected(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.gate(1, fixture(1).replace('F3\tEEG\t500.0\nF1\tEEG\t500.0\n', 'F1\tEEG\t500.0\nF3\tEEG\t500.0\n'))

    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.gate(13, fixture(13).replace('F1\tEEG\t500.0\n', 'F3\tEEG\t500.0\n'))

    def test_wrong_sampling_rejected(self):
        with self.assertRaisesRegex(ValueError, 'sampling'):
            self.gate(13, fixture(13).replace('500.0', '250.0'))

    def test_outside_cohort_rejected(self):
        with self.assertRaisesRegex(ValueError, 'cohort'):
            self.gate(21)

    def test_missing_column_rejected(self):
        with self.assertRaisesRegex(ValueError, 'required'):
            self.gate(13, fixture(13).replace('sampling_frequency', 'freq'))

    def test_wrong_derivative_rejected(self):
        with self.assertRaisesRegex(ValueError, 'derivative'):
            self.gate(13, meta=json.dumps({'Version': '1.1.0', 'DatasetType': 'raw'}))


if __name__ == '__main__':
    unittest.main()
