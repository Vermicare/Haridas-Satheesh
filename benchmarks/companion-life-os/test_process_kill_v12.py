"""Process-kill crash-window tests for the FICTIONAL Companion SQLite boundary.

This runs only a disposable child process and temporary local SQLite database.
It does not simulate a physical power cut, authenticate users or call a connector.
"""
import copy
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from authorization_guard_v02 import ContractError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import (
    APPROVAL_KEY, IDENTITY_KEY, NOW, fixture,
)

# A child uses the actual v1.1 boundary. The connection subclass kills the
# child immediately before/after sqlite3.Connection.commit(), not the parent.
CHILD = r"""
import os
import sqlite3
import sys
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture

db_path, crash_point, operation = sys.argv[1:]
class CrashConnection(sqlite3.Connection):
    def commit(self):
        if crash_point == 'before':
            os._exit(71)
        super().commit()
        if crash_point == 'after':
            os._exit(72)

class CrashStore(FictionalRevocableStore):
    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=15.0, isolation_level=None,
                               factory=CrashConnection)
        return conn

scenario = fixture()
issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
identity = issuer.issue_identity('fictional-user',
    '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
approval = issuer.issue_approval(scenario)
boundary = FictionalRevocableBoundary(CrashStore(db_path), IDENTITY_KEY, APPROVAL_KEY)
if operation == 'execute':
    boundary.execute(scenario, scenario['authorization']['scope'],
        identity_token=identity, approval_token=approval, now=NOW)
elif operation == 'revoke':
    boundary.revoke(approval, now=NOW, reason='fictional test withdrawal')
else:
    raise ValueError('unsupported test operation')
os._exit(99)  # A successful return means the expected crash hook was NOT hit.
"""


class FictionalProcessKillTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / 'fictional-crash.sqlite3'
        self.store = FictionalRevocableStore(self.db)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.scenario = fixture()
        self.scope = copy.deepcopy(self.scenario['authorization']['scope'])
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.identity = issuer.issue_identity('fictional-user',
            '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        self.approval = issuer.issue_approval(self.scenario)

    def kill_child(self, operation, crash_point):
        proc = subprocess.run(
            [sys.executable, '-B', '-c', CHILD, str(self.db), crash_point, operation],
            cwd=str(Path(__file__).resolve().parent),
            capture_output=True, text=True, timeout=15,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
            check=False,
        )
        self.assertEqual(proc.returncode, 71 if crash_point == 'before' else 72,
            'child did not reach intended commit hook; stderr=' + proc.stderr[-1000:])

    def execute_after_restart(self):
        reopened = FictionalRevocableBoundary(
            FictionalRevocableStore(self.db), IDENTITY_KEY, APPROVAL_KEY)
        return reopened.execute(self.scenario, self.scope,
            identity_token=self.identity, approval_token=self.approval, now=NOW)

    def test_execute_kill_before_commit_rolls_back(self):
        self.kill_child('execute', 'before')
        self.assertEqual(self.store.receipt_count(), 0)
        retry = self.execute_after_restart()
        self.assertFalse(retry['idempotent_replay'])
        self.assertEqual(retry['external_actions'], 0)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_execute_kill_after_commit_recovers_idempotently(self):
        self.kill_child('execute', 'after')
        self.assertEqual(self.store.receipt_count(), 1)
        retry = self.execute_after_restart()
        self.assertTrue(retry['idempotent_replay'])
        self.assertEqual(retry['external_actions'], 0)
        self.assertEqual(self.store.receipt_count(), 1)

    def test_revoke_kill_before_commit_rolls_back(self):
        self.kill_child('revoke', 'before')
        self.assertEqual(self.store.revocation_count(), 0)
        result = self.execute_after_restart()
        self.assertFalse(result['idempotent_replay'])
        self.assertEqual(result['external_actions'], 0)

    def test_revoke_kill_after_commit_persists_and_denies(self):
        self.kill_child('revoke', 'after')
        self.assertEqual(self.store.revocation_count(), 1)
        with self.assertRaisesRegex(ContractError, 'revoked'):
            self.execute_after_restart()
        self.assertEqual(self.store.receipt_count(), 0)


if __name__ == '__main__':
    unittest.main()
