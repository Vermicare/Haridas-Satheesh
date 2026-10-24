"""Entirely fictional cooling CSV fixtures. No physical experiments."""
import csv
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
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


if __name__ == '__main__':
    unittest.main()
