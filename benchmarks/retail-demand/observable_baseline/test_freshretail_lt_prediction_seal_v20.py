"""Fictional-only negative controls for the TRAIN-only v2.0 prediction seal."""
import datetime as dt
import math
import random
import unittest

import freshretail_lt_prediction_seal_v20 as v20


def rows(key=(1, 2), n=90, start=dt.date(2025, 4, 15), value=0.25):
    return [{'store_id': key[0], 'product_id': key[1],
             'dt': (start + dt.timedelta(days=i)).isoformat(),
             'hours_sale': [value] * 24,
             'hours_stock_status': [0] * 24,
             'stock_hour6_22_cnt': 0} for i in range(n)]


class TrainOnlySealV20Tests(unittest.TestCase):
    def setUp(self):
        self.sample = rows()
        self.selected = ((1, 2),)

    def test_training_cohort_matches_explicit_fictional_digest(self):
        expected = v20.cohort_digest(self.selected)
        keys, report = v20.training_cohort(self.sample, size=1, expected_digest=expected)
        self.assertEqual(keys, self.selected)
        self.assertEqual(report['eligible_complete_valid_series'], 1)
        self.assertEqual(report['duplicate_training_rows'], 0)

    def test_training_cohort_rejects_future_date(self):
        with self.assertRaises(v20.SealError):
            v20.training_cohort(self.sample + rows(start=dt.date(2025, 7, 14), n=1),
                                size=1, expected_digest=v20.cohort_digest(self.selected))

    def test_training_cohort_rejects_wrong_fingerprint(self):
        with self.assertRaisesRegex(v20.SealError, 'fingerprint'):
            v20.training_cohort(self.sample, size=1, expected_digest='0'*64)

    def test_training_cohort_does_not_repair_duplicate(self):
        with self.assertRaisesRegex(v20.SealError, 'insufficient'):
            v20.training_cohort(self.sample + [dict(self.sample[0])], size=1,
                                expected_digest=v20.cohort_digest(self.selected))

    def test_training_cohort_rejects_invalid_stock_flag(self):
        sample = rows()
        sample[0]['hours_stock_status'] = [2]*24
        with self.assertRaisesRegex(v20.SealError, 'insufficient'):
            v20.training_cohort(sample, size=1,
                                expected_digest=v20.cohort_digest(self.selected))

    def test_seal_four_models_and_seven_future_days(self):
        result = v20.sealed_predictions(self.selected, self.sample)
        self.assertEqual(result['predicted_days'], 7)
        self.assertEqual(len(result['models']), 4)
        self.assertEqual(result['forecast_dates'], ['2025-07-14','2025-07-15','2025-07-16',
                                                     '2025-07-17','2025-07-18','2025-07-19','2025-07-20'])
        self.assertFalse(result['evaluation_labels_read'])
        self.assertNotIn('store_id', result)
        self.assertNotIn('product_id', result)

    def test_seal_deterministic_under_training_row_shuffle(self):
        shuffled = list(self.sample)
        random.Random(1234).shuffle(shuffled)
        self.assertEqual(v20.sealed_predictions(self.selected, self.sample)['prediction_sha256'],
                         v20.sealed_predictions(self.selected, shuffled)['prediction_sha256'])

    def test_seal_rejects_missing_training_day(self):
        with self.assertRaisesRegex(v20.SealError, 'missing or duplicate'):
            v20.sealed_predictions(self.selected, self.sample[:-1])

    def test_seal_rejects_duplicate_training_day(self):
        with self.assertRaisesRegex(v20.SealError, 'missing or duplicate'):
            v20.sealed_predictions(self.selected, self.sample + [dict(self.sample[-1])])

    def test_seal_rejects_noncohort_row(self):
        with self.assertRaisesRegex(v20.SealError, 'noncohort'):
            v20.sealed_predictions(self.selected, self.sample + rows(key=(3, 4), n=1))

    def test_seal_rejects_future_training_row(self):
        with self.assertRaisesRegex(v20.SealError, 'outside frozen history'):
            v20.sealed_predictions(self.selected, self.sample + rows(n=1, start=dt.date(2025, 7, 14)))

    def test_seal_rejects_negative_sale(self):
        sample = rows()
        sample[0]['hours_sale'][8] = -0.5
        with self.assertRaises(ValueError):
            v20.sealed_predictions(self.selected, sample)

    def test_seal_rejects_nonfinite_sale(self):
        sample = rows()
        sample[0]['hours_sale'][8] = math.inf
        with self.assertRaises(ValueError):
            v20.sealed_predictions(self.selected, sample)

    def test_seal_rejects_ambiguous_selected_cohort(self):
        with self.assertRaisesRegex(v20.SealError, 'invalid frozen cohort'):
            v20.sealed_predictions(((1, 2), (1, 2)), self.sample)

    def test_no_future_label_input_in_seal_interface(self):
        self.assertEqual(v20.sealed_predictions.__code__.co_argcount, 2)
        result = v20.sealed_predictions(self.selected, self.sample)
        self.assertEqual(result['forecast_accuracy'], 'TBD')
        self.assertFalse(result['evaluation_file_opened'])


if __name__ == '__main__':
    unittest.main()
