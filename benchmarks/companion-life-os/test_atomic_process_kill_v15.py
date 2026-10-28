"""Actual disposable child-process kill at v1.4 fictional sink/ack commit.

Zero external connectors or accounts. Deliberately no production security claim.
The child uses os._exit, not an exception pretending to be a crash.
"""
import copy
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture

# Only the CHILD uses CrashConnection. The parent creates/stages all test
# records before starting it; initialization is not part of the injected window.
CHILD = r"""
import os
import sqlite3
import sys
from atomic_revocation_delivery_v14 import AtomicFictionalDelivery
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY

path, nonce, point = sys.argv[1:]
class CrashConnection(sqlite3.Connection):
    def commit(self):
        if point == 'before':
            os._exit(71)
        super().commit()
        if point == 'after':
            os._exit(72)

class CrashStore(FictionalRevocableStore):
    def _connect(self):
        return sqlite3.connect(self.path, timeout=15.0, isolation_level=None,
                               factory=CrashConnection)

boundary = FictionalRevocableBoundary(CrashStore(path), IDENTITY_KEY, APPROVAL_KEY)
AtomicFictionalDelivery(boundary).dispatch(nonce)
os._exit(99)  # Unexpected: no commit hook reached.
"""


class AtomicProcessKillTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.db = Path(temporary.name) / 'atomic-kill-v15.sqlite3'
        self.store = FictionalRevocableStore(self.db)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.adapter = AtomicFictionalDelivery(self.boundary)
        scenario = fixture()
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        identity = issuer.issue_identity('fictional-user', '2026-10-01T09:00:00Z',
                                         '2026-10-01T12:00:00Z')
        self.approval = issuer.issue_approval(scenario)
        self.nonce = self.adapter.stage(
            scenario, copy.deepcopy(scenario['authorization']['scope']),
            identity_token=identity, approval_token=self.approval, now=NOW)['nonce']

    def kill_child(self, point):
        result = subprocess.run(
            [sys.executable, '-B', '-c', CHILD, str(self.db), self.nonce, point],
            cwd=str(Path(__file__).resolve().parent), capture_output=True, text=True,
            timeout=20, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
            check=False,
        )
        self.assertEqual(result.returncode, 71 if point == 'before' else 72,
                         'child did not reach commit hook; stderr=' + result.stderr[-1200:])
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_kill_before_sink_ack_commit_rolls_back_both(self):
        self.kill_child('before')
        self.assertEqual(self.adapter.counts(self.nonce),
                         {'status': 'pending', 'fictional_sink_rows': 0, 'external_actions': 0})
        recovered = AtomicFictionalDelivery(
            FictionalRevocableBoundary(FictionalRevocableStore(self.db),
                                       IDENTITY_KEY, APPROVAL_KEY))
        outcome = recovered.dispatch(self.nonce)
        self.assertFalse(outcome['outbox_replay'])
        self.assertEqual(outcome['external_actions'], 0)
        self.assertEqual(recovered.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_kill_after_sink_ack_commit_replays_without_duplicate(self):
        self.kill_child('after')
        self.assertEqual(self.adapter.counts(self.nonce),
                         {'status': 'acked', 'fictional_sink_rows': 1, 'external_actions': 0})
        recovered = AtomicFictionalDelivery(
            FictionalRevocableBoundary(FictionalRevocableStore(self.db),
                                       IDENTITY_KEY, APPROVAL_KEY))
        replay = recovered.dispatch(self.nonce)
        self.assertTrue(replay['outbox_replay'])
        self.assertEqual(replay['external_actions'], 0)
        self.assertEqual(recovered.counts(self.nonce)['fictional_sink_rows'], 1)

    def test_kill_before_cancel_commit_leaves_pending_but_revoked(self):
        self.boundary.revoke(self.approval, now=NOW, reason='fictional withdrawal')
        self.kill_child('before')
        self.assertEqual(self.adapter.counts(self.nonce)['status'], 'pending')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)
        with self.assertRaisesRegex(FictionalDeliveryError, 'revoked'):
            self.adapter.dispatch(self.nonce)
        self.assertEqual(self.adapter.counts(self.nonce)['status'], 'cancelled')
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)

    def test_kill_after_cancel_commit_persists_cancelled(self):
        self.boundary.revoke(self.approval, now=NOW, reason='fictional withdrawal')
        self.kill_child('after')
        self.assertEqual(self.adapter.counts(self.nonce),
                         {'status': 'cancelled', 'fictional_sink_rows': 0, 'external_actions': 0})
        with self.assertRaisesRegex(FictionalDeliveryError, 'cancelled'):
            self.adapter.dispatch(self.nonce)
        self.assertEqual(self.adapter.counts(self.nonce)['fictional_sink_rows'], 0)


if __name__ == '__main__':
    unittest.main()
