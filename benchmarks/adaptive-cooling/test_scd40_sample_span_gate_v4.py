"""Fictional negative controls: no physical device or real ten-minute wait."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from scd40_dry_run_capture_v1 import capture
from scd40_capture_verify_v2 import verify, CaptureError
from scd40_sample_span_gate_v4 import audit

class Clock:
    def __init__(self):
        self.t = 0.0
        self.base = datetime(2026, 10, 30, tzinfo=timezone.utc)
    def monotonic(self): return self.t
    def sleep(self, seconds): self.t += seconds
    def utc(self): return self.base + timedelta(seconds=self.t)

class Sensor:
    def __init__(self, clock, first, last):
        self.clock, self.first, self.last = clock, first, last
        self.temperature, self.relative_humidity, self.CO2 = 25.0, 45.0, 700.0
    def start_periodic_measurement(self): pass
    def stop_periodic_measurement(self): pass
    @property
    def data_ready(self): return self.first <= self.clock.t <= self.last

def case(path, first, last):
    clock = Clock()
    receipt = capture(Sensor(clock, first, last), path,
                      run_id='FICTIONAL', placement='FICTIONAL', duration_s=600,
                      poll_s=5, monotonic=clock.monotonic, sleep=clock.sleep,
                      utc_now=clock.utc)
    return receipt

class Tests(unittest.TestCase):
    def test_boundary_dropout_passes_v2_but_requires_v4_review(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'fictional.jsonl'; receipt = case(p, 60, 540)
            self.assertTrue(verify(p,expected_sha256=receipt['sha256'])['recomputed_capture_quality_gate_passed'])
            result = audit(p,expected_sha256=receipt['sha256'])
            self.assertEqual(result['status'],'REVIEW_REQUIRED')
            self.assertEqual(result['sample_span_s'],480)
            self.assertEqual(result['minimum_review_sample_span_s'],590)
            self.assertIn('SAMPLE_SPAN_SHORTER_THAN_PROVISIONAL_REVIEW_MINIMUM',result['problems'])
    def test_nominal_span_is_consistent_but_not_physical_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'fictional.jsonl'; receipt = case(p, 5, 595)
            result = audit(p,expected_sha256=receipt['sha256'])
            self.assertEqual(result['status'],'SAMPLE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED')
            self.assertEqual(result['sample_span_s'],590)
            self.assertFalse(result['physical_origin_authenticated'])
            self.assertFalse(result['cooling_performance_claim_permitted'])
    def test_byte_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'fictional.jsonl'; receipt = case(p, 5, 595)
            p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaises(CaptureError): audit(p,expected_sha256=receipt['sha256'])
    def test_no_sample_is_review_required(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'fictional.jsonl'; receipt = case(p, 1000, 2000)
            result = audit(p,expected_sha256=receipt['sha256'])
            self.assertEqual(result['status'],'REVIEW_REQUIRED')
            self.assertIn('V2_CAPTURE_QUALITY_NOT_MET',result['problems'])

if __name__=='__main__': unittest.main()
