"""Fictional UTC/monotonic consistency tests; no physical device or elapsed time."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from scd40_clock_concordance_v3 import audit, ClockAuditError

START=datetime(2026,10,29,tzinfo=timezone.utc)

def fixture():
    rows=[{'event':'begin','utc':START.isoformat()}]
    for i in range(120):
        rows.append({'event':'sample','index':i,'utc':(START+timedelta(seconds=5*i)).isoformat(), 'elapsed_monotonic_s':5*i})
    rows.append({'event':'complete','utc':(START+timedelta(seconds=600)).isoformat(),'elapsed_monotonic_s':600})
    return rows

class ClockTests(unittest.TestCase):
    def run_case(self, rows, *, corrupt_hash=False):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fictional.jsonl'
            raw=(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows)).encode()
            p.write_bytes(raw)
            sha=hashlib.sha256(raw).hexdigest()
            if corrupt_hash:
                sha='0'*64
            return audit(p,sha)
    def test_aligned_fictional(self):
        r=self.run_case(fixture())
        self.assertFalse(r['clock_review_required'])
        self.assertEqual(r['sample_count'],120)
        self.assertFalse(r['physical_origin_authenticated'])
    def test_frozen_utc_detected(self):
        rows=fixture()
        for row in rows[1:]:row['utc']=START.isoformat()
        r=self.run_case(rows)
        self.assertTrue(r['clock_review_required'])
        self.assertEqual(r['max_utc_monotonic_skew_s'],600)
    def test_utc_backward_jump_detected(self):
        rows=fixture();rows[30]['utc']=(START-timedelta(seconds=10)).isoformat()
        r=self.run_case(rows)
        self.assertTrue(r['clock_review_required'])
        self.assertEqual(r['utc_regressions'],1)
    def test_clock_forward_jump_detected(self):
        rows=fixture();rows[40]['utc']=(START+timedelta(seconds=300)).isoformat()
        r=self.run_case(rows)
        self.assertTrue(r['clock_review_required'])
    def test_bad_sha_rejected(self):
        with self.assertRaisesRegex(ClockAuditError,'SHA-256 mismatch'):
            self.run_case(fixture(),corrupt_hash=True)
    def test_non_increasing_monotonic_rejected(self):
        rows=fixture();rows[40]['elapsed_monotonic_s']=rows[39]['elapsed_monotonic_s']
        with self.assertRaisesRegex(ClockAuditError,'non-increasing'):
            self.run_case(rows)
    def test_clock_drift_below_tolerance(self):
        rows=fixture();rows[-1]['utc']=(START+timedelta(seconds=606)).isoformat()
        self.assertFalse(self.run_case(rows)['clock_review_required'])

if __name__=='__main__': unittest.main()
