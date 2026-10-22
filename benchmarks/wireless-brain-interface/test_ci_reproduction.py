"""Regression tests for frozen WBI synthetic reproducibility; not clinical validation."""
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_frozen_wbi as v

FOLDER = Path(__file__).resolve().parent
SOURCE = FOLDER / 'synthetic_evaluator.py'
CSV = FOLDER / 'synthetic_risk_coverage.csv'

class TestFrozenReproduction(unittest.TestCase):
    def test_pinned_blob_and_csv(self):
        info = v.validate_sources(SOURCE, CSV)
        self.assertEqual(info['source_git_blob'], v.EXPECTED_SOURCE_GIT_BLOB)
        self.assertEqual(info['reference_csv_sha256'], v.EXPECTED_CSV_SHA256)

    def test_two_independent_clean_executions(self):
        result = v.run_twice(SOURCE)
        self.assertEqual(result['runs'], 2)
        self.assertTrue(result['deterministic_stdout'])
        self.assertTrue(result['deterministic_csv'])

    def test_reference_metrics(self):
        result = v.run_twice(SOURCE)
        self.assertEqual(result['policies']['authorization_gate']['incorrect_action_risk'], .1571)
        self.assertEqual(result['policies']['confidence_abstention']['incorrect_action_risk'], .1301)
        self.assertNotEqual(result['policies']['authorization_gate']['coverage'],
                            result['policies']['confidence_abstention']['coverage'])

    def test_source_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / 'synthetic_evaluator.py'
            bad.write_bytes(SOURCE.read_bytes() + b'\n# accidental change\n')
            with self.assertRaisesRegex(ValueError, 'FROZEN SOURCE CHANGED'):
                v.validate_sources(bad, CSV)

    def test_reference_csv_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / 'synthetic_risk_coverage.csv'
            bad.write_bytes(CSV.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'PUBLISHED CSV CHANGED'):
                v.validate_sources(SOURCE, bad)

    def test_missing_synthetic_warning_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing synthetic-only warning'):
            v.parse_stdout('frozen thresholds: abstention_conf=0.75; gate_conf=0.70; gate_drift=0.70')

    def test_threshold_tampering_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Threshold drift'):
            v.parse_stdout('SYNTHETIC ONLY — not EEG/clinical validation\n'
                           'frozen thresholds: abstention_conf=0.80; gate_conf=0.70; gate_drift=0.70')

    def test_report_does_not_upgrade_evidence(self):
        result = v.verify(SOURCE, CSV)
        self.assertEqual(result['real_eeg'], 'TBD')
        self.assertEqual(result['matched_coverage_gate_superiority'], 'NOT ESTABLISHED')
        self.assertIn('TBD', result['cross_environment_ci'])

    def test_wrong_policy_metric_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Synthetic reference metrics changed'):
            v.parse_stdout('SYNTHETIC ONLY — not EEG/clinical validation\n'
                           'frozen thresholds: abstention_conf=0.75; gate_conf=0.70; gate_drift=0.70\n'
                           'ungated coverage=1.0000 incorrect_action_risk=0.9999 '
                           'correct_action_retention=1.0000 brier=0.1865 ece=0.1099')

if __name__ == '__main__':
    unittest.main()
