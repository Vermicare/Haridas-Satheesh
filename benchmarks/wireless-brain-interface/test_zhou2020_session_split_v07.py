"""Metadata-only negative controls and pinned original census integration."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from zhou2020_event_concentration_v06 import PINNED_JSON_SHA256
from test_zhou2020_event_concentration_v06 import fictional_census
from zhou2020_session_split_v07 import assign, build

SOURCE = Path(__file__).with_name('frozen_v05_census.json')


class SessionIndexSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.is_real=SOURCE.exists()
        if cls.is_real:
            raw=SOURCE.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==PINNED_JSON_SHA256
            cls.source=json.loads(raw)
        else:
            cls.source=fictional_census()

    def test_original_source_counts_and_disjoint(self):
        result=build(self.source)
        self.assertEqual(len(result['entries']),833)
        self.assertEqual(sum(result['role_file_counts'].values()),833)
        self.assertEqual(len({x['event_tsv_path'] for x in result['entries']}),833)
        self.assertTrue(result['candidate_not_confirmatory'])

    def test_latest_available_session_reserved_per_subject(self):
        result=build(self.source)
        for subject in range(1,21):
            entries=[x for x in result['entries'] if x['subject']==subject]
            top=max(x['session_index'] for x in entries)
            self.assertEqual({x['session_index'] for x in entries if x['role']=='test_candidate'},{top})
            self.assertEqual(len({x['role'] for x in entries}),3)
        self.assertEqual(result['subject_allocations']['20']['candidate_test_session_index'],5)
        self.assertEqual(result['subject_allocations']['1']['candidate_test_session_index'],6)

    def test_irregular_run_counts_preserved(self):
        result=build(self.source)
        if not self.is_real:
            self.skipTest('requires pinned original v0.5 census JSON')
        selected=[x['run_index'] for x in result['entries'] if x['subject']==20 and x['session_index']==4]
        self.assertEqual(len(selected),9)
        self.assertEqual(len(set(selected)),9)

    def test_count_and_label_independence_of_assignment(self):
        original, _=assign(self.source['file_provenance'])
        modified=copy.deepcopy(self.source['file_provenance'])
        for r in modified:
            r['event_rows']=999999
            r['trial_label']='DO_NOT_USE'
        altered, _=assign(modified)
        self.assertEqual(original,altered)

    def test_duplicate_run_key_rejected(self):
        modified=copy.deepcopy(self.source['file_provenance'])
        modified[1]['path']=modified[0]['path']
        with self.assertRaisesRegex(ValueError,'duplicate_subject_session_run'):
            assign(modified)

    def test_path_subject_mismatch_rejected(self):
        modified=copy.deepcopy(self.source['file_provenance'])
        modified[0]['subject']=2
        with self.assertRaisesRegex(ValueError,'path_metadata_mismatch'):
            assign(modified)

    def test_path_session_mismatch_rejected(self):
        modified=copy.deepcopy(self.source['file_provenance'])
        modified[0]['session']=1
        with self.assertRaisesRegex(ValueError,'path_metadata_mismatch'):
            assign(modified)

    def test_boolean_subject_rejected(self):
        modified=copy.deepcopy(self.source['file_provenance'])
        modified[0]['subject']=True
        with self.assertRaisesRegex(ValueError,'invalid_subject_session_path'):
            assign(modified)

    def test_source_mutation_rejected_by_cli(self):
        if not self.is_real:
            self.skipTest('requires pinned original v0.5 census JSON')
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'changed.json'
            source.write_bytes(SOURCE.read_bytes()+b' ')
            run=subprocess.run([sys.executable,str(Path(__file__).with_name('zhou2020_session_split_v07.py')),str(source)],capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            self.assertIn('byte hash mismatch',run.stderr+run.stdout)

    def test_candidate_not_real_outcome_claim(self):
        result=build(self.source)
        self.assertFalse(result['original_npz_bytes_verified'])
        self.assertFalse(result['event_to_npz_pairing_verified'])
        self.assertFalse(result['chronological_acquisition_dates_verified'])
        self.assertTrue(result['earlier_exploratory_event_label_preview_disclosed'])
        self.assertFalse(result['heldout_outcomes_accessed_by_this_program'])
        self.assertFalse(result['maturity_advanced'])

if __name__=='__main__':unittest.main()
