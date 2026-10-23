#!/usr/bin/env python3
"""Adversarial tests for fictional archive integrity and frozen-only transfer."""
import copy
import json
import unittest
from pathlib import Path
from baseline import baseline
from evaluator import evaluate
from fixture_integrity_preflight import audit_fixture
from lineage_and_shift import audit_archive
from run_lineage_shift import report

ROOT = Path(__file__).resolve().parent

class ArchiveAndShiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads((ROOT/'fixture.json').read_text())
        cls.independent = json.loads((ROOT/'independent_scenario_v03.json').read_text())

    def test_frozen_predecessor_remains_unresolved(self):
        self.assertIn('unresolved_predecessor', audit_fixture(self.frozen))

    def test_independent_synthetic_fixture_structurally_linked(self):
        self.assertEqual([], audit_fixture(self.independent))
        self.assertEqual([], audit_archive(self.independent))

    def test_missing_archive_record_rejected(self):
        f = copy.deepcopy(self.independent)
        f['history']['records'] = []
        self.assertIn('unresolved_archive_ref', audit_archive(f))
        self.assertEqual([], audit_fixture(f)) # earlier gate misses it

    def test_wrong_archive_decision_id_rejected(self):
        f = copy.deepcopy(self.independent)
        f['history']['records'][0]['decision_id'] = 'OTHER'
        self.assertIn('archive_decision_id_mismatch', audit_archive(f))

    def test_duplicate_archive_reference_rejected(self):
        f = copy.deepcopy(self.independent)
        f['history']['records'].append(copy.deepcopy(f['history']['records'][0]))
        self.assertIn('duplicate_archive_ref', audit_archive(f))

    def test_empty_archive_text_rejected(self):
        f = copy.deepcopy(self.independent)
        f['history']['records'][0]['text'] = '  '
        self.assertIn('archive_record_missing_text', audit_archive(f))

    def test_missing_historical_declaration_rejected(self):
        f = copy.deepcopy(self.independent)
        del f['ground_truth']['historical_decisions'][0]['record_ref']
        self.assertIn('invalid_historical_declaration', audit_archive(f))

    def test_duplicate_historical_ids_rejected(self):
        f = copy.deepcopy(self.independent)
        f['ground_truth']['historical_decisions'].append(copy.deepcopy(f['ground_truth']['historical_decisions'][0]))
        self.assertIn('duplicate_historical_id', audit_archive(f))

    def test_unknown_supersession_rejected(self):
        f = copy.deepcopy(self.independent)
        f['ground_truth']['decisions'][0]['supersedes'] = 'GHOST'
        self.assertIn('unresolved_predecessor', audit_fixture(f))

    def test_frozen_scores_perfect_but_not_ready(self):
        s = evaluate(self.frozen, baseline(self.frozen))
        self.assertEqual(1.0, s['metrics']['decisions']['f1'])
        self.assertIn('unresolved_predecessor', audit_fixture(self.frozen))

    def test_independent_baseline_abstains_everywhere(self):
        predicted = baseline(self.independent)
        self.assertTrue(all(not objects for objects in predicted.values()))
        s = evaluate(self.independent, predicted)
        self.assertTrue(all(s['metrics'][k]['f1'] == 0.0 for k in predicted))

    def test_report_distinguishes_structural_from_semantic(self):
        r = report()
        self.assertEqual('TBD', r['real_workflow_results'])
        self.assertFalse(r['cases']['independent_fictional']['archive_authenticity_verified'])
        self.assertFalse(r['cases']['independent_fictional']['semantic_ground_truth_reviewed_by_humans'])
        self.assertEqual(['unresolved_predecessor'],r['cases']['frozen']['fixture_preflight_codes'])

if __name__ == '__main__':
    unittest.main()
