"""Fictional negative controls for v0.4 subject-level paired comparison."""
import json
import unittest
from rest_exposure_rate_v02 import Recording, Segment
from matched_opportunity_contract_v03 import Decision
from subject_level_v04 import SubjectTrial, aggregate, demo


class SubjectLevelTests(unittest.TestCase):
    def trial(self, n, *, gate_samples=(2000,), abstention_samples=(2000,),
              gate_direction='T1', abstention_direction='T1'):
        rec=Recording(100,6000)
        segments=(Segment(0,2000,'T0'),Segment(2000,4000,'T1'),Segment(4000,6000,'T0'))
        stamps=(0,1000,2000,3000,4000,5000)
        choices=[]
        for policy in ('ungated','abstention','gate'):
            for s in stamps:
                if policy=='gate':
                    direction=gate_direction if s in gate_samples else None
                elif policy=='abstention':
                    direction=abstention_direction if s in abstention_samples else None
                else:
                    direction='T1' if s in (2000,3000) else None
                choices.append(Decision(s,policy,direction))
        return SubjectTrial(f'F{n:03d}',rec,segments,stamps,tuple(choices))

    def test_paired_equal_coverage_returns_descriptive_zero(self):
        out=aggregate([self.trial(1),self.trial(2),self.trial(3)])
        self.assertEqual(out['unweighted_subject_mean_risk_delta'],0)
        self.assertEqual(out['decision'],'DIAGNOSTIC_ONLY')
        self.assertFalse(out['real_eeg_evaluated'])

    def test_one_unmatched_subject_withholds_entire_aggregate(self):
        out=aggregate([self.trial(1),self.trial(2),self.trial(3,gate_samples=())])
        self.assertEqual(out['decision'],'WITHHELD_UNMATCHED_SUBJECT')
        self.assertIsNone(out['unweighted_subject_mean_risk_delta'])
        self.assertEqual(out['incomparable_subjects'],1)

    def test_small_sample_withholds(self):
        out=aggregate([self.trial(1),self.trial(2)])
        self.assertEqual(out['decision'],'WITHHELD_INSUFFICIENT_SUBJECTS')
        self.assertIsNone(out['unweighted_subject_mean_risk_delta'])

    def test_rest_harm_not_hidden_by_equal_imagery_coverage(self):
        out=aggregate([self.trial(i,gate_samples=(0,2000)) for i in (1,2,3)])
        self.assertTrue(out['all_subjects_comparable'])
        self.assertTrue(out['any_rest_false_action_rate_regression'])
        self.assertEqual(out['decision'],'DIAGNOSTIC_TRADEOFF')

    def test_imagery_recall_regression_visible(self):
        out=aggregate([self.trial(i,gate_direction='T2') for i in (1,2,3)])
        self.assertTrue(out['any_correct_action_recall_regression'])
        self.assertEqual(out['decision'],'DIAGNOSTIC_TRADEOFF')

    def test_duplicate_subject_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            aggregate([self.trial(1),self.trial(1),self.trial(2)])

    def test_missing_grid_decision_fails_closed(self):
        t=self.trial(1)
        t=SubjectTrial(t.subject_id,t.recording,t.segments,t.opportunities,t.decisions[:-1])
        with self.assertRaisesRegex(ValueError,'incomplete'):
            aggregate([t,self.trial(2),self.trial(3)])

    def test_bad_subject_identifier_fails_closed(self):
        t=self.trial(1)
        for bad in ('S001','F1','',None,'F001/private'):
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,'subject identifier'):
                aggregate([SubjectTrial(bad,t.recording,t.segments,t.opportunities,t.decisions)])

    def test_invalid_parameters_fails_closed(self):
        for bad in (True,float('nan'),float('inf'),-1,1.1,'0.05'):
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,'tolerance'):
                aggregate([self.trial(1)],tolerance=bad)
        for bad in (True,0,-1,1.2):
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,'minimum'):
                aggregate([self.trial(1)],minimum_subjects=bad)

    def test_input_order_does_not_change_output(self):
        rows=[self.trial(1),self.trial(2),self.trial(3)]
        self.assertEqual(aggregate(rows),aggregate(list(reversed(rows))))

    def test_demo_reproducible_and_negative(self):
        self.assertEqual(demo(),demo())
        out=json.loads(demo())
        self.assertIsNone(out['unweighted_subject_mean_risk_delta'])
        self.assertFalse(out['real_eeg_evaluated'])


if __name__=='__main__':
    unittest.main()
