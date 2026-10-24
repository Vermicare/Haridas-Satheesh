"""Fictional-only regression tests; no physical cooling measurements."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from fixture_origin_gate import RAW_HEADER, INSTRUMENT_HEADER, REQUIRED, check


class OriginGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        d=Path(self.temp.name)
        self.raw=d/'raw.csv'; self.manifest=d/'instrument.csv'; self.plan=d/'plan.json'
        self.record={k:'' for k in RAW_HEADER}
        self.record.update(run_id='A',condition='ambient',notes='unverified example')
        self.instruments=[]
        for i,name in enumerate(sorted(REQUIRED)):
            row={k:'value' for k in INSTRUMENT_HEADER}
            row.update(instrument_id=f'ID{i}',measurement=name,notes='')
            self.instruments.append(row)
        self.plan_dict=dict(geometry_id='G1',ambient_position='P1',target_position='P2',
                            surface_position='P3',power_boundary='input')
        self.write()

    def write(self):
        with self.raw.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=RAW_HEADER);writer.writeheader();writer.writerow(self.record)
        with self.manifest.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=INSTRUMENT_HEADER);writer.writeheader();writer.writerows(self.instruments)
        self.plan.write_text(json.dumps(self.plan_dict))

    def codes(self,mode='bench'):
        return check(self.raw,self.manifest,self.plan,mode)['problems']

    def test_unverified_even_when_structure_passes(self):
        r=check(self.raw,self.manifest,self.plan)
        self.assertEqual(r['status'],'STRUCTURE_ONLY_ORIGIN_UNVERIFIED')
        self.assertFalse(r['physical_origin_authenticated'])
        self.assertFalse(r['performance_claim_permitted'])

    def test_fictional_raw_rejected(self):
        self.record['notes']='FICTIONAL DATA / DO NOT USE';self.write()
        self.assertIn('EXPLICIT_FICTIONAL_RAW',self.codes())

    def test_synthetic_plan_rejected(self):
        self.plan_dict['comment']='SYNTHETIC fixture';self.write()
        self.assertIn('EXPLICIT_FICTIONAL_PLAN',self.codes())

    def test_mock_instrument_rejected(self):
        self.instruments[0]['notes']='MOCK SENSOR';self.write()
        self.assertIn('EXPLICIT_FICTIONAL_INSTRUMENT',self.codes())

    def test_missing_instrument_provenance(self):
        self.instruments[0]['accuracy_or_uncertainty']='TBD';self.write()
        self.assertIn('INSTRUMENT_PROVENANCE_TBD',self.codes())

    def test_missing_instrument(self):
        self.instruments.pop();self.write()
        self.assertIn('INSTRUMENT_COVERAGE',self.codes())

    def test_missing_geometry(self):
        self.plan_dict['target_position']='TBD';self.write()
        self.assertIn('GEOMETRY_TBD',self.codes())

    def test_wrong_header(self):
        self.raw.write_text('run_id,notes\nA,ok\n')
        self.assertIn('RAW_HEADER',self.codes())

    def test_malformed_csv_row_rejected_not_crash(self):
        with self.raw.open('a') as f: f.write('extra,field,not,enough\n')
        self.assertIn('RAW_ROW',self.codes())

    def test_nonobject_plan(self):
        self.plan.write_text('[]')
        self.assertIn('PLAN_OBJECT',self.codes())

    def test_dry_run_fictional_not_claimed_physical(self):
        self.record['notes']='FICTIONAL';self.write()
        r=check(self.raw,self.manifest,self.plan,'dry-run')
        self.assertEqual(r['status'],'STRUCTURE_ONLY_ORIGIN_UNVERIFIED')
        self.assertFalse(r['physical_origin_authenticated'])


    def test_explicit_fictional_raw_marker_in_other_column_rejected(self):
        self.record['surface_temp_c'] = 'FICTIONAL 27'
        self.write()
        self.assertIn('EXPLICIT_FICTIONAL_RAW', self.codes())

    def test_explicit_mock_optional_instrument_rejected(self):
        extra = {key: 'value' for key in INSTRUMENT_HEADER}
        extra.update(instrument_id='EXTRA', measurement='optional_thermal_camera',
                     notes='MOCK DEVICE')
        self.instruments.append(extra)
        self.write()
        self.assertIn('EXPLICIT_FICTIONAL_INSTRUMENT', self.codes())

    def test_unmarked_optional_instrument_is_allowed(self):
        extra = {key: 'value' for key in INSTRUMENT_HEADER}
        extra.update(instrument_id='EXTRA', measurement='optional_thermal_camera',
                     notes='')
        self.instruments.append(extra)
        self.write()
        self.assertEqual(check(self.raw, self.manifest, self.plan)['status'],
                         'STRUCTURE_ONLY_ORIGIN_UNVERIFIED')

if __name__=='__main__':
    unittest.main()
