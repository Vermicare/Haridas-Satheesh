"""Fictional-only cooling cross-artifact alignment regressions. No hardware."""
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from capture_alignment import audit
from capture_chain import REQUIRED_METADATA, VERSION
from dry_run_integrity import HEADER


class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.rows = []
        for i in range(11):
            row = dict.fromkeys(HEADER, '')
            row.update(run_id='FICTIONAL-001',
                       timestamp=(self.start + timedelta(seconds=60*i)).isoformat(),
                       condition='ambient', ambient_temp_c='30', ambient_rh_pct='50',
                       target_temp_c='29', target_rh_pct='50', air_velocity_m_s='0',
                       surface_temp_c='28', power_w='60', energy_wh=str(i),
                       condensation_flag='no', notes='FICTIONAL_TEST_ONLY')
            self.rows.append(row)
        self.plan = {'run_id': 'FICTIONAL-001', 'condition': 'ambient',
                     'geometry_id': 'FICTIONAL_TEST_ONLY'}
        self.metadata = {key: 'FICTIONAL_TEST_ONLY' for key in REQUIRED_METADATA}
        self.metadata.update(run_id='FICTIONAL-001', capture_start=self.start.isoformat(),
                             capture_end=(self.start + timedelta(seconds=600)).isoformat(),
                             sample_interval_s=60)
        self.manifest = {'schema_version': VERSION, 'origin': 'fictional_test_only',
                         'metadata': self.metadata, 'artifacts': {}}
        (self.root / 'original_logger.txt').write_text('FICTIONAL_TEST_ONLY\n')
        (self.root / 'instrument_manifest.csv').write_text('FICTIONAL_TEST_ONLY\n')
        self.save()

    def save(self):
        with (self.root / 'measurement.csv').open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=HEADER, lineterminator='\n')
            w.writeheader(); w.writerows(self.rows)
        (self.root / 'run_plan.json').write_text(json.dumps(self.plan) + '\n')
        names = {'original_logger': 'original_logger.txt',
                 'measurement_csv': 'measurement.csv',
                 'instrument_manifest': 'instrument_manifest.csv',
                 'run_plan': 'run_plan.json'}
        for role, name in names.items():
            self.manifest['artifacts'][role] = {
                'path': name, 'sha256': hashlib.sha256((self.root / name).read_bytes()).hexdigest()}
        (self.root / 'capture_manifest.json').write_text(json.dumps(self.manifest, sort_keys=True) + '\n')

    def test_fictional_aligned_bundle_is_not_physical_proof(self):
        report = audit(self.root)
        self.assertEqual(report['status'], 'DECLARATIONS_ALIGNED_ORIGIN_UNVERIFIED', report)
        self.assertFalse(report['physical_origin_authenticated'])
        self.assertFalse(report['logger_to_csv_conversion_verified'])
        self.assertFalse(report['performance_claim_permitted'])
        self.assertEqual(report['summary']['rows'], 11)
        json.dumps(report, allow_nan=False)

    def test_csv_run_id_disagrees_even_when_rehashed(self):
        self.rows[0]['run_id'] = 'FICTIONAL-DIFFERENT'
        self.save()
        self.assertIn('RUN_ID_MANIFEST_MISMATCH', audit(self.root)['problems'])

    def test_all_csv_ids_disagree_even_when_rehashed(self):
        for row in self.rows: row['run_id'] = 'FICTIONAL-DIFFERENT'
        self.save()
        self.assertIn('RUN_ID_MANIFEST_MISMATCH', audit(self.root)['problems'])

    def test_plan_run_id_disagrees_even_when_rehashed(self):
        self.plan['run_id'] = 'FICTIONAL-DIFFERENT'
        self.save()
        self.assertIn('RUN_ID_PLAN_MISMATCH', audit(self.root)['problems'])

    def test_plan_condition_disagrees_even_when_rehashed(self):
        self.plan['condition'] = 'prototype'
        self.save()
        self.assertIn('CONDITION_PLAN_MISMATCH', audit(self.root)['problems'])

    def test_missing_plan_condition_fails_closed(self):
        self.plan.pop('condition')
        self.save()
        self.assertIn('CONDITION_PLAN_MISMATCH', audit(self.root)['problems'])

    def test_start_declaration_far_before_samples_fails(self):
        self.metadata['capture_start'] = (self.start - timedelta(seconds=120)).isoformat()
        self.save()
        self.assertIn('CAPTURE_START_MISMATCH', audit(self.root)['problems'])

    def test_end_declaration_far_after_samples_fails(self):
        self.metadata['capture_end'] = (self.start + timedelta(seconds=720)).isoformat()
        self.save()
        self.assertIn('CAPTURE_END_MISMATCH', audit(self.root)['problems'])

    def test_one_interval_capture_boundary_slack_accepted(self):
        self.metadata['capture_start'] = (self.start - timedelta(seconds=60)).isoformat()
        self.metadata['capture_end'] = (self.start + timedelta(seconds=660)).isoformat()
        self.save()
        self.assertEqual(audit(self.root)['status'], 'DECLARATIONS_ALIGNED_ORIGIN_UNVERIFIED')

    def test_csv_energy_disagreement_rejected(self):
        for row in self.rows: row['energy_wh'] = '0'
        self.save()
        self.assertIn('CSV_INTEGRITY_REJECTED', audit(self.root)['problems'])

    def test_tampered_csv_without_rehash_rejected(self):
        (self.root / 'measurement.csv').write_text('SWAPPED\n')
        self.assertIn('CAPTURE_CHAIN_REJECTED', audit(self.root)['problems'])

    def test_invalid_external_manifest_pin_rejected(self):
        self.assertIn('CAPTURE_CHAIN_REJECTED', audit(self.root, expected_manifest_sha256='0'*64)['problems'])

    def test_plan_duplicate_json_key_rejected(self):
        (self.root / 'run_plan.json').write_text('{"run_id":"FICTIONAL-001","run_id":"OTHER","condition":"ambient"}')
        self.manifest['artifacts']['run_plan']['sha256'] = hashlib.sha256((self.root / 'run_plan.json').read_bytes()).hexdigest()
        (self.root / 'capture_manifest.json').write_text(json.dumps(self.manifest) + '\n')
        self.assertIn('ALIGNMENT_UNREADABLE_OR_AMBIGUOUS', audit(self.root)['problems'])


if __name__ == '__main__':
    unittest.main()
