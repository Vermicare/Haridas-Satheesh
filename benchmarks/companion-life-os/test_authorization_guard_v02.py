"""Adversarial fictional authorization tests, including baseline negative controls."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from authorization_guard_v02 import ContractError, simulate_once
from validator import can_execute

SOURCE = Path(__file__).with_name('scenario.json')


def scenario():
    s = json.loads(SOURCE.read_text())
    s['proposed_decision']['scope'] = copy.deepcopy(s['authorization']['scope'])
    s['authorization'].update(issued_at='2026-10-01T10:00:00Z',
                              expires_at='2026-10-01T11:00:00Z', nonce='fictional-nonce-1')
    return s


class AuthorizationGuardTests(unittest.TestCase):
    def setUp(self):
        self.s = scenario()
        self.scope = copy.deepcopy(self.s['authorization']['scope'])
        self.consumed = set()

    def execute(self, **kwargs):
        params = dict(principal='fictional-user', now='2026-10-01T10:30:00Z',
                      consumed=self.consumed, trusted_principals={'fictional-user'})
        params.update(kwargs)
        return simulate_once(self.s, self.scope, **params)

    def test_clean_receipt_no_external_action(self):
        result = self.execute()
        self.assertEqual((result['result'], result['external_actions']), ('simulated-success', 0))
        self.assertEqual(self.consumed, {'fictional-nonce-1'})

    def test_replay_blocked(self):
        self.execute()
        with self.assertRaisesRegex(ContractError, 'replayed'):
            self.execute()

    def test_expired_blocked(self):
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.execute(now='2026-10-01T11:00:00Z')

    def test_future_grant_blocked(self):
        with self.assertRaises(ContractError):
            self.execute(now='2026-10-01T09:59:59Z')

    def test_spoofed_approval_actor_blocked(self):
        self.s['authorization']['approved_by'] = 'fictional-attacker'
        with self.assertRaises(ContractError):
            self.execute()

    def test_untrusted_principal_blocked(self):
        with self.assertRaises(ContractError):
            self.execute(trusted_principals=set())

    def test_changed_decision_scope_blocked(self):
        self.s['proposed_decision']['scope']['new_due'] = '2026-10-09'
        with self.assertRaises(ContractError):
            self.execute()

    def test_wider_requested_scope_blocked(self):
        self.scope['delete_task'] = True
        with self.assertRaises(ContractError):
            self.execute()

    def test_untrusted_evidence_blocked(self):
        self.s['proposed_decision']['evidence'].append('E3')
        with self.assertRaises(ContractError):
            self.execute()

    def test_unsupported_connector_blocked(self):
        self.s['simulated_action']['connector'] = 'real-task-store'
        with self.assertRaises(ContractError):
            self.execute()

    def test_action_id_mismatch_blocked(self):
        self.s['simulated_action']['authorization'] = 'OTHER'
        with self.assertRaises(ContractError):
            self.execute()

    def test_missing_decision_scope_blocked(self):
        del self.s['proposed_decision']['scope']
        with self.assertRaises(ContractError):
            self.execute()

    def test_missing_nonce_blocked(self):
        self.s['authorization']['nonce'] = ''
        with self.assertRaises(ContractError):
            self.execute()

    def test_bad_timestamp_blocked(self):
        with self.assertRaises(ContractError):
            self.execute(now='tomorrow')

    def test_negative_control_baseline_accepts_spoofed_actor(self):
        # Finding: committed v0.1 checks IDs and scope, not approved_by identity.
        self.s['authorization']['approved_by'] = 'fictional-attacker'
        self.assertTrue(can_execute(self.s, self.s['authorization'], self.scope))

    def test_negative_control_baseline_replay_has_no_state(self):
        # Finding: v0.1 accepts the same authorization twice; it has no consumption state.
        self.assertTrue(can_execute(self.s, self.s['authorization'], self.scope))
        self.assertTrue(can_execute(self.s, self.s['authorization'], self.scope))


if __name__ == '__main__':
    unittest.main()
