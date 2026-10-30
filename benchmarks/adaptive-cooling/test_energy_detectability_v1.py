"""Fictional negative controls for the existing cooling energy preflight.

No hardware, sensors, power meters, or thermal-performance observations are used.
This is a detectability audit of documented default tolerances, not a proposed
change to the historical validator.
"""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from dry_run_integrity import HEADER, audit

ABS_TOL_WH = 0.5
REL_TOL = 0.30
DURATION_S = 600


def minimum_detectable_constant_power_w(duration_s=DURATION_S):
    """Strict threshold for a stuck-zero energy counter, constant power."""
    return 3600 * ABS_TOL_WH / (duration_s * (1 - REL_TOL))


def fictional_csv(path, *, power_w, counter_tracks_power):
    """Construct a fictional 600 s trace; NEVER a physical measurement."""
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with Path(path).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator='\n')
        writer.writeheader()
        for elapsed in range(0, DURATION_S + 1, 60):
            writer.writerow({
                'run_id': 'FICTIONAL-ENERGY-NEGATIVE-CONTROL',
                'timestamp': (start + timedelta(seconds=elapsed)).isoformat(),
                'condition': 'prototype',
                'ambient_temp_c': '28', 'ambient_rh_pct': '50',
                'target_temp_c': '28', 'target_rh_pct': '50',
                'air_velocity_m_s': '0', 'surface_temp_c': '28',
                'power_w': str(power_w),
                'energy_wh': (f'{power_w * elapsed / 3600:.12f}'
                              if counter_tracks_power else '0'),
                'condensation_flag': 'unknown',
                'notes': 'FICTIONAL TEST ONLY',
            })


class CoolingEnergyDetectabilityTests(unittest.TestCase):
    def check(self, power_w, counter_tracks_power):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fictional.csv'
            fictional_csv(path, power_w=power_w,
                          counter_tracks_power=counter_tracks_power)
            return audit(path)

    def test_low_power_stuck_counter_is_structurally_accepted(self):
        result = self.check(1.0, False)
        self.assertEqual(result['rows'], 11)
        self.assertEqual(result['duration_s'], 600)
        self.assertAlmostEqual(result['power_integral_estimate_wh'], 1 / 6)
        self.assertEqual(result['energy_counter_delta_wh'], 0)
        self.assertEqual(result['status'], 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED')
        self.assertFalse(result['performance_claim_permitted'])

    def test_higher_power_stuck_counter_is_rejected(self):
        result = self.check(5.0, False)
        self.assertEqual(result['status'], 'REJECTED')
        self.assertIn('POWER_ENERGY_INCONSISTENCY', result['problems'])

    def test_low_power_consistent_counter_is_structurally_accepted(self):
        result = self.check(1.0, True)
        self.assertEqual(result['status'], 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED')
        self.assertAlmostEqual(result['energy_counter_delta_wh'], 1 / 6, places=9)

    def test_analytic_detection_boundary(self):
        threshold = minimum_detectable_constant_power_w()
        self.assertAlmostEqual(threshold, 30 / 7, places=10)
        self.assertLess(1.0, threshold)
        self.assertGreater(5.0, threshold)


if __name__ == '__main__':
    unittest.main()
