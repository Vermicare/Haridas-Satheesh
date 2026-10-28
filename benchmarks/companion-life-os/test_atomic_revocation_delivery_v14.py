"""Fictional v1.4 integration and negative controls; zero external actions."""
import copy
import sqlite3
from contextlib import closing
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from authorization_guard_v02 import ContractError
from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from fictional_outbox_v07 import FictionalIdempotentSink, FictionalOutbox
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture


class AtomicDeliveryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / 'receipts.sqlite3'
        self.store = FictionalRevocableStore(self.db)
        self.boundary = FictionalRevocableBoundary(self.store, IDENTITY_KEY, APPROVAL_KEY)
        self.adapter = AtomicFictionalDelivery(self.boundary)
        self.scenario = fixture()
        self.scope = copy.deepcopy(self.scenario['authorization']['scope'])
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        self.identity = issuer.issue_identity('fictional-user', '2026-10-01T09:00:00Z',
                                              '2026-10-01T12:00:00Z')
        self.approval = issuer.issue_approval(self.scenario)
        self.args = {'identity_token': self.identity, 'approval_token': self.approval, 'now': NOW}

    def stage(self):
        return self.adapter.stage(self.scenario, self.scope, **self.args)['nonce']

    def revoke(self):
        self.boundary.revoke(self.approval, now=NOW, reason='fictional stop')

    def test_revocation_before_dispatch_cancels_without_sink(self):
        nonce = self.stage()
        self.revoke()
        with self.assertRaisesRegex(FictionalDeliveryError, 'revoked'):
            self.adapter.dispatch(nonce)
        self.assertEqual(self.adapter.counts(nonce)['status'], 'cancelled')
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 0)

    def test_revocation_before_stage_denies(self):
        self.boundary.execute(self.scenario, self.scope, **self.args)
        self.revoke()
        with self.assertRaisesRegex(ContractError, 'revoked'):
            self.stage()
        self.assertEqual(self.adapter.counts('missing')['fictional_sink_rows'], 0)

    def test_dispatch_before_revocation_is_not_undone(self):
        nonce = self.stage()
        first = self.adapter.dispatch(nonce)
        self.revoke()
        replay = self.adapter.dispatch(nonce)
        self.assertFalse(first['outbox_replay'])
        self.assertTrue(replay['outbox_replay'])
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 1)

    def test_before_commit_failure_rolls_back_sink_and_ack(self):
        nonce = self.stage()
        with self.assertRaisesRegex(RuntimeError, 'before commit'):
            self.adapter.dispatch(nonce, failure_point='before_commit')
        self.assertEqual(self.adapter.counts(nonce),
                         {'status': 'pending', 'fictional_sink_rows': 0, 'external_actions': 0})
        self.revoke()
        with self.assertRaises(FictionalDeliveryError):
            self.adapter.dispatch(nonce)
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 0)

    def test_after_commit_failure_is_idempotent(self):
        nonce = self.stage()
        with self.assertRaisesRegex(RuntimeError, 'after commit'):
            self.adapter.dispatch(nonce, failure_point='after_commit')
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 1)
        self.assertTrue(self.adapter.dispatch(nonce)['outbox_replay'])

    def test_concurrent_dispatches_create_one_fake_row(self):
        nonce = self.stage()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.adapter.dispatch(nonce), range(12)))
        self.assertEqual(sum(not r['outbox_replay'] for r in results), 1)
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 1)

    def test_tampered_approval_binding_rejected(self):
        nonce = self.stage()
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("""UPDATE fictional_atomic_outbox_v14
                          SET approval_digest=? WHERE nonce=?""", ('0'*64, nonce))
            db.commit()
        with self.assertRaisesRegex(FictionalDeliveryError, 'binding changed'):
            self.adapter.dispatch(nonce)
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 0)

    def test_legacy_bypass_remains_and_is_explicitly_not_fixed(self):
        nonce = self.stage()
        FictionalOutbox(self.db).stage(nonce)
        self.revoke()
        with self.assertRaises(FictionalDeliveryError):
            self.adapter.dispatch(nonce)
        sink = FictionalIdempotentSink(self.db.with_name('legacy-sink.sqlite3'))
        legacy = FictionalOutbox(self.db).dispatch(nonce, sink)
        self.assertEqual(legacy['simulated_actions'], 1)
        self.assertEqual(sink.count(), 1)
        self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 0)

    def test_revocation_and_dispatch_race_has_one_serialized_outcome(self):
        nonce = self.stage()
        with ThreadPoolExecutor(max_workers=2) as pool:
            rev = pool.submit(self.revoke)
            disp = pool.submit(self.adapter.dispatch, nonce)
            rev.result()
            try:
                result = disp.result()
                self.assertEqual(result['external_actions'], 0)
                self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 1)
            except FictionalDeliveryError:
                self.assertEqual(self.adapter.counts(nonce)['fictional_sink_rows'], 0)
                self.assertEqual(self.adapter.counts(nonce)['status'], 'cancelled')


if __name__ == '__main__':
    unittest.main()
