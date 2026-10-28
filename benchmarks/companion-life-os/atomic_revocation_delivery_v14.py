"""v1.4 fictional SINGLE-SQLite-transaction revocation/dispatch experiment.

Only disposable fixtures; NO external connector, authenticated identity, trusted
clock, physical power-loss guarantee, or production authorization. The legacy
v0.7 outbox remains a separate bypass and MUST NOT be used for real effects.
"""
import hashlib
import json
from contextlib import closing


def _json(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _digest(obj):
    return hashlib.sha256(_json(obj).encode('utf-8')).hexdigest()


class FictionalDeliveryError(ValueError):
    pass


class AtomicFictionalDelivery:
    """A fake sink and outbox in ONE SQLite transaction with revocation check."""

    def __init__(self, boundary):
        from revocable_signed_boundary_v11 import FictionalRevocableBoundary
        if not isinstance(boundary, FictionalRevocableBoundary):
            raise TypeError('fictional signed/revocable boundary required')
        self.boundary = boundary
        self.store = boundary.store
        with closing(self.store._connect()) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS fictional_atomic_outbox_v14 (
                nonce TEXT PRIMARY KEY, approval_digest TEXT NOT NULL,
                payload_json TEXT NOT NULL, binding_digest TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending','cancelled','acked')),
                ack_json TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS fictional_atomic_sink_v14 (
                nonce TEXT PRIMARY KEY, payload_digest TEXT NOT NULL,
                ack_json TEXT NOT NULL)""")

    @staticmethod
    def _payload(nonce, receipt_json):
        from fictional_outbox_v07 import _payload
        return _payload(nonce, receipt_json)

    def stage(self, scenario, requested_scope, *, identity_token, approval_token, now):
        from revocable_signed_boundary_v11 import _token_digest
        # Existing fictional signed boundary checks token/scope/time. Recheck
        # revocation inside the insertion transaction to close the race.
        receipt = self.boundary.execute(scenario, requested_scope,
                                        identity_token=identity_token,
                                        approval_token=approval_token, now=now)
        nonce = receipt['nonce']
        approval_digest = _token_digest(approval_token)
        with closing(self.store._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                if db.execute('SELECT 1 FROM fictional_revocations WHERE token_sha256=?',
                              (approval_digest,)).fetchone():
                    raise FictionalDeliveryError('fictional approval revoked before staging')
                source = db.execute('SELECT receipt_json FROM receipts WHERE nonce=?',
                                    (nonce,)).fetchone()
                if source is None:
                    raise FictionalDeliveryError('source receipt missing')
                payload = self._payload(nonce, source[0])
                if payload != self._payload(nonce, _json(receipt)):
                    raise FictionalDeliveryError('receipt mismatch')
                binding = _digest({'payload': payload, 'approval_digest': approval_digest})
                old = db.execute("""SELECT approval_digest,binding_digest,status
                                    FROM fictional_atomic_outbox_v14 WHERE nonce=?""",
                                 (nonce,)).fetchone()
                if old:
                    if old[0] != approval_digest or old[1] != binding:
                        raise FictionalDeliveryError('nonce rebound to different approval')
                    if old[2] == 'cancelled':
                        raise FictionalDeliveryError('cancelled work cannot be restaged')
                else:
                    db.execute('INSERT INTO fictional_atomic_outbox_v14 VALUES(?,?,?,?,?,?)',
                               (nonce, approval_digest, _json(payload), binding, 'pending', None))
                db.commit()
                return {'nonce': nonce, 'synthetic': True, 'external_actions': 0,
                        'stage_replay': bool(old)}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def dispatch(self, nonce, *, failure_point=None):
        if failure_point not in (None, 'before_commit', 'after_commit'):
            raise ValueError('unsupported fictional failure injection')
        with closing(self.store._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute("""SELECT approval_digest,payload_json,binding_digest,
                                          status,ack_json
                                   FROM fictional_atomic_outbox_v14 WHERE nonce=?""",
                                 (nonce,)).fetchone()
                if row is None:
                    raise FictionalDeliveryError('work not staged')
                approval_digest, payload_json, binding, status, ack_json = row
                from fictional_outbox_v07 import _decode
                payload = _decode(payload_json)
                if _digest({'payload': payload, 'approval_digest': approval_digest}) != binding:
                    raise FictionalDeliveryError('outbox binding changed')
                source = db.execute('SELECT receipt_json FROM receipts WHERE nonce=?',
                                    (nonce,)).fetchone()
                if source is None or self._payload(nonce, source[0]) != payload:
                    raise FictionalDeliveryError('source receipt changed')
                existing_sink = db.execute("""SELECT payload_digest,ack_json
                                              FROM fictional_atomic_sink_v14 WHERE nonce=?""",
                                           (nonce,)).fetchone()
                if status == 'acked':
                    if existing_sink is None or existing_sink[0] != _digest(payload) or (
                        existing_sink[1] != ack_json
                    ):
                        raise FictionalDeliveryError('acknowledgment/sink mismatch')
                    ack = _decode(ack_json)
                    if ack != {'nonce': nonce, 'synthetic': True,
                               'simulated_actions': 1, 'external_actions': 0,
                               'payload_digest': _digest(payload)}:
                        raise FictionalDeliveryError('stored acknowledgment invalid')
                    db.commit()
                    return {**ack, 'outbox_replay': True}
                if status == 'cancelled':
                    raise FictionalDeliveryError('fictional pending work cancelled')
                if existing_sink is not None:
                    raise FictionalDeliveryError('unexpected preexisting sink row')
                if db.execute('SELECT 1 FROM fictional_revocations WHERE token_sha256=?',
                              (approval_digest,)).fetchone():
                    db.execute("""UPDATE fictional_atomic_outbox_v14
                                  SET status='cancelled' WHERE nonce=?""", (nonce,))
                    db.commit()
                    raise FictionalDeliveryError('fictional approval revoked; pending work cancelled')
                ack = {'nonce': nonce, 'synthetic': True, 'simulated_actions': 1,
                       'external_actions': 0, 'payload_digest': _digest(payload)}
                db.execute('INSERT INTO fictional_atomic_sink_v14 VALUES(?,?,?)',
                           (nonce, _digest(payload), _json(ack)))
                db.execute("""UPDATE fictional_atomic_outbox_v14
                              SET status='acked',ack_json=? WHERE nonce=?""",
                           (_json(ack), nonce))
                if failure_point == 'before_commit':
                    raise RuntimeError('fictional injected crash before commit')
                db.commit()
                if failure_point == 'after_commit':
                    raise RuntimeError('fictional injected crash after commit')
                return {**ack, 'outbox_replay': False}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def counts(self, nonce):
        with closing(self.store._connect()) as db:
            status = db.execute('SELECT status FROM fictional_atomic_outbox_v14 WHERE nonce=?',
                                (nonce,)).fetchone()
            count = db.execute('SELECT COUNT(*) FROM fictional_atomic_sink_v14').fetchone()[0]
            return {'status': status[0] if status else None,
                    'fictional_sink_rows': count, 'external_actions': 0}
