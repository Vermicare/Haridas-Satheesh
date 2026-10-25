"""Adversarial, fictional-only SQLite correction lineage contract tests."""
import copy
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from correction_ledger_v05 import FictionalCorrectionLedger, CorrectionContractError


ORIGINAL = {'synthetic': True, 'result': 'simulated-success',
            'action': 'ACT1', 'decision': 'D1', 'authorization': 'AUTH1',
            'nonce': 'fictional-nonce-1', 'external_actions': 0}


def request(parent='fictional-nonce-1', correction_id='C1', grant_nonce='correction-nonce-1'):
    return {'id': correction_id, 'parent_event_id': parent, 'approved_by': 'fictional-user',
            'decision': 'D1', 'action': 'ACT1',
            'grant': {'id': 'AUTH-C-' + correction_id, 'nonce': grant_nonce,
                      'approved_by': 'fictional-user',
                      'issued_at': '2026-10-01T10:00:00Z',
                      'expires_at': '2026-10-01T11:00:00Z',
                      'scope': {'operation': 'restore_due_date',
                                'original_nonce': 'fictional-nonce-1',
                                'parent_event_id': parent,
                                'new_due': '2026-10-02'}}}


class CorrectionLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'fictional.sqlite3'
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE receipts (nonce TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, receipt_json TEXT NOT NULL)')
            db.execute('INSERT INTO receipts VALUES (?,?,?)',
                       ('fictional-nonce-1', 'fixture-digest-not-cryptographic-proof',
                        json.dumps(ORIGINAL, sort_keys=True)))
        self.store = FictionalCorrectionLedger(self.path)

    def record(self, correction=None, ledger=None, **overrides):
        kw = {'principal': 'fictional-user', 'now': '2026-10-01T10:30:00Z',
              'trusted_principals': {'fictional-user'}}
        kw.update(overrides)
        return (ledger or self.store).record('fictional-nonce-1', correction or request(), **kw)

    def test_happy_path_preserves_original_receipt(self):
        r = self.record()
        self.assertFalse(r['idempotent_replay'])
        self.assertEqual(r['external_actions'], 0)
        self.assertEqual(self.store.correction_count(), 1)
        with closing(sqlite3.connect(self.path)) as db, db:
            self.assertEqual(json.loads(db.execute('SELECT receipt_json FROM receipts').fetchone()[0]), ORIGINAL)

    def test_restart_idempotent(self):
        first = self.record()
        replay = self.record(ledger=FictionalCorrectionLedger(self.path))
        self.assertTrue(replay['idempotent_replay'])
        self.assertEqual(self.store.correction_count(), 1)
        self.assertEqual(first['correction_id'], replay['correction_id'])

    def test_concurrent_attempts_one_new_event(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            rs = list(pool.map(lambda _: self.record(ledger=FictionalCorrectionLedger(self.path)), range(16)))
        self.assertEqual(sum(not r['idempotent_replay'] for r in rs), 1)
        self.assertEqual(self.store.correction_count(), 1)

    def test_precommit_failure_rolls_back(self):
        with self.assertRaisesRegex(RuntimeError, 'before commit'):
            self.record(failure_point='before_commit')
        self.assertEqual(self.store.correction_count(), 0)

    def test_postcommit_failure_retry(self):
        with self.assertRaisesRegex(RuntimeError, 'after commit'):
            self.record(failure_point='after_commit')
        self.assertTrue(self.record()['idempotent_replay'])
        self.assertEqual(self.store.correction_count(), 1)

    def test_fork_rejected(self):
        self.record()
        with self.assertRaisesRegex(CorrectionContractError, 'fork'):
            self.record(request(correction_id='C2', grant_nonce='correction-nonce-2'))
        self.assertEqual(self.store.correction_count(), 1)

    def test_linear_second_correction(self):
        self.record()
        r = self.record(request(parent='C1', correction_id='C2', grant_nonce='correction-nonce-2'))
        self.assertEqual(r['parent_event_id'], 'C1')
        self.assertEqual(self.store.correction_count(), 2)

    def test_unknown_parent_rejected(self):
        with self.assertRaisesRegex(CorrectionContractError, 'unknown'):
            self.record(request(parent='unknown'))

    def test_changed_request_same_id_rejected(self):
        self.record()
        bad = request()
        bad['grant']['scope']['new_due'] = '2026-10-03'
        with self.assertRaisesRegex(CorrectionContractError, 'already bound'):
            self.record(bad)

    def test_reused_grant_nonce_rejected(self):
        self.record()
        with self.assertRaisesRegex(CorrectionContractError, 'nonce replay'):
            self.record(request(parent='C1', correction_id='C2', grant_nonce='correction-nonce-1'))

    def test_expired_rejected_even_on_retry(self):
        self.record()
        with self.assertRaisesRegex(CorrectionContractError, 'expired'):
            self.record(now='2026-10-01T11:00:00Z')

    def test_forged_actor_rejected(self):
        bad = request()
        bad['approved_by'] = 'fictional-attacker'
        with self.assertRaisesRegex(CorrectionContractError, 'principal mismatch'):
            self.record(bad)

    def test_changed_scope_rejected(self):
        bad = request()
        bad['grant']['scope']['original_nonce'] = 'other'
        with self.assertRaisesRegex(CorrectionContractError, 'scope mismatch'):
            self.record(bad)

    def test_invalid_date_rejected(self):
        bad = request()
        bad['grant']['scope']['new_due'] = '2026-02-30'
        with self.assertRaisesRegex(CorrectionContractError, 'calendar date'):
            self.record(bad)

    def test_noncanonical_time_rejected(self):
        bad = request()
        bad['grant']['issued_at'] = '2026-10-01T10:00:00+00:00'
        with self.assertRaisesRegex(CorrectionContractError, 'canonical UTC'):
            self.record(bad)

    def test_missing_original_receipt_rejected(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('DELETE FROM receipts')
        with self.assertRaisesRegex(CorrectionContractError, 'not found'):
            self.record()

    def test_wrong_original_binding_rejected(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('UPDATE receipts SET receipt_json=?', (json.dumps({**ORIGINAL, 'decision': 'D2'}),))
        with self.assertRaisesRegex(CorrectionContractError, 'binding mismatch'):
            self.record()

    def test_no_memory_database(self):
        with self.assertRaises(ValueError):
            FictionalCorrectionLedger(':memory:')


if __name__ == '__main__':
    unittest.main()
