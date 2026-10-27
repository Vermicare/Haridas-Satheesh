"""No-network adversarial tests for atomic fictional revocation/receipt ordering."""
import copy
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from authorization_guard_v02 import ContractError
from authorization_store_v03 import FictionalDurableStore
from sandbox_issuer_v10 import FictionalIssuer, FictionalSignedBoundary
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore

IDENTITY_KEY = b'PUBLIC_TEST_ONLY_IDENTITY_KEY_2026'
APPROVAL_KEY = b'PUBLIC_TEST_ONLY_APPROVAL_KEY_2026'
NOW = '2026-10-01T10:30:00Z'


def fixture():
    s = json.loads(Path(__file__).with_name('scenario.json').read_text(encoding='utf-8'))
    s['proposed_decision']['scope'] = copy.deepcopy(s['authorization']['scope'])
    s['authorization'].update(issued_at='2026-10-01T10:00:00Z',
                              expires_at='2026-10-01T11:00:00Z', nonce='revocation-fixture-1')
    return s


class FictionalRevocationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / 'sandbox.sqlite3'
        self.store = FictionalRevocableStore(self.db)
        self.issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.s = fixture()
        self.scope = copy.deepcopy(self.s['authorization']['scope'])
        self.identity = self.issuer.issue_identity('fictional-user', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        self.approval = self.issuer.issue_approval(self.s)

    def execute(self, boundary=None, **kw):
        return (boundary or self.boundary).execute(self.s, self.scope,
            identity_token=kw.get('identity_token', self.identity),
            approval_token=kw.get('approval_token', self.approval),
            now=kw.get('now', NOW))

    def revoke(self, **kw):
        return self.boundary.revoke(kw.get('approval_token', self.approval),
                                    now=kw.get('now', NOW), reason=kw.get('reason', 'fictional operator withdrew approval'))

    def test_valid_first_use_and_replay_before_revocation(self):
        first = self.execute()
        second = self.execute()
        self.assertFalse(first['idempotent_replay'])
        self.assertTrue(second['idempotent_replay'])
        self.assertEqual(first['external_actions'], 0)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_revoked_before_first_use_blocks_receipt(self):
        result = self.revoke()
        self.assertTrue(result['new_revocation'])
        with self.assertRaisesRegex(ContractError, 'revoked'):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 0)

    def test_revoked_after_first_use_blocks_replay_but_preserves_receipt(self):
        first = self.execute()
        self.revoke()
        with self.assertRaisesRegex(ContractError, 'revoked'):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 1)
        self.assertEqual(first['external_actions'], 0)

    def test_revocation_persists_across_restart(self):
        self.revoke()
        restarted = FictionalRevocableBoundary(FictionalRevocableStore(self.db),
                                                IDENTITY_KEY, APPROVAL_KEY)
        with self.assertRaisesRegex(ContractError, 'revoked'):
            self.execute(boundary=restarted)
        self.assertEqual(self.store.revocation_count(), 1)

    def test_repeat_revocation_does_not_rewrite_first_event(self):
        self.assertTrue(self.revoke()['new_revocation'])
        self.assertFalse(self.revoke(now='2026-10-01T10:31:00Z', reason='different reason')['new_revocation'])
        with self.store._connect() as db:
            row = db.execute('SELECT revoked_at,reason FROM fictional_revocations').fetchone()
        self.assertEqual(row, (NOW, 'fictional operator withdrew approval'))
        self.assertEqual(self.store.revocation_count(), 1)

    def test_baseline_v10_has_no_revocation_gate_negative_control(self):
        self.revoke()
        # Intentional negative result: the original v1.0 path does not consult
        # the revocation table. This does NOT exploit any private system.
        baseline = FictionalSignedBoundary(IDENTITY_KEY, APPROVAL_KEY)
        old = baseline.execute(FictionalDurableStore(self.db), self.s, self.scope,
                               identity_token=self.identity, approval_token=self.approval, now=NOW)
        self.assertFalse(old['idempotent_replay'])
        self.assertEqual(old['external_actions'], 0)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_concurrent_revocation_and_execute_have_serializable_outcome(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_revoke = pool.submit(self.revoke)
            f_execute = pool.submit(self.execute)
            self.assertTrue(f_revoke.result()['synthetic'])
            try:
                r = f_execute.result()
                self.assertEqual(r['external_actions'], 0)
                self.assertEqual(self.store.receipt_count(), 1)
            except ContractError as exc:
                self.assertIn('revoked', str(exc))
                self.assertEqual(self.store.receipt_count(), 0)
        with self.assertRaisesRegex(ContractError, 'revoked'):
            self.execute()
        self.assertEqual(self.store.revocation_count(), 1)

    def test_many_attempts_after_revocation_are_denied(self):
        self.revoke()
        def worker(_):
            try:
                self.execute()
                return 'INCORRECT_ACCEPT'
            except ContractError:
                return 'DENIED'
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(worker, range(12)))
        self.assertEqual(results, ['DENIED'] * 12)
        self.assertEqual(self.store.receipt_count(), 0)

    def test_different_approval_token_not_revoked(self):
        self.revoke()
        s2 = copy.deepcopy(self.s)
        s2['authorization']['nonce'] = 'revocation-fixture-2'
        token2 = self.issuer.issue_approval(s2)
        r = self.boundary.execute(s2, self.scope, identity_token=self.identity,
                                  approval_token=token2, now=NOW)
        self.assertFalse(r['idempotent_replay'])
        self.assertEqual(self.store.receipt_count(), 1)

    def test_invalid_signature_cannot_be_revoked_as_valid_approval(self):
        with self.assertRaises(ContractError):
            self.revoke(approval_token=self.approval + 'x')
        self.assertEqual(self.store.revocation_count(), 0)

    def test_wrong_identity_rejected_before_receipt(self):
        other = self.issuer.issue_identity('fictional-other', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        with self.assertRaisesRegex(ContractError, 'identity/approval mismatch'):
            self.execute(identity_token=other)
        self.assertEqual(self.store.receipt_count(), 0)

    def test_scope_escalation_rejected_before_receipt(self):
        self.scope['new_due'] = '2026-10-09'
        with self.assertRaisesRegex(ContractError, 'not bound'):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 0)

    def test_expiry_still_enforced(self):
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.execute(now='2026-10-01T11:00:00Z')
        self.assertEqual(self.store.receipt_count(), 0)

    def test_missing_revocation_table_fails_closed(self):
        with self.store._connect() as db:
            db.execute('DROP TABLE fictional_revocations')
        with self.assertRaises(sqlite3.OperationalError):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 0)

    def test_bad_revocation_reason_and_time_rejected(self):
        with self.assertRaises(ContractError):
            self.revoke(reason='  ')
        with self.assertRaises(ContractError):
            self.revoke(now='not-a-time')
        self.assertEqual(self.store.revocation_count(), 0)


if __name__ == '__main__':
    unittest.main()
