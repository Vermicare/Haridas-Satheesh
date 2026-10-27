"""Fictional-only negative controls for cooling capture-byte chain. No hardware."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from capture_chain import audit, ROLES, REQUIRED_METADATA, VERSION


class CaptureChainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.metadata = {key: 'FICTIONAL_TEST_ONLY' for key in REQUIRED_METADATA}
        self.metadata.update(run_id='FICTIONAL_RUN',
                             capture_start='2026-01-01T00:00:00+00:00',
                             capture_end='2026-01-01T00:10:00+00:00',
                             sample_interval_s=30)
        self.manifest = {
            'schema_version': VERSION, 'origin': 'fictional_test_only',
            'metadata': self.metadata, 'artifacts': {},
        }
        for role in ROLES:
            name = role + '.txt'
            content = ('FICTIONAL TEST ' + role + '\n').encode()
            (self.root / name).write_bytes(content)
            self.manifest['artifacts'][role] = {
                'path': name, 'sha256': hashlib.sha256(content).hexdigest()}
        self.write()

    def write(self):
        (self.root / 'capture_manifest.json').write_text(
            json.dumps(self.manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    def problems(self):
        return audit(self.root)['problems']

    def test_fictional_chain_pass_is_not_physical_proof(self):
        report = audit(self.root)
        self.assertEqual(report['status'], 'CHAIN_CHECKED_ORIGIN_UNVERIFIED')
        self.assertFalse(report['physical_origin_authenticated'])
        self.assertFalse(report['logger_to_csv_conversion_verified'])
        self.assertFalse(report['performance_claim_permitted'])
        self.assertEqual(len(report['artifacts']), 4)
        json.dumps(report, allow_nan=False)

    def test_modified_raw_logger_rejected(self):
        (self.root / 'original_logger.txt').write_text('DIFFERENT\n')
        self.assertIn('SHA256_MISMATCH_ORIGINAL_LOGGER', self.problems())

    def test_swapped_measurement_csv_rejected(self):
        (self.root / 'measurement_csv.txt').write_text('SWAPPED\n')
        self.assertIn('SHA256_MISMATCH_MEASUREMENT_CSV', self.problems())

    def test_modified_instrument_manifest_rejected(self):
        (self.root / 'instrument_manifest.txt').write_text('CHANGED\n')
        self.assertIn('SHA256_MISMATCH_INSTRUMENT_MANIFEST', self.problems())

    def test_missing_original_logger_rejected(self):
        (self.root / 'original_logger.txt').unlink()
        self.assertIn('UNREADABLE_OR_UNSAFE_ARTIFACT_ORIGINAL_LOGGER', self.problems())

    def test_empty_run_plan_rejected_even_with_matching_digest(self):
        (self.root / 'run_plan.txt').write_bytes(b'')
        self.manifest['artifacts']['run_plan']['sha256'] = hashlib.sha256(b'').hexdigest()
        self.write()
        self.assertIn('EMPTY_ARTIFACT_RUN_PLAN', self.problems())

    def test_path_traversal_rejected(self):
        self.manifest['artifacts']['run_plan']['path'] = '../run_plan.txt'
        self.write()
        self.assertIn('UNREADABLE_OR_UNSAFE_ARTIFACT_RUN_PLAN', self.problems())

    def test_noncanonical_path_alias_rejected(self):
        self.manifest['artifacts']['run_plan']['path'] = './run_plan.txt'
        self.write()
        self.assertIn('UNREADABLE_OR_UNSAFE_ARTIFACT_RUN_PLAN', self.problems())

    def test_whitespace_metadata_rejected(self):
        self.metadata['heat_rejection_path'] = '   '
        self.write()
        self.assertIn('MISSING_METADATA_HEAT_REJECTION_PATH', self.problems())

    def test_symlink_artifact_rejected(self):
        target = self.root / 'run_plan.txt'
        target.rename(self.root / 'real_run_plan.txt')
        target.symlink_to(self.root / 'real_run_plan.txt')
        self.assertIn('UNREADABLE_OR_UNSAFE_ARTIFACT_RUN_PLAN', self.problems())

    def test_duplicate_artifact_paths_rejected(self):
        self.manifest['artifacts']['run_plan']['path'] = 'original_logger.txt'
        self.write()
        self.assertIn('DUPLICATE_OR_INVALID_ARTIFACT_PATH', self.problems())

    def test_duplicate_json_key_rejected(self):
        original = (self.root / 'capture_manifest.json').read_text()
        (self.root / 'capture_manifest.json').write_text('{' + '"origin":"fictional_test_only",' + original[1:])
        self.assertIn('MANIFEST_UNREADABLE_OR_AMBIGUOUS', self.problems())

    def test_nonfinite_json_rejected(self):
        original = (self.root / 'capture_manifest.json').read_text()
        (self.root / 'capture_manifest.json').write_text(original.replace('"sample_interval_s": 30', '"sample_interval_s": NaN'))
        self.assertIn('MANIFEST_UNREADABLE_OR_AMBIGUOUS', self.problems())

    def test_missing_thermal_storage_boundary_rejected(self):
        self.metadata['recharge_energy_accounting'] = 'TBD'
        self.write()
        self.assertIn('MISSING_METADATA_RECHARGE_ENERGY_ACCOUNTING', self.problems())

    def test_short_declared_capture_rejected(self):
        self.metadata['capture_end'] = '2026-01-01T00:09:59+00:00'
        self.write()
        self.assertIn('DECLARED_CAPTURE_UNDER_600S', self.problems())

    def test_naive_clock_rejected(self):
        self.metadata['capture_start'] = '2026-01-01T00:00:00'
        self.write()
        self.assertIn('INVALID_CAPTURE_TIME_RANGE', self.problems())

    def test_manifest_external_pin_detects_edit(self):
        original = hashlib.sha256((self.root / 'capture_manifest.json').read_bytes()).hexdigest()
        self.metadata['logger_version'] = 'CHANGED'
        self.write()
        result = audit(self.root, expected_manifest_sha256=original)
        self.assertIn('MANIFEST_PIN_MISMATCH', result['problems'])
        self.assertFalse(result['external_manifest_pin_verified'])

    def test_correct_manifest_external_pin_verified_but_not_authentic(self):
        digest = hashlib.sha256((self.root / 'capture_manifest.json').read_bytes()).hexdigest()
        result = audit(self.root, expected_manifest_sha256=digest.upper())
        self.assertTrue(result['external_manifest_pin_verified'])
        self.assertEqual(result['status'], 'CHAIN_CHECKED_ORIGIN_UNVERIFIED')
        self.assertFalse(result['physical_origin_authenticated'])

    def test_invalid_manifest_pin_rejected(self):
        self.assertIn('INVALID_MANIFEST_PIN', audit(self.root, expected_manifest_sha256='bad')['problems'])

    def test_malformed_artifact_sha_rejected(self):
        self.manifest['artifacts']['original_logger']['sha256'] = 'not-sha'
        self.write()
        self.assertIn('INVALID_SHA256_ORIGINAL_LOGGER', self.problems())

    def test_missing_artifact_role_rejected(self):
        self.manifest['artifacts'].pop('run_plan')
        self.write()
        self.assertIn('ARTIFACT_ROLES_MISMATCH', self.problems())

    def test_invalid_origin_rejected(self):
        self.manifest['origin'] = 'real_100_percent_proven'
        self.write()
        self.assertIn('INVALID_ORIGIN_DECLARATION', self.problems())


if __name__ == '__main__':
    unittest.main()
