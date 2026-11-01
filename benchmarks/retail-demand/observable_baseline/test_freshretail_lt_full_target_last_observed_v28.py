"""15 fictional-only controls; never opens publisher source or EVAL labels."""
import csv,datetime as dt,hashlib,io,unittest
from freshretail_lt_full_target_last_observed_v28 import FullTargetError,historical,forecast

def tr(a,b,d,q): return {'store_id':a,'product_id':b,'dt':d,'sale_amount':q}
def tg(a,b,d): return {'store_id':a,'product_id':b,'dt':d}
class FullTargetTests(unittest.TestCase):
    def setUp(self):
        self.rows=[tr(1,2,'2025-07-12',1.25),tr(1,2,'2025-07-13',2.5),tr(2,3,'2025-07-13',4)]
        self.keys=[tg(2,3,'2025-07-14'),tg(1,2,dt.date(2025,7,15)),tg(9,9,'2025-07-16')]
    def test_last_and_fallback(self):
        last,n=historical(self.rows,3); raw,r=forecast(last,self.keys,3)
        self.assertEqual(n,3)
        self.assertEqual([x['prediction'] for x in csv.DictReader(io.StringIO(raw.decode()))],['2.5','4','0'])
        self.assertEqual(r['zero_fallback_rows'],1)
    def test_deterministic_order(self):
        a,_=historical(self.rows);b,_=historical(self.rows[::-1])
        x,r=forecast(a,self.keys,3);y,_=forecast(b,self.keys[::-1],3)
        self.assertEqual(x,y);self.assertEqual(hashlib.sha256(x).hexdigest(),r['csv_sha256'])
    def test_future_train_rejected(self):
        with self.assertRaises(FullTargetError): historical(self.rows+[tr(1,2,'2025-07-14',9)])
    def test_duplicate_latest_rejected(self):
        with self.assertRaises(FullTargetError): historical(self.rows+[self.rows[1]])
    def test_invalid_quantities(self):
        for v in (float('nan'),float('inf'),-1,True,'1'):
            with self.subTest(v=str(v)),self.assertRaises(FullTargetError):
                historical([tr(1,2,'2025-07-13',v)])
    def test_bad_dates(self):
        for d in ('2025-7-13','2025-07-13T00:00:00',dt.datetime(2025,7,13),None):
            with self.subTest(d=str(d)),self.assertRaises(FullTargetError):
                historical([tr(1,2,d,1)])
    def test_bad_ids(self):
        for k in ('1',-1,True,10**18):
            with self.subTest(k=str(k)),self.assertRaises(FullTargetError):
                historical([tr(k,2,'2025-07-13',1)])
    def test_train_count(self):
        with self.assertRaises(FullTargetError): historical(self.rows,4)
    def test_duplicate_eval(self):
        a,_=historical(self.rows)
        with self.assertRaises(FullTargetError): forecast(a,self.keys+[self.keys[0]],4)
    def test_missing_eval(self):
        a,_=historical(self.rows)
        with self.assertRaises(FullTargetError): forecast(a,self.keys,4)
    def test_extra_eval(self):
        a,_=historical(self.rows)
        with self.assertRaises(FullTargetError): forecast(a,self.keys,2)
    def test_bad_horizon(self):
        a,_=historical(self.rows)
        with self.assertRaises(FullTargetError): forecast(a,[tg(1,2,'2025-07-21')],1)
    def test_future_labels_ignored(self):
        a,_=historical(self.rows)
        x,_=forecast(a,self.keys,3)
        poison=[dict(k,sale_amount=999,stock_hour6_22_cnt=16,hours_sale=['LEAK']) for k in self.keys]
        y,_=forecast(a,poison,3);self.assertEqual(x,y)
    def test_missing_key(self):
        a,_=historical(self.rows)
        with self.assertRaises(FullTargetError): forecast(a,[tg(None,2,'2025-07-14')],1)
    def test_empty_train(self):
        with self.assertRaises(FullTargetError): historical([])
if __name__=='__main__': unittest.main()
