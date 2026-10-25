"""Synthetic-only crash-window and idempotency tests; no external action."""
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fictional_outbox_v07 import FictionalIdempotentSink, FictionalOutbox, OutboxContractError


class OutboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'receipt.sqlite3'
        self.sinkdb = Path(self.tmp.name) / 'sink.sqlite3'
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE receipts (nonce TEXT PRIMARY KEY, fingerprint TEXT, receipt_json TEXT)')
            db.execute('INSERT INTO receipts VALUES(?,?,?)', ('n1', 'test-only', json.dumps({
                'nonce': 'n1', 'decision': 'D1', 'action': 'A1',
                'synthetic': True, 'external_actions': 0})))
        self.outbox = FictionalOutbox(self.db)
        self.sink = FictionalIdempotentSink(self.sinkdb)

    def test_stage_and_deliver(self):
        self.assertFalse(self.outbox.stage('n1')['stage_replay'])
        self.assertEqual(self.outbox.status('n1'), 'pending')
        result = self.outbox.dispatch('n1', self.sink)
        self.assertEqual((result['external_actions'], result['simulated_actions']), (0, 1))
        self.assertEqual((self.sink.count(), self.outbox.status('n1')), (1, 'acked'))

    def test_stage_idempotency_and_restart(self):
        self.outbox.stage('n1')
        self.assertTrue(FictionalOutbox(self.db).stage('n1')['stage_replay'])
        self.assertFalse(FictionalOutbox(self.db).dispatch('n1', FictionalIdempotentSink(self.sinkdb))['outbox_replay'])
        self.assertTrue(FictionalOutbox(self.db).dispatch('n1', FictionalIdempotentSink(self.sinkdb))['outbox_replay'])
        self.assertEqual(self.sink.count(), 1)

    def test_crash_after_sink_before_ack_recovers(self):
        self.outbox.stage('n1')
        with self.assertRaisesRegex(RuntimeError, 'after sink'):
            self.outbox.dispatch('n1', self.sink, failure_point='after_sink_before_ack')
        self.assertEqual(self.outbox.status('n1'), 'pending')
        self.assertEqual(self.sink.count(), 1)
        result = FictionalOutbox(self.db).dispatch('n1', FictionalIdempotentSink(self.sinkdb))
        self.assertTrue(result['sink_replay'])
        self.assertEqual(self.outbox.status('n1'), 'acked')
        self.assertEqual(self.sink.count(), 1)

    def test_concurrent_delivery_one_fake_sink_effect(self):
        self.outbox.stage('n1')
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: FictionalOutbox(self.db).dispatch('n1', FictionalIdempotentSink(self.sinkdb)), range(16)))
        self.assertEqual(len(results), 16)
        self.assertEqual(self.sink.count(), 1)
        self.assertEqual(self.outbox.status('n1'), 'acked')

    def test_missing_original_fails_closed(self):
        with self.assertRaisesRegex(OutboxContractError, 'original receipt missing'):
            self.outbox.stage('absent')
        self.assertIsNone(self.outbox.status('absent'))

    def test_dispatch_before_stage_fails(self):
        with self.assertRaisesRegex(OutboxContractError, 'not staged'):
            self.outbox.dispatch('n1', self.sink)
        self.assertEqual(self.sink.count(), 0)

    def test_original_changed_after_stage_rejected(self):
        self.outbox.stage('n1')
        with sqlite3.connect(self.db) as db:
            db.execute('UPDATE receipts SET receipt_json=? WHERE nonce=?', (json.dumps({
                'nonce': 'n1', 'decision': 'D1', 'action': 'A2',
                'synthetic': True, 'external_actions': 0}), 'n1'))
        with self.assertRaisesRegex(OutboxContractError, 'source receipt changed'):
            self.outbox.dispatch('n1', self.sink)
        self.assertEqual(self.sink.count(), 0)

    def test_nonfinite_original_rejected(self):
        with sqlite3.connect(self.db) as db:
            db.execute('UPDATE receipts SET receipt_json=? WHERE nonce=?',
                       ('{"nonce":"n1","decision":"D1","action":"A1","synthetic":true,"external_actions":NaN}', 'n1'))
        with self.assertRaises(OutboxContractError):
            self.outbox.stage('n1')

    def test_overflowed_numeric_json_rejected(self):
        with sqlite3.connect(self.db) as db:
            db.execute('UPDATE receipts SET receipt_json=? WHERE nonce=?',
                       ('{"nonce":"n1","decision":"D1","action":"A1","synthetic":true,"external_actions":0,"extra":1e400}', 'n1'))
        with self.assertRaisesRegex(OutboxContractError, 'non-finite'):
            self.outbox.stage('n1')
        self.assertIsNone(self.outbox.status('n1'))

    def test_invalid_source_is_not_staged(self):
        with sqlite3.connect(self.db) as db:
            db.execute('UPDATE receipts SET receipt_json=? WHERE nonce=?', (json.dumps({
                'nonce': 'n1', 'decision': 'D1', 'action': 'A1',
                'synthetic': True, 'external_actions': True}), 'n1'))
        with self.assertRaisesRegex(OutboxContractError, 'binding mismatch'):
            self.outbox.stage('n1')
        self.assertIsNone(self.outbox.status('n1'))

    def test_sink_rejects_nonce_payload_collision(self):
        self.outbox.stage('n1')
        self.outbox.dispatch('n1', self.sink)
        with self.assertRaisesRegex(OutboxContractError, 'different payload'):
            self.sink.apply({'nonce': 'n1', 'decision': 'D2', 'action': 'A1', 'synthetic': True})
        self.assertEqual(self.sink.count(), 1)

    def test_bad_ack_rejected_no_ack_state(self):
        self.outbox.stage('n1')
        class BadSink:
            def apply(self, payload):
                return {'nonce': payload['nonce'], 'digest': 'wrong', 'synthetic': True,
                        'external_actions': 0}
        with self.assertRaisesRegex(OutboxContractError, 'acknowledgment'):
            self.outbox.dispatch('n1', BadSink())
        self.assertEqual(self.outbox.status('n1'), 'pending')

    def test_nonidempotent_adapter_replay_hazard(self):
        self.outbox.stage('n1')
        class UnsafeSink:
            count = 0
            def apply(self, payload):
                from fictional_outbox_v07 import _digest
                self.count += 1
                return {'nonce': payload['nonce'], 'digest': _digest(payload),
                        'synthetic': True, 'simulated_actions': 1, 'external_actions': 0}
        unsafe = UnsafeSink()
        with self.assertRaises(RuntimeError):
            self.outbox.dispatch('n1', unsafe, failure_point='after_sink_before_ack')
        self.outbox.dispatch('n1', unsafe)
        self.assertEqual(unsafe.count, 2)  # negative control: no general exactly-once guarantee

    def test_real_v03_generated_receipt_integration(self):
        from authorization_store_v03 import FictionalDurableStore
        from test_actual_receipt_integration_v06 import fictional_scenario
        scenario = fictional_scenario()
        actual = FictionalDurableStore(self.db).execute(
            scenario, scenario['authorization']['scope'],
            principal='fictional-user', now='2026-10-01T10:30:00Z',
            trusted_principals={'fictional-user'})
        self.assertEqual(actual['external_actions'], 0)
        nonce = actual['nonce']
        self.outbox.stage(nonce)
        self.outbox.dispatch(nonce, self.sink)
        self.assertEqual(self.outbox.status(nonce), 'acked')
        self.assertEqual(self.sink.count(), 1)


if __name__ == '__main__':
    unittest.main()
