"""Fictional controls for a publisher-data evaluation contract; no real scores."""
import copy
import datetime as dt
import unittest
from official_holdout_v12 import (select_train_only, evaluate_cohort,
                                   bootstrap_macro_delta, SAMPLE_SEED)
from retail_gate import EvidenceError, forecast_at_origin, parse_row


def fixture(censored_eval=()):
    start = dt.date(2024, 3, 28)
    def row(i, key=(1, 2), censored=False):
        status = [0]*24
        if censored: status[8] = 1
        return {'store_id': key[0], 'product_id': key[1],
                'dt': (start+dt.timedelta(days=i)).isoformat(),
                'hours_sale': [1.0]*24, 'hours_stock_status': status,
                'stock_hour6_22_cnt': int(censored)}
    return [row(i, censored=i%5==0) for i in range(90)], [row(i, censored=i-90 in censored_eval) for i in range(90, 97)]


class OfficialHoldoutTests(unittest.TestCase):
    def test_deterministic_train_only_cohort(self):
        keys = [(i, i*3) for i in range(100)]
        selected = select_train_only(keys, 8)
        self.assertEqual(selected, select_train_only(reversed(keys), 8))
        self.assertEqual(len(selected), 8)
        self.assertTrue(SAMPLE_SEED)

    def test_holdout_scoring_and_censoring(self):
        train, evaluation = fixture((1, 3))
        result = evaluate_cohort([(1, 2)], train, evaluation)
        self.assertEqual(result['uncensored_eval_days_scored'], 5)
        self.assertEqual(result['censored_eval_days_excluded'], 2)
        self.assertEqual(result['series_with_at_least_one_uncensored_eval_day'], 1)
        self.assertIn('seasonal_naive', result['day_weighted_mae'])

    def test_eval_labels_cannot_enter_predictions(self):
        train, evaluation = fixture()
        altered = copy.deepcopy(evaluation)
        for row in altered: row['hours_sale'][6] = 99.0
        to_parsed = lambda rows: [parse_row(r, i) for i, r in enumerate(rows)]
        self.assertEqual(forecast_at_origin(to_parsed(train+evaluation), 90),
                         forecast_at_origin(to_parsed(train+altered), 90))
        first = evaluate_cohort([(1, 2)], train, evaluation)
        second = evaluate_cohort([(1, 2)], train, altered)
        self.assertNotEqual(first['day_weighted_mae'], second['day_weighted_mae'])
        self.assertEqual(first['frozen_train_selected_series'], second['frozen_train_selected_series'])

    def test_missing_eval_day_aborts_not_replaces(self):
        train, evaluation = fixture()
        with self.assertRaises(EvidenceError): evaluate_cohort([(1, 2)], train, evaluation[:-1])

    def test_duplicate_train_day_aborts(self):
        train, evaluation = fixture()
        train[3] = copy.deepcopy(train[2])
        with self.assertRaises(EvidenceError): evaluate_cohort([(1, 2)], train, evaluation)

    def test_noncohort_row_aborts(self):
        train, evaluation = fixture()
        train[0]['store_id'] = 99
        with self.assertRaises(EvidenceError): evaluate_cohort([(1, 2)], train, evaluation)

    def test_all_censored_aborts(self):
        train, evaluation = fixture(tuple(range(7)))
        with self.assertRaises(EvidenceError): evaluate_cohort([(1, 2)], train, evaluation)

    def test_wrong_calendar_aborts(self):
        train, evaluation = fixture()
        for row in train+evaluation:
            row['dt'] = (dt.date.fromisoformat(row['dt'])+dt.timedelta(days=1)).isoformat()
        with self.assertRaises(EvidenceError): evaluate_cohort([(1, 2)], train, evaluation)

    def test_bootstrap_determinism(self):
        self.assertEqual(bootstrap_macro_delta([0.1, -0.2, 0.3], reps=100),
                         bootstrap_macro_delta([0.1, -0.2, 0.3], reps=100))

    def test_bad_ids_fail(self):
        with self.assertRaises(EvidenceError): select_train_only([(True, 2)], 1)
        with self.assertRaises(EvidenceError): select_train_only([(1, 2)], 2)


if __name__ == '__main__': unittest.main()
