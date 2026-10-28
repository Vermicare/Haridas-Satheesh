"""Fictional-only adversarial structural verification. Zero sensor hardware."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from scd40_capture_verify_v2 import verify, CaptureError


def fixture():
    rows = [{'event':'begin','schema_version':'scd40-physical-dry-run-logger-v1',
             'run_id':'FICTIONAL','placement':'test fixture',
             'declared_origin':'physical_device_logger',
             'physical_origin_authenticated':False,'calibration_verified':False,
             'cooling_performance_claim_permitted':False,'utc':'2026-10-29T00:00:00+00:00',
             'requested_duration_s':600,'poll_s':5}]
    for i in range(120):
        rows.append({'event':'sample','index':i,'utc':'2026-10-29T00:00:00+00:00',
                     'elapsed_monotonic_s':i*5.,'scd4x_temperature_c':25.,
                     'scd4x_relative_humidity_pct':45.,'scd4x_co2_ppm':700.})
    rows.append({'event':'complete','utc':'2026-10-29T00:10:00+00:00',
                 'elapsed_monotonic_s':600.,'samples':120,'max_sample_gap_s':5.,
                 'minimum_600_s_observed':True,'capture_quality_gate_passed':True,
                 'physical_origin_authenticated':False,
                 'cooling_performance_claim_permitted':False})
    return rows


def encode(rows):
    return (''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows)).encode()


class VerificationTests(unittest.TestCase):
    def check(self, rows, *, good=False):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private.jsonl'; raw=encode(rows);p.write_bytes(raw)
            sha=hashlib.sha256(raw).hexdigest()
            if good:
                result=verify(p,expected_sha256=sha)
                self.assertTrue(result['recomputed_capture_quality_gate_passed'])
                self.assertFalse(result['physical_origin_authenticated'])
                return
            with self.assertRaises(CaptureError): verify(p,expected_sha256=sha)
    def test_fictional_positive_only_structural(self): self.check(fixture(),good=True)
    def test_no_samples_is_valid_file_but_quality_fails(self):
        rows=fixture();rows[1:-1]=[]
        rows[-1]['samples']=0
        rows[-1]['max_sample_gap_s']=None
        rows[-1]['capture_quality_gate_passed']=False
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'empty.jsonl';raw=encode(rows);p.write_bytes(raw)
            result=verify(p,expected_sha256=hashlib.sha256(raw).hexdigest())
            self.assertTrue(result['record_structure_valid'])
            self.assertFalse(result['recomputed_capture_quality_gate_passed'])
    def test_integration_with_actual_logger_mock_only(self):
        # The live logger's capture() is imported from the same repository branch.
        # No hardware import, no physical claim, no 600-second wall-clock wait.
        from scd40_dry_run_capture_v1 import capture
        class Clock:
            t=0.
            def now(self): return self.t
            def sleep(self, n): self.t+=n
        class Sensor:
            temperature=25.
            relative_humidity=45.
            CO2=700.
            data_ready=True
            def start_periodic_measurement(self): pass
            def stop_periodic_measurement(self): pass
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fictional.jsonl';c=Clock()
            logger_result=capture(Sensor(),p,run_id='FICTIONAL-INTEGRATION',
                                  placement='fictional fixture',duration_s=600,poll_s=5,
                                  monotonic=c.now,sleep=c.sleep)
            checked=verify(p,expected_sha256=logger_result['sha256'])
            self.assertEqual(checked['samples'],120)
            self.assertTrue(checked['recomputed_capture_quality_gate_passed'])
            self.assertFalse(checked['physical_origin_authenticated'])
    def test_requires_prior_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'f.jsonl';p.write_bytes(encode(fixture()))
            with self.assertRaisesRegex(CaptureError,'preexisting'):verify(p)
    def test_tamper_after_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'f.jsonl';p.write_bytes(encode(fixture()));sha=hashlib.sha256(p.read_bytes()).hexdigest()
            p.write_bytes(p.read_bytes().replace(b'700.0',b'701.0',1))
            with self.assertRaisesRegex(CaptureError,'SHA-256 mismatch'):verify(p,expected_sha256=sha)
    def test_missing_sample(self):
        rows=fixture();rows.pop(40);self.check(rows)
    def test_duplicate_index(self):
        rows=fixture();rows[12]['index']=10;self.check(rows)
    def test_forged_quality_flag(self):
        rows=fixture();rows[-1]['capture_quality_gate_passed']=False;self.check(rows)
    def test_forged_sample_count(self):
        rows=fixture();rows[-1]['samples']=121;self.check(rows)
    def test_forged_gap(self):
        rows=fixture();rows[-1]['max_sample_gap_s']=0.;self.check(rows)
    def test_nonmonotonic(self):
        rows=fixture();rows[12]['elapsed_monotonic_s']=rows[11]['elapsed_monotonic_s'];self.check(rows)
    def test_out_of_range(self):
        rows=fixture();rows[12]['scd4x_co2_ppm']=-1;self.check(rows)
    def test_missing_complete(self):self.check(fixture()[:-1])
    def test_failed_record(self):
        rows=fixture();rows.insert(-1,{'event':'stop_failed'});self.check(rows)
    def test_unsupported_origin_claim(self):
        rows=fixture();rows[0]['physical_origin_authenticated']=True;self.check(rows)
    def test_duration_forgery(self):
        rows=fixture();rows[-1]['elapsed_monotonic_s']=10.;self.check(rows)
    def test_missing_end_newline(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'f.jsonl';raw=encode(fixture()).rstrip(b'\n');p.write_bytes(raw)
            with self.assertRaisesRegex(CaptureError,'truncated'):verify(p,expected_sha256=hashlib.sha256(raw).hexdigest())
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'f.jsonl';raw=encode(fixture()).replace(b'"index": 0',b'"index": 0, "index": 0',1);p.write_bytes(raw)
            with self.assertRaisesRegex(CaptureError,'duplicate JSON key'):verify(p,expected_sha256=hashlib.sha256(raw).hexdigest())
    def test_false_early_dropout_pass(self):
        rows=fixture();rows[2:-1]=[];rows[-1]['samples']=1;rows[-1]['max_sample_gap_s']=None
        rows[-1]['capture_quality_gate_passed']=True;self.check(rows)


if __name__=='__main__':unittest.main()
