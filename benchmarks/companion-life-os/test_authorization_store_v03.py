"""Clean-room fictional restart, concurrent writer, crash, scope and replay tests."""
import copy
import sqlite3
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from authorization_store_v03 import FictionalDurableStore
from authorization_guard_v02 import ContractError
import json


def scenario():
    s = json.loads(Path(__file__).with_name("scenario.json").read_text())
    s["proposed_decision"]["scope"] = copy.deepcopy(s["authorization"]["scope"])
    s["authorization"].update(issued_at="2026-10-01T10:00:00Z",
                              expires_at="2026-10-01T11:00:00Z", nonce="fictional-nonce-1")
    return s


class DurableStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'fictional.sqlite3'
        self.store = FictionalDurableStore(self.path)
        self.s = scenario()
        self.scope = copy.deepcopy(self.s['authorization']['scope'])

    def run_once(self, store=None, scenario_override=None, scope_override=None, **kwargs):
        args = dict(principal='fictional-user', now='2026-10-01T10:30:00Z',
                    trusted_principals={'fictional-user'})
        args.update(kwargs)
        return (store or self.store).execute(scenario_override or self.s,
                                             scope_override or self.scope, **args)

    def test_first_action_fictional_only(self):
        r = self.run_once()
        self.assertEqual(r['external_actions'], 0)
        self.assertFalse(r['idempotent_replay'])
        self.assertEqual(self.store.receipt_count(), 1)

    def test_restart_returns_same_receipt_without_new_action(self):
        first = self.run_once()
        restarted = FictionalDurableStore(self.path)
        second = self.run_once(store=restarted)
        self.assertTrue(second['idempotent_replay'])
        self.assertEqual({k:v for k,v in second.items() if k != 'idempotent_replay'},
                         {k:v for k,v in first.items() if k != 'idempotent_replay'})
        self.assertEqual(restarted.receipt_count(), 1)

    def test_concurrent_writers_create_one_receipt(self):
        def worker(_):
            return self.run_once(store=FictionalDurableStore(self.path))
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(worker, range(16)))
        self.assertEqual(sum(not r['idempotent_replay'] for r in results), 1)
        self.assertEqual(sum(r['idempotent_replay'] for r in results), 15)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_precommit_crash_rolls_back(self):
        with self.assertRaisesRegex(RuntimeError, 'before commit'):
            self.run_once(failure_point='before_commit')
        self.assertEqual(self.store.receipt_count(), 0)
        self.assertFalse(self.run_once()['idempotent_replay'])

    def test_postcommit_crash_recovers_idempotently(self):
        with self.assertRaisesRegex(RuntimeError, 'after commit'):
            self.run_once(failure_point='after_commit')
        self.assertEqual(self.store.receipt_count(), 1)
        self.assertTrue(self.run_once(store=FictionalDurableStore(self.path))['idempotent_replay'])

    def test_nonce_collision_different_scope_rejected(self):
        self.run_once()
        changed = copy.deepcopy(self.s)
        changed['proposed_decision']['scope']['new_due'] = '2026-10-07'
        changed['authorization']['scope']['new_due'] = '2026-10-07'
        with self.assertRaisesRegex(ContractError, 'nonce already bound'):
            self.run_once(scenario_override=changed, scope_override=changed['authorization']['scope'])
        self.assertEqual(self.store.receipt_count(), 1)

    def test_wrong_principal_does_not_reveal_existing_receipt(self):
        self.run_once()
        with self.assertRaises(ContractError):
            self.run_once(principal='fictional-attacker', trusted_principals={'fictional-attacker'})

    def test_expired_retry_fails_closed(self):
        self.run_once()
        with self.assertRaisesRegex(ContractError, 'expired'):
            self.run_once(now='2026-10-01T11:00:00Z')

    def test_corrupt_db_is_not_silently_recreated(self):
        self.run_once()
        self.path.write_bytes(b'not-a-sqlite-database')
        with self.assertRaises(sqlite3.DatabaseError):
            self.run_once()

    def test_memory_database_rejected(self):
        with self.assertRaises(ValueError):
            FictionalDurableStore(':memory:')


if __name__ == '__main__':
    unittest.main()
