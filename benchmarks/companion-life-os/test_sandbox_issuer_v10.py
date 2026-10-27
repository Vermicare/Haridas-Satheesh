"""Adversarial tests for public fictional issuer signatures + real v0.3 SQLite receipts."""
import copy
import hashlib
import hmac
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from authorization_guard_v02 import ContractError
from authorization_store_v03 import FictionalDurableStore
from sandbox_issuer_v10 import FictionalIssuer, FictionalSignedBoundary, _b64

IDENTITY_KEY = b'PUBLIC_TEST_ONLY_IDENTITY_KEY_2026'
APPROVAL_KEY = b'PUBLIC_TEST_ONLY_APPROVAL_KEY_2026'
NOW = '2026-10-01T10:30:00Z'


def fixture():
    scenario = json.loads(Path(__file__).with_name('scenario.json').read_text(encoding='utf-8'))
    scenario['proposed_decision']['scope'] = copy.deepcopy(scenario['authorization']['scope'])
    scenario['authorization'].update(issued_at='2026-10-01T10:00:00Z',
                                     expires_at='2026-10-01T11:00:00Z', nonce='signed-fictional-1')
    return scenario


class FictionalSignedBoundaryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / 'sandbox.sqlite3'
        self.store = FictionalDurableStore(self.db)
        self.s = fixture()
        self.scope = copy.deepcopy(self.s['authorization']['scope'])
        self.issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.boundary = FictionalSignedBoundary(IDENTITY_KEY, APPROVAL_KEY)
        self.identity = self.issuer.issue_identity('fictional-user', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        self.approval = self.issuer.issue_approval(self.s)

    def execute(self, **kwargs):
        args = dict(identity_token=self.identity, approval_token=self.approval, now=NOW)
        args.update(kwargs)
        return self.boundary.execute(self.store, self.s, self.scope, **args)

    def test_signed_fictional_happy_path_zero_external_actions(self):
        receipt = self.execute()
        self.assertFalse(receipt['idempotent_replay'])
        self.assertEqual(receipt['external_actions'], 0)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_restart_idempotent_receipt(self):
        first = self.execute()
        second = self.boundary.execute(FictionalDurableStore(self.db), self.s, self.scope,
                                       identity_token=self.identity, approval_token=self.approval, now=NOW)
        self.assertTrue(second['idempotent_replay'])
        self.assertEqual(first['nonce'], second['nonce'])
        self.assertEqual(self.store.receipt_count(), 1)

    def test_parallel_attempts_create_only_one_receipt(self):
        def worker(_):
            return self.boundary.execute(FictionalDurableStore(self.db), self.s, self.scope,
                                         identity_token=self.identity, approval_token=self.approval, now=NOW)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(worker, range(12)))
        self.assertEqual(sum(not x['idempotent_replay'] for x in results), 1)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_unsigned_principal_string_cannot_replace_identity(self):
        with self.assertRaises(ContractError):
            self.execute(identity_token='fictional-user')
        self.assertEqual(self.store.receipt_count(), 0)

    def test_fictional_impersonation_token_rejected(self):
        other = self.issuer.issue_identity('fictional-attacker', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        with self.assertRaisesRegex(ContractError, 'identity/approval mismatch'):
            self.execute(identity_token=other)
        self.assertEqual(self.store.receipt_count(), 0)

    def test_modified_identity_signature_rejected(self):
        body, signature = self.identity.split('.')
        corrupted = body + '.' + ('A' if signature[0] != 'A' else 'B') + signature[1:]
        with self.assertRaisesRegex(ContractError, 'signature'):
            self.execute(identity_token=corrupted)
        self.assertEqual(self.store.receipt_count(), 0)

    def test_modified_approval_signature_rejected(self):
        body, signature = self.approval.split('.')
        corrupted = body + '.' + ('A' if signature[0] != 'A' else 'B') + signature[1:]
        with self.assertRaisesRegex(ContractError, 'signature'):
            self.execute(approval_token=corrupted)
        self.assertEqual(self.store.receipt_count(), 0)

    def test_changed_scope_rejected_even_with_valid_old_signature(self):
        self.scope['new_due'] = '2026-10-09'
        with self.assertRaisesRegex(ContractError, 'not bound'):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 0)

    def test_changed_fictional_scenario_rejected(self):
        self.s['evidence'][0]['content']['due'] = '2026-10-09'
        with self.assertRaisesRegex(ContractError, 'not bound'):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 0)

    def test_changed_connector_rejected(self):
        self.s['simulated_action']['connector'] = 'real-connector'
        with self.assertRaisesRegex(ContractError, 'not bound'):
            self.execute()
        self.assertEqual(self.store.receipt_count(), 0)

    def test_identity_expiry_rejected(self):
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.execute(now='2026-10-01T12:00:00Z')
        self.assertEqual(self.store.receipt_count(), 0)

    def test_approval_expiry_rejected(self):
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.execute(now='2026-10-01T11:00:00Z')
        self.assertEqual(self.store.receipt_count(), 0)

    def test_wrong_signing_key_rejected(self):
        other = FictionalIssuer(b'OTHER_PUBLIC_IDENTITY_TEST_KEY_1', b'OTHER_PUBLIC_APPROVAL_TEST_KEY_1')
        with self.assertRaisesRegex(ContractError, 'signature'):
            self.execute(identity_token=other.issue_identity('fictional-user', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z'))
        self.assertEqual(self.store.receipt_count(), 0)

    def test_duplicate_claim_keys_rejected_even_if_signed(self):
        # Construct a token with a valid HMAC over noncanonical, duplicate-key JSON.
        raw = b'{"kind":"identity","kind":"identity","audience":"fictional-companion-task-store-v1","subject":"fictional-user","issued_at":"2026-10-01T09:00:00Z","expires_at":"2026-10-01T12:00:00Z"}'
        body = _b64(raw)
        forged = body + '.' + _b64(hmac.new(IDENTITY_KEY, body.encode('ascii'), hashlib.sha256).digest())
        with self.assertRaises(ContractError):
            self.execute(identity_token=forged)
        self.assertEqual(self.store.receipt_count(), 0)

    def test_same_key_for_two_issuers_rejected(self):
        with self.assertRaises(ValueError):
            FictionalIssuer(IDENTITY_KEY, IDENTITY_KEY)


if __name__ == '__main__':
    unittest.main()
