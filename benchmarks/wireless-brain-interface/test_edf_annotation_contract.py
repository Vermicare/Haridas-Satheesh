"""Synthetic EDF+ annotation fixtures; passing tests do not validate real EEG."""
import hashlib
import unittest
from edf_smoke import SmokeError
from edf_annotation_contract import extract_annotations, parse_tal, validate_and_summarize
from test_edf_smoke import fictional_edf


def with_tals(*tals):
    edf = bytearray(fictional_edf())
    ann_samples = 64
    start = len(edf) - ann_samples * 2
    payload = b'\x00'.join(tals) + b'\x00'
    if len(payload) > ann_samples:
        raise ValueError('too many TAL bytes')
    for i, value in enumerate(payload):
        edf[start + 2 * i] = value
    return bytes(edf)


class EDFAnnotationContractTests(unittest.TestCase):
    def test_valid_task_and_timekeeping(self):
        edf = with_tals(b'+0\x14\x14', b'+0.1\x150.2\x14T1\x14', b'+0.4\x150.2\x14T2\x14')
        r = extract_annotations(edf)
        self.assertEqual(r['event_counts'], {'T1': 1, 'T2': 1})
        self.assertEqual(r['timekeeping_records'], 1)
        self.assertFalse(r['raw_eeg_samples_decoded'])

    def test_integrity_bound_to_same_bytes(self):
        edf = with_tals(b'+0\x14\x14', b'+0.1\x150.2\x14T1\x14')
        digest = hashlib.sha256(edf).hexdigest()
        r = validate_and_summarize(edf, digest + '  S001/S001R04.edf\n')
        self.assertEqual(r['annotations']['event_counts'], {'T1': 1})
        self.assertFalse(r['decoder_trained'])

    def test_unknown_task_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'unknown'):
            extract_annotations(with_tals(b'+0.1\x150.2\x14T3\x14'))

    def test_out_of_bounds_event_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'exceeds'):
            extract_annotations(with_tals(b'+0.9\x150.2\x14T1\x14'))

    def test_event_without_duration_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'missing duration'):
            extract_annotations(with_tals(b'+0.1\x14T1\x14'))

    def test_missing_events_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'no task events'):
            extract_annotations(with_tals(b'+0\x14\x14'))

    def test_malformed_tal_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'separator'):
            parse_tal(b'+1T1')

    def test_nonfinite_onset_rejected(self):
        with self.assertRaisesRegex(SmokeError, 'onset'):
            parse_tal(b'+nan\x14T1\x14')

    def test_corrupt_high_byte_rejected(self):
        edf = bytearray(with_tals(b'+0.1\x150.2\x14T1\x14'))
        edf[-127] = 1
        with self.assertRaisesRegex(SmokeError, 'high bytes'):
            extract_annotations(bytes(edf))

    def test_duplicate_labels_same_tal_are_counted(self):
        edf = with_tals(b'+0.1\x150.2\x14T1\x14T1\x14')
        self.assertEqual(extract_annotations(edf)['event_counts']['T1'], 2)


if __name__ == '__main__':
    unittest.main()
