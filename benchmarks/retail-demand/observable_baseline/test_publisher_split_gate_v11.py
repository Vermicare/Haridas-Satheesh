"""Fictional date-only negative controls for publisher train/eval split gate."""
import datetime as dt
import json
import unittest
from publisher_split_gate_v11 import SplitError, validate_publisher_split, demo


def dates():
    start = dt.date(2025, 1, 1)
    return [(start + dt.timedelta(days=i)).isoformat() for i in range(97)]


class PublisherSplitGateTests(unittest.TestCase):
    def test_valid_fictional_90_plus_7(self):
        d = dates()
        result = validate_publisher_split(d[:90], d[90:], fitted_dates=d[:90])
        self.assertEqual((result['train_days'], result['eval_days']), (90, 7))
        self.assertFalse(result['publisher_parquet_verified'])
        self.assertFalse(result['fit_feature_leakage_excluded'])
        self.assertTrue(result['fit_date_boundary_checked'])

    def test_fit_provenance_unknown_stays_unknown(self):
        d = dates()
        self.assertFalse(validate_publisher_split(d[:90], d[90:])['fit_date_boundary_checked'])

    def test_reject_train_short_or_eval_short(self):
        d = dates()
        for tr, ev in ((d[:89], d[90:]), (d[:90], d[90:96])):
            with self.subTest(tr=len(tr), ev=len(ev)), self.assertRaisesRegex(SplitError, 'exactly'):
                validate_publisher_split(tr, ev)

    def test_reject_overlapping_split(self):
        d = dates()
        with self.assertRaisesRegex(SplitError, 'overlap or gap'):
            validate_publisher_split(d[:90], d[89:96])

    def test_reject_gap_between_train_and_eval(self):
        d = dates()
        with self.assertRaisesRegex(SplitError, 'overlap or gap'):
            validate_publisher_split(d[:90], [
                (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat() for day in d[90:97]])

    def test_reject_gap_within_train(self):
        d = dates()
        d[50] = '2025-02-22'
        with self.assertRaisesRegex(SplitError, 'consecutive'):
            validate_publisher_split(d[:90], d[90:])

    def test_reject_unsorted_eval(self):
        d = dates()
        ev = d[90:]
        ev[1], ev[2] = ev[2], ev[1]
        with self.assertRaisesRegex(SplitError, 'consecutive'):
            validate_publisher_split(d[:90], ev)

    def test_reject_invalid_date_types_and_suffixes(self):
        d = dates()
        for bad in (True, 123, '2025-01-01T12:00:00', '2025-02-30', '2025-1-1'):
            tr = d[:90]
            tr[0] = bad
            with self.subTest(bad=bad), self.assertRaises(SplitError):
                validate_publisher_split(tr, d[90:])

    def test_reject_fit_on_heldout_eval_day(self):
        d = dates()
        with self.assertRaisesRegex(SplitError, 'outside official training'):
            validate_publisher_split(d[:90], d[90:], fitted_dates=[d[89], d[90]])

    def test_reject_fit_on_date_before_train(self):
        d = dates()
        with self.assertRaisesRegex(SplitError, 'outside official training'):
            validate_publisher_split(d[:90], d[90:], fitted_dates=['2024-12-31'])

    def test_reject_malformed_fit_provenance(self):
        d = dates()
        for bad in (None, True, '2025-01-01T01:00:00', '2025-02-30'):
            with self.subTest(bad=bad), self.assertRaises(SplitError):
                validate_publisher_split(d[:90], d[90:], fitted_dates=[bad])

    def test_demo_deterministic(self):
        self.assertEqual(demo(), demo())
        result = json.loads(demo())
        self.assertEqual(result['public_data_scores'], 'TBD')


if __name__ == '__main__':
    unittest.main()
