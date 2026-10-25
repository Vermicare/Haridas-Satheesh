import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from retail_gate import (EvidenceError, benchmark, corrected_training_history, evaluate,
                         parse_row, read_jsonl, select_series, forecast_at_origin)


def fake(i=0, **kw):
    status = [0]*24
    if i % 5 == 0:
        status[11] = 1
    x = {'store_id': 1, 'product_id': 2, 'dt': (dt.date(2024, 1, 1)+dt.timedelta(days=i)).isoformat(),
         'hours_sale': [0.0]*24, 'hours_stock_status': status,
         'stock_hour6_22_cnt': sum(status[6:22])}
    x['hours_sale'][8] = float(1 + i % 7)
    x.update(kw)
    return x


class SchemaTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_row(fake(), 1)['stockout_hours'], 1)
    def test_24_hours(self):
        with self.assertRaises(EvidenceError): parse_row(fake(hours_sale=[1.0]*23), 1)
    def test_count_mismatch(self):
        with self.assertRaises(EvidenceError): parse_row(fake(stock_hour6_22_cnt=0), 1)
    def test_negative_sales(self):
        with self.assertRaises(EvidenceError): parse_row(fake(hours_sale=[-1.0]*24), 1)
    def test_status_bool_invalid(self):
        with self.assertRaises(EvidenceError): parse_row(fake(hours_stock_status=[False]*24), 1)
    def test_status_22_excluded(self):
        s = [0]*24; s[22]=1
        self.assertEqual(parse_row(fake(hours_stock_status=s,stock_hour6_22_cnt=0), 1)['stockout_hours'], 0)
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.jsonl';p.write_text(json.dumps(fake())+'\n'+json.dumps(fake())+'\n')
            with self.assertRaisesRegex(EvidenceError,'duplicate'):read_jsonl(p)
    def test_empty_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.jsonl';p.write_text('')
            with self.assertRaisesRegex(EvidenceError,'empty'):read_jsonl(p)
    def test_bad_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.jsonl';p.write_text('{not json}\n')
            with self.assertRaisesRegex(EvidenceError,'malformed'):read_jsonl(p)


class CausalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = Path(self.temp.name)/'fictional.jsonl'
        self.fixture.write_text(''.join(json.dumps(fake(i), sort_keys=True)+'\n' for i in range(84)))
        self.key, self.rows = select_series(read_jsonl(self.fixture))
    def test_selection(self):
        self.assertEqual(self.key, ('1','2'))
    def test_three_chronological_folds(self):
        folds=evaluate(self.rows)
        self.assertEqual(len(folds),3)
        for f in folds:self.assertLess(f['train_last_date'],f['origin_date'])
    def test_future_perturbation_invariance(self):
        a=corrected_training_history(self.rows,42)
        self.rows[45]['y']=10**9
        self.rows[45]['censored']=False
        self.assertEqual(a,corrected_training_history(self.rows,42))
    def test_forecasts_unchanged_when_test_values_corrupted(self):
        before=forecast_at_origin(self.rows,42)
        for i in range(42,49):
            self.rows[i]['y']=10**9
            self.rows[i]['censored']=True
        self.assertEqual(before,forecast_at_origin(self.rows,42))
    def test_future_stockout_cannot_affect_selection(self):
        self.rows[80]['censored']=not self.rows[80]['censored']
        self.assertEqual(select_series({('1','2'):self.rows})[0],('1','2'))
    def test_no_latent_truth_scored(self):
        r=evaluate(self.rows)
        for f in r:
            self.assertEqual(f['uncensored_test_days']+f['censored_test_days_excluded_from_latent_truth_scoring'],7)
            self.assertEqual(f['models']['seasonal_naive']['evaluated_days'],f['uncensored_test_days'])
    def test_zero_valid_days_null_mae(self):
        for i in range(42,49):self.rows[i]['censored']=True
        self.assertIsNone(evaluate(self.rows)[0]['models']['seasonal_naive']['mae_uncensored_only'])
    def test_gap_fail_closed(self):
        self.rows[25]['day']+=dt.timedelta(days=2)
        with self.assertRaises(EvidenceError):select_series({('1','2'):self.rows})
    def test_no_post_selection_on_future_coverage(self):
        other = [dict(r) for r in self.rows]
        for r in other: r['key']=('9','9')
        self.rows[60]['day']+=dt.timedelta(days=1)
        with self.assertRaisesRegex(EvidenceError,'preselected cohort'):
            select_series({('1','2'):self.rows,('9','9'):other})
    def test_external_provenance_required(self):
        with self.assertRaisesRegex(EvidenceError,'requires'):benchmark(self.fixture)
    def test_checksum_rejected(self):
        with self.assertRaisesRegex(EvidenceError,'checksum'):benchmark(self.fixture,'0'*64,'https://example.org')
    def test_fictional_report_labels(self):
        r=benchmark(self.fixture,synthetic=True)
        self.assertEqual(r['data_kind'],'FICTIONAL_TEST_ONLY')
        self.assertEqual(r['latent_demand_ground_truth'],'UNAVAILABLE')
    def test_result_deterministic(self):
        self.assertEqual(benchmark(self.fixture,synthetic=True),benchmark(self.fixture,synthetic=True))

if __name__=='__main__':unittest.main()
