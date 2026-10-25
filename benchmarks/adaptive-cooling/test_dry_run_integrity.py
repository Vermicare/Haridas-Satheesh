"""Entirely fictional cooling CSV fixtures. No physical experiments."""
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from dry_run_integrity import HEADER, audit


class DryRunIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'fictional.csv'
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.rows = []
        for i in range(11):
            row = dict.fromkeys(HEADER, '')
            row.update(run_id='DEMO', timestamp=(start + timedelta(seconds=i*60)).isoformat(),
                       condition='fan_only', ambient_temp_c='28', ambient_rh_pct='50',
                       target_temp_c='27', target_rh_pct='52', air_velocity_m_s='1.0',
                       surface_temp_c='27', power_w='60', energy_wh=str(i),
                       condensation_flag='no', notes='fictional test data')
            self.rows.append(row)
        self.write()

    def write(self):
        with self.path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(self.rows)

    def codes(self):
        return audit(self.path)['problems']

    def test_fictional_consistent_structure_is_not_physical_evidence(self):
        r = audit(self.path)
        self.assertEqual(r['status'], 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED')
        self.assertFalse(r['physical_origin_authenticated'])
        self.assertFalse(r['performance_claim_permitted'])
        self.assertAlmostEqual(r['power_integral_estimate_wh'], 10)
        self.assertAlmostEqual(r['energy_counter_delta_wh'], 10)

    def test_nonincrementing_energy_counter_rejected(self):
        for row in self.rows: row['energy_wh'] = '0'
        self.write()
        self.assertIn('POWER_ENERGY_INCONSISTENCY', self.codes())

    def test_counter_reset_rejected(self):
        self.rows[6]['energy_wh'] = '0'; self.write()
        self.assertIn('ENERGY_COUNTER_DECREASE', self.codes())

    def test_backward_timestamp_rejected(self):
        self.rows[5]['timestamp'] = self.rows[4]['timestamp']; self.write()
        self.assertIn('NONMONOTONIC_TIMESTAMP', self.codes())

    def test_insufficient_duration_rejected(self):
        self.rows.pop(); self.write()
        self.assertIn('INSUFFICIENT_DURATION', self.codes())

    def test_gap_rejected(self):
        self.rows.pop(5); self.write()
        self.assertIn('SAMPLING_GAP', self.codes())

    def test_mixed_run_rejected(self):
        self.rows[6]['run_id'] = 'OTHER'; self.write()
        self.assertIn('MIXED_RUN_IDS', self.codes())

    def test_mixed_condition_rejected(self):
        self.rows[6]['condition'] = 'prototype'; self.write()
        self.assertIn('MIXED_CONDITIONS', self.codes())

    def test_bad_humidity_rejected(self):
        self.rows[2]['ambient_rh_pct'] = '101'; self.write()
        self.assertIn('RH_OUT_OF_RANGE', self.codes())

    def test_missing_value_rejected(self):
        self.rows[2]['power_w'] = ''; self.write()
        self.assertIn('INVALID_NUMERIC', self.codes())

    def test_extra_column_rejected(self):
        with self.path.open('a') as f: f.write(',unexpected\n')
        self.assertIn('MALFORMED_ROW', self.codes())

    def test_naive_timestamp_rejected(self):
        self.rows[2]['timestamp'] = '2026-01-01T00:02:00'; self.write()
        self.assertIn('INVALID_TIMESTAMP', self.codes())

    def test_negative_power_rejected(self):
        self.rows[2]['power_w'] = '-1'; self.write()
        self.assertIn('NEGATIVE_PHYSICAL_QUANTITY', self.codes())

    def test_nonfinite_rejected(self):
        self.rows[2]['power_w'] = 'nan'; self.write()
        self.assertIn('INVALID_NUMERIC', self.codes())


    def test_snapshot_digest_matches_exact_parsed_raw_bytes(self):
        raw = self.path.read_bytes()
        result = audit(self.path, expected_sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['status'], 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED')
        self.assertEqual(result['raw_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['raw_byte_count'], len(raw))

    def test_pinned_digest_rejects_changed_raw_bytes(self):
        pinned = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.rows[3]['notes'] = 'fictional edited after pinning'
        self.write()
        result = audit(self.path, expected_sha256=pinned)
        self.assertIn('RAW_SHA256_MISMATCH', result['problems'])
        self.assertFalse(result['performance_claim_permitted'])

    def test_malformed_pinned_digest_rejected(self):
        result = audit(self.path, expected_sha256='not-a-sha256')
        self.assertIn('INVALID_EXPECTED_SHA256', result['problems'])

    def test_uppercase_pinned_digest_accepted(self):
        pinned = hashlib.sha256(self.path.read_bytes()).hexdigest().upper()
        self.assertEqual(audit(self.path, expected_sha256=pinned)['problems'], [])

    def test_parse_uses_hashed_snapshot_not_second_filesystem_read(self):
        original = self.path.read_bytes()
        real_read_bytes = Path.read_bytes
        def replace_after_snapshot_read(path):
            if path == self.path:
                self.rows[4]['notes'] = 'fictional later filesystem mutation'
                self.write()
                return original
            return real_read_bytes(path)
        with patch.object(Path, 'read_bytes', replace_after_snapshot_read):
            result = audit(self.path, expected_sha256=hashlib.sha256(original).hexdigest())
        self.assertEqual(result['status'], 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED')
        self.assertEqual(result['raw_sha256'], hashlib.sha256(original).hexdigest())
        self.assertNotEqual(result['raw_sha256'], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertFalse(result['physical_origin_authenticated'])


    def test_large_finite_power_stalled_counter_rejected(self):
        # Pre-fix: (1e308 + 1e308)/2 overflowed to inf; inf > inf
        # was false, allowing an invalid structural PASS.
        for row in self.rows:
            row['power_w'] = '1e308'
            row['energy_wh'] = '0'
        self.write()
        result = audit(self.path)
        self.assertIn('POWER_ENERGY_INCONSISTENCY', result['problems'])
        self.assertEqual(result['status'], 'REJECTED')
        self.assertTrue(math.isfinite(result['power_integral_estimate_wh']))
        json.dumps(result, allow_nan=False)

    def test_large_finite_consistent_power_counter_stays_finite(self):
        # Positive arithmetic control; fictional values are NOT physical evidence.
        for i, row in enumerate(self.rows):
            row['power_w'] = '1e308'
            row['energy_wh'] = str((i / 60) * 1e308)
        self.write()
        result = audit(self.path)
        self.assertEqual(result['status'], 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED')
        self.assertTrue(math.isfinite(result['power_integral_estimate_wh']))
        self.assertFalse(result['performance_claim_permitted'])
        json.dumps(result, allow_nan=False)

    def test_nonfinite_derived_integral_rejected_json_safely(self):
        # Pathological timestamp gaps already fail, but must never emit Infinity.
        for i, row in enumerate(self.rows):
            row['timestamp'] = f'{2000 + i * 100:04d}-01-01T00:00:00+00:00'
            row['power_w'] = '1e308'
            row['energy_wh'] = '0'
        self.write()
        result = audit(self.path)
        self.assertIn('NONFINITE_DERIVED_ENERGY', result['problems'])
        self.assertIsNone(result['power_integral_estimate_wh'])
        self.assertEqual(result['status'], 'REJECTED')
        json.dumps(result, allow_nan=False)

    def test_nonfinite_derived_tolerance_rejected(self):
        for row in self.rows:
            row['energy_wh'] = '0'
        self.write()
        result = audit(self.path, energy_rel_tol=1e308)
        self.assertIn('NONFINITE_ENERGY_TOLERANCE', result['problems'])
        self.assertEqual(result['status'], 'REJECTED')
        json.dumps(result, allow_nan=False)

if __name__ == '__main__':
    unittest.main()
