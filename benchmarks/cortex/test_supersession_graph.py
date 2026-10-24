"""Fictional-only adversarial lineage tests. No real meetings or people."""
import copy
import unittest
from fixture_integrity_preflight import audit_fixture
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

    def test_earlier_membership_gate_misses_self_loop(self):
        f = {'meeting': {'utterances': [{'id': 'n01'}]},
             'ground_truth': {'historical_decisions': [
                 {'id': 'H0', 'record_ref': 'FICTIONAL-ARCHIVE'}],
                 'decisions': [{'id': 'D3', 'source': ['n01'],
                                'statement': 'Fictional approval', 'status': 'active',
                                'supersedes': 'D3'}]}}
        self.assertEqual([], audit_fixture(f))  # prior membership-only gate
        self.assertIn('self_supersession', audit_supersession(f))

    def test_earlier_membership_gate_misses_two_node_cycle(self):
        f = {'meeting': {'utterances': [{'id': 'n01'}]},
             'ground_truth': {'historical_decisions': [
                 {'id': 'H0', 'record_ref': 'FICTIONAL-ARCHIVE', 'supersedes': 'D3'}],
                 'decisions': [{'id': 'D3', 'source': ['n01'],
                                'statement': 'Fictional approval', 'status': 'active',
                                'supersedes': 'H0'}]}}
        self.assertEqual([], audit_fixture(f))  # prior membership-only gate
        self.assertIn('cyclic_supersession', audit_supersession(f))

    def test_malformed_top_level(self):
        self.assertEqual(['malformed_fixture'], audit_supersession(None))
        self.assertEqual(['malformed_ground_truth'], audit_supersession({}))


    def test_very_long_acyclic_history_without_recursive_walk(self):
        # Fictional stress fixture: tests linear traversal without wall-clock
        # assertions, which are unstable across CI operating systems.
        rows = [{'id': 'D0'}] + [
            {'id': f'D{i}', 'supersedes': f'D{i-1}'}
            for i in range(1, 12000)
        ]
        self.assertEqual([], audit_supersession(
            {'ground_truth': {'decisions': rows}}))

    def test_seeded_graph_cycle_oracle(self):
        # Independently compare cycle presence to a deliberately simple
        # quadratic reference on small, fictional graphs.
        import random
        rng = random.Random(20261024)
        for trial in range(80):
            rows = [{'id': f'D{i}'} for i in range(20)]
            for row in rows:
                if rng.randrange(4):
                    row['supersedes'] = f'D{rng.randrange(20)}'
            graph = {r['id']: r['supersedes'] for r in rows
                     if 'supersedes' in r}
            expected_cycle = False
            for start in graph:
                seen = set()
                node = start
                while node in graph:
                    if node in seen:
                        expected_cycle = True
                        break
                    seen.add(node)
                    node = graph[node]
                if expected_cycle:
                    break
            actual = audit_supersession(
                {'ground_truth': {'decisions': rows}})
            self.assertEqual(expected_cycle,
                             'cyclic_supersession' in actual,
                             msg=f'fictional trial {trial}')



if __name__ == '__main__':
    unittest.main()
