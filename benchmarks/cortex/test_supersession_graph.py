"""Fictional-only adversarial lineage tests. No real meetings or people."""
import copy
import unittest
from supersession_graph import audit_supersession

BASE = {'ground_truth': {'historical_decisions': [
    {'id': 'H0', 'record_ref': 'FICTIONAL-ARCHIVE-001'}],
    'decisions': [{'id': 'D3', 'supersedes': 'H0'}]}}


class SupersessionGraphTests(unittest.TestCase):
    def test_valid_single_predecessor(self):
        self.assertEqual([], audit_supersession(BASE))

    def test_empty_decisions(self):
        self.assertEqual([], audit_supersession({'ground_truth': {}}))

    def test_self_reference_exposed(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['decisions'][0]['supersedes'] = 'D3'
        self.assertEqual(['cyclic_supersession', 'self_supersession'], audit_supersession(f))

    def test_two_node_cycle(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['historical_decisions'][0]['supersedes'] = 'D3'
        self.assertEqual(['cyclic_supersession'], audit_supersession(f))

    def test_three_node_cycle(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['decisions'].append({'id': 'D4', 'supersedes': 'D3'})
        f['ground_truth']['historical_decisions'][0]['supersedes'] = 'D4'
        self.assertEqual(['cyclic_supersession'], audit_supersession(f))

    def test_missing_predecessor(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['decisions'][0]['supersedes'] = 'GHOST'
        self.assertEqual(['unresolved_predecessor'], audit_supersession(f))

    def test_duplicate_id_does_not_collapse(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['decisions'].append({'id': 'D3', 'supersedes': 'H0'})
        self.assertEqual(['duplicate_decision_id'], audit_supersession(f))

    def test_fork_requires_review(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['decisions'].append({'id': 'D4', 'supersedes': 'H0'})
        self.assertEqual(['forked_supersession_review'], audit_supersession(f))

    def test_long_acyclic_chain(self):
        f = {'ground_truth': {'decisions': [{'id': 'D0'}] + [
            {'id': f'D{i}', 'supersedes': f'D{i-1}'} for i in range(1, 150)]}}
        self.assertEqual([], audit_supersession(f))

    def test_invalid_ref_type(self):
        f = copy.deepcopy(BASE)
        f['ground_truth']['decisions'][0]['supersedes'] = ['H0']
        self.assertEqual(['invalid_predecessor_ref'], audit_supersession(f))

    def test_malformed_collection(self):
        self.assertEqual(['malformed_decision_collection'],
                         audit_supersession({'ground_truth': {'decisions': 'bad'}}))

    def test_malformed_decision_id(self):
        self.assertEqual(['invalid_decision_id'],
                         audit_supersession({'ground_truth': {'decisions': [{'id': ''}]}}))

    def test_malformed_top_level(self):
        self.assertEqual(['malformed_fixture'], audit_supersession(None))
        self.assertEqual(['malformed_ground_truth'], audit_supersession({}))


if __name__ == '__main__':
    unittest.main()
