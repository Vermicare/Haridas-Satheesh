"""Adversarial fictional-only expiry-aware dispatch candidate regression tests."""
import copy
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from authorization_guard_v02 import ContractError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from expiry_checked_delivery_v21 import ExpiryCheckedFictionalDelivery, FictionalDeliveryError
from test_revocable_signed_boundary_v11 import IDENTITY_KEY, APPROVAL_KEY, NOW, fixture


class ExpiryCheckedDispatchV21Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'fictional.sqlite3'
        self.store = FictionalRevocableStore(self.path)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.adapter = ExpiryCheckedFictionalDelivery(self.boundary)
        self.issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.scenario = fixture()
        self.scope = copy.deepcopy(self.scenario['authorization']['scope'])
        self.identity = self.issuer.issue_identity('fictional-user',
            '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        self.approval = self.issuer.issue_approval(self.scenario)
        self.nonce = self.scenario['authorization']['nonce']
        self.kw = {'identity_token': self.identity,
                   'approval_token': self.approval, 'now': NOW}

    def stage(self):
        return self.adapter.stage(self.scenario, self.scope, **self.kw)

    def dispatch(self, **changes):
        return self.adapter.dispatch(self.nonce, **{**self.kw, **changes})

    def test_01_valid_fake_dispatch_and_idempotent_replay(self):
        self.stage()
        self.assertFalse(self.dispatch()['outbox_replay'])
        self.assertTrue(self.dispatch()['outbox_replay'])
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_02_expired_approval_denies_pending_without_fake_effect(self):
        self.stage()
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.dispatch(now='2026-10-01T11:00:00Z')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)
        self.assertEqual(self.adapter.counts(self.nonce)['status'], 'pending')

    def test_03_expired_identity_denies_pending(self):
        self.stage()
        expired_identity = self.issuer.issue_identity('fictional-user',
            '2026-10-01T09:00:00Z', '2026-10-01T10:31:00Z')
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.dispatch(identity_token=expired_identity, now='2026-10-01T10:31:00Z')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)

    def test_04_not_yet_valid_time_denied(self):
        self.stage()
        with self.assertRaisesRegex(ContractError, 'not yet valid'):
            self.dispatch(now='2026-10-01T08:59:59Z')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)

    def test_05_malformed_clock_denied(self):
        self.stage()
        with self.assertRaises(ContractError):
            self.dispatch(now='not-a-time')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)

    def test_06_wrong_signed_identity_denied(self):
        self.stage()
        other = self.issuer.issue_identity('fictional-other',
            '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        with self.assertRaisesRegex(FictionalDeliveryError, 'identity/nonce mismatch'):
            self.dispatch(identity_token=other)
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)

    def test_07_other_signed_approval_denied(self):
        self.stage()
        other = copy.deepcopy(self.scenario)
        other['authorization']['nonce'] = 'fictional-other-nonce'
        other_approval = self.issuer.issue_approval(other)
        with self.assertRaisesRegex(FictionalDeliveryError, 'identity/nonce mismatch'):
            self.dispatch(approval_token=other_approval)
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)

    def test_08_revoked_pending_denied(self):
        self.stage()
        self.boundary.revoke(self.approval, now=NOW, reason='fictional stop')
        with self.assertRaisesRegex(FictionalDeliveryError, 'revoked'):
            self.dispatch()
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)
        self.assertEqual(self.adapter.counts(self.nonce)['status'], 'cancelled')

    def test_09_revoked_acked_replay_denied(self):
        self.stage(); self.dispatch()
        self.boundary.revoke(self.approval, now=NOW, reason='fictional stop')
        with self.assertRaisesRegex(FictionalDeliveryError, 'revoked'):
            self.dispatch()
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_10_expired_acked_replay_denied(self):
        self.stage(); self.dispatch()
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.dispatch(now='2026-10-01T11:00:00Z')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_11_restart_replay_does_not_duplicate_fake_effect(self):
        self.stage(); self.dispatch()
        reopened = ExpiryCheckedFictionalDelivery(FictionalRevocableBoundary(
            FictionalRevocableStore(self.path), IDENTITY_KEY, APPROVAL_KEY))
        self.assertTrue(reopened.dispatch(self.nonce, **self.kw)['outbox_replay'])
        self.assertEqual(reopened.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_12_precommit_crash_rolls_back_and_retries(self):
        self.stage()
        with self.assertRaisesRegex(RuntimeError, 'before commit'):
            self.dispatch(failure_point='before_commit')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)
        self.assertFalse(self.dispatch()['outbox_replay'])
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_13_concurrent_valid_attempts_single_fake_effect(self):
        self.stage()
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda _: self.dispatch(), range(12)))
        self.assertEqual(sum(not r['outbox_replay'] for r in results), 1)
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_14_invalid_signature_denied(self):
        self.stage()
        with self.assertRaises(ContractError):
            self.dispatch(approval_token=self.approval+'x')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)


if __name__ == '__main__':
    unittest.main()
