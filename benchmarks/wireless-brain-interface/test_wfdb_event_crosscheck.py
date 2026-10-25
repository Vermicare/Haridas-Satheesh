"""Synthetic-only negative controls; real .event is fetched solely by CI."""
import hashlib
from types import SimpleNamespace
import unittest

from wfdb_event_crosscheck import CrossFormatError, compare_tal_to_wfdb, verify_event_digest, wfdb_events


def tal():
    labels = ['T0'] * 15 + ['T1'] * 8 + ['T2'] * 7
    return [{'label': label, 'onset_s': float(i), 'duration_s': 1.0} for i, label in enumerate(labels)]


def events():
    return [(t['label'], int(t['onset_s'] * 160), t['duration_s']) for t in tal()]


class CrossFormatTests(unittest.TestCase):
    def test_agreement(self):
        self.assertEqual(compare_tal_to_wfdb(tal(), events())['matched_events'], 30)

    def test_one_sample_tolerance(self):
        x = events()
        x[1] = (x[1][0], x[1][1] + 1, x[1][2])
        self.assertEqual(compare_tal_to_wfdb(tal(), x)['matched_events'], 30)

    def test_wrong_label(self):
        x = events()
        x[1] = ('T2', x[1][1], x[1][2])
        with self.assertRaises(CrossFormatError):
            compare_tal_to_wfdb(tal(), x)

    def test_wrong_time(self):
        x = events()
        x[1] = (x[1][0], x[1][1] + 2, x[1][2])
        with self.assertRaisesRegex(CrossFormatError, 'onset mismatch'):
            compare_tal_to_wfdb(tal(), x)

    def test_missing_event(self):
        with self.assertRaisesRegex(CrossFormatError, '29/30 discrepancy'):
            compare_tal_to_wfdb(tal(), events()[:-1])

    def test_bad_tal_nan(self):
        t = tal()
        t[0]['onset_s'] = float('nan')
        with self.assertRaisesRegex(CrossFormatError, 'invalid TAL'):
            compare_tal_to_wfdb(t, events())

    def test_valid_aux_note(self):
        ann = SimpleNamespace(sample=[0, 160], aux_note=['T0 duration: 1.0', 'T1 duration: 4.1'], symbol=['"', '"'])
        self.assertEqual(wfdb_events(ann), [('T0', 0, 1.0), ('T1', 160, 4.1)])

    def test_unknown_label(self):
        ann = SimpleNamespace(sample=[0], aux_note=['NOPE'], symbol=['"'])
        with self.assertRaisesRegex(CrossFormatError, 'unknown'):
            wfdb_events(ann)

    def test_duplicate_event(self):
        ann = SimpleNamespace(sample=[0, 0], aux_note=['T0 duration: 1.0', 'T0 duration: 1.0'], symbol=['"', '"'])
        with self.assertRaisesRegex(CrossFormatError, 'duplicate'):
            wfdb_events(ann)

    def test_unsorted_events(self):
        ann = SimpleNamespace(sample=[160, 0], aux_note=['T0 duration: 1.0', 'T1 duration: 4.1'], symbol=['"', '"'])
        with self.assertRaisesRegex(CrossFormatError, 'out-of-order'):
            wfdb_events(ann)

    def test_reject_negative_sample(self):
        ann = SimpleNamespace(sample=[-1], aux_note=['T0 duration: 1.0'], symbol=['"'])
        with self.assertRaisesRegex(CrossFormatError, 'negative'):
            wfdb_events(ann)

    def test_known_initial_rest_omission(self):
        t = tal()
        t[0]['duration_s'] = 4.2
        t[1]['onset_s'] = 4.2
        e = [(x['label'], round(x['onset_s'] * 160), x['duration_s']) for x in t[1:]]
        out = compare_tal_to_wfdb(t, e)
        self.assertEqual(out['matched_events'], 29)
        self.assertEqual(out['omitted_from_wfdb'], [t[0]])
        self.assertEqual(out['status'], 'RECONCILED_WITH_INITIAL_REST_OMISSION')

    def test_wrong_second_event_after_omission(self):
        t = tal()
        t[0]['duration_s'] = 4.2
        e = events()[1:]
        e[0] = ('T2', 672, 4.1)
        with self.assertRaises(CrossFormatError):
            compare_tal_to_wfdb(t, e)

    def test_duration_mismatch(self):
        x = events()
        x[1] = (x[1][0], x[1][1], x[1][2] + 0.1)
        with self.assertRaisesRegex(CrossFormatError, 'duration mismatch'):
            compare_tal_to_wfdb(tal(), x)

    def test_reject_malformed_duration_note(self):
        ann = SimpleNamespace(sample=[0], aux_note=['T0 duration: nan'], symbol=['"'])
        with self.assertRaisesRegex(CrossFormatError, 'unknown'):
            wfdb_events(ann)

    def test_checksum_mismatch(self):
        idx = hashlib.sha256(b'expected').hexdigest() + '  S001/S001R04.edf.event\n'
        with self.assertRaisesRegex(CrossFormatError, 'mismatch'):
            verify_event_digest(b'actual', idx)

    def test_checksum_match(self):
        idx = hashlib.sha256(b'expected').hexdigest() + '  S001/S001R04.edf.event\n'
        self.assertEqual(verify_event_digest(b'expected', idx), hashlib.sha256(b'expected').hexdigest())


if __name__ == '__main__':
    unittest.main()
