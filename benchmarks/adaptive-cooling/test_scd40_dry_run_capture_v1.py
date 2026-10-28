"""Fictional test doubles only; no physical data or claimed device execution."""
import json
from pathlib import Path
import tempfile
import unittest
from scd40_dry_run_capture_v1 import capture, valid_sample


class Clock:
    def __init__(self): self.t = 0.
    def now(self): return self.t
    def sleep(self, seconds): self.t += seconds


class Sensor:
    def __init__(self, ready=True, temp=25., rh=45., co2=700.):
        self.ready, self.temperature, self.relative_humidity, self.CO2 = ready, temp, rh, co2
        self.started = self.stopped = False
    @property
    def data_ready(self): return self.ready
    def start_periodic_measurement(self): self.started = True
    def stop_periodic_measurement(self): self.stopped = True


class Tests(unittest.TestCase):
    def test_valid_fictional_device(self):
        with tempfile.TemporaryDirectory() as td:
            c, s = Clock(), Sensor()
            path = Path(td) / 'capture.jsonl'
            r = capture(s, path, run_id='FICTIONAL', placement='fixture',
                        duration_s=3, poll_s=1, monotonic=c.now, sleep=c.sleep)
            rows = [json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual([x['event'] for x in rows], ['begin','sample','sample','sample','complete'])
            self.assertEqual(r['samples'], 3)
            self.assertFalse(r['capture_quality_gate_passed'])
            self.assertEqual(r['elapsed_monotonic_s'], 3)
            self.assertFalse(rows[-1]['minimum_600_s_observed'])
            self.assertFalse(r['physical_origin_authenticated'])
            self.assertTrue(s.started and s.stopped)
    def test_no_data_not_fabricated(self):
        with tempfile.TemporaryDirectory() as td:
            c, s = Clock(), Sensor(ready=False)
            r = capture(s, Path(td)/'empty.jsonl', run_id='F', placement='fixture',
                        duration_s=2, poll_s=1, monotonic=c.now, sleep=c.sleep)
            self.assertEqual(r['samples'], 0)
    def test_failure_preserves_partial_and_stops(self):
        with tempfile.TemporaryDirectory() as td:
            c, s = Clock(), Sensor(temp=float('nan'))
            p = Path(td)/'failed.jsonl'
            with self.assertRaises(ValueError):
                capture(s, p, run_id='F', placement='fixture', duration_s=2,
                        monotonic=c.now, sleep=c.sleep)
            rows = [json.loads(x) for x in p.read_text().splitlines()]
            self.assertEqual(rows[-1]['event'], 'capture_failed')
            self.assertTrue(s.stopped)
            self.assertNotIn('complete', [x['event'] for x in rows])
    def test_never_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'prior.jsonl'; p.write_text('previous evidence')
            with self.assertRaises(FileExistsError):
                capture(Sensor(), p, run_id='F', placement='fixture', duration_s=1)
            self.assertEqual(p.read_text(), 'previous evidence')
    def test_invalid_values(self):
        for values in [(float('inf'), 50, 500), (20, 101, 500), (20, 50, -1), ('20', 50, 500)]:
            with self.subTest(values=values), self.assertRaises(ValueError): valid_sample(*values)
    def test_missing_provenance(self):
        with self.assertRaises(ValueError):
            capture(Sensor(), '/does/not/matter', run_id='', placement='fixture')
    def test_early_dropout_cannot_pass_600_second_gate(self):
        class Dropout(Sensor):
            @property
            def data_ready(self): return c.now() < 10
        with tempfile.TemporaryDirectory() as td:
            c = Clock()
            r = capture(Dropout(), Path(td)/'dropout.jsonl', run_id='F',
                        placement='fixture', duration_s=600, poll_s=5,
                        monotonic=c.now, sleep=c.sleep)
            self.assertEqual(r['samples'], 2)
            self.assertFalse(r['capture_quality_gate_passed'])

    def test_600_second_elapsed_flag_fictional(self):
        with tempfile.TemporaryDirectory() as td:
            c = Clock()
            r = capture(Sensor(ready=False), Path(td)/'f.jsonl', run_id='F',
                        placement='fixture', duration_s=600, poll_s=5,
                        monotonic=c.now, sleep=c.sleep)
            self.assertEqual(r['elapsed_monotonic_s'], 600)
            self.assertEqual(r['samples'], 0)
            self.assertFalse(r['capture_quality_gate_passed'])
            rows = [json.loads(x) for x in (Path(td)/'f.jsonl').read_text().splitlines()]
            self.assertTrue(rows[-1]['minimum_600_s_observed'])
            self.assertEqual(rows[-1]['samples'], 0)


if __name__ == '__main__': unittest.main()
