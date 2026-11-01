"""Fictional expiry-aware single-SQLite dispatch candidate, not production auth.

Adds test-harness time/identity/approval verification at dispatch to the v1.4
local atomic outbox. Public test HMAC keys and caller-supplied time are NOT
real identity or trusted time. Legacy v0.3/v0.7 paths remain bypasses; no
external connector is used. Never deploy as a security boundary.
"""
from contextlib import closing

from atomic_revocation_delivery_v14 import (
    AtomicFictionalDelivery, FictionalDeliveryError, _digest, _json,
)
from fictional_outbox_v07 import _decode
from revocable_signed_boundary_v11 import _token_digest
from sandbox_issuer_v10 import (
    _verify, _time_gate, IDENTITY_KEYS, APPROVAL_KEYS,
)


class ExpiryCheckedFictionalDelivery(AtomicFictionalDelivery):
    """One fake SQLite effect boundary with explicit dispatch-time checks."""

    def dispatch(self, nonce, *, identity_token, approval_token, now,
                 failure_point=None):
        if failure_point not in (None, 'before_commit', 'after_commit'):
            raise ValueError('unsupported fictional failure injection')
        # Verify BOTH signed fictional tokens and their windows on EVERY call,
        # including replay. No untrusted caller can skip the time parameter.
        identity = _verify(identity_token, self.boundary.signed.identity_key,
                           'identity', IDENTITY_KEYS)
        approval = _verify(approval_token, self.boundary.approval_key,
                           'approval', APPROVAL_KEYS)
        _time_gate(identity, now)
        _time_gate(approval, now)
        if (identity['subject'] != approval['principal'] or
                approval['nonce'] != nonce):
            raise FictionalDeliveryError('signed fictional dispatch identity/nonce mismatch')
        digest = _token_digest(approval_token)
        with closing(self.store._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute('''SELECT approval_digest,payload_json,binding_digest,
                                   status,ack_json FROM fictional_atomic_outbox_v14
                                   WHERE nonce=?''', (nonce,)).fetchone()
                if row is None:
                    raise FictionalDeliveryError('fictional work not staged')
                stored_digest, payload_json, binding, status, ack_json = row
                if stored_digest != digest:
                    raise FictionalDeliveryError('approval token differs from staged grant')
                payload = _decode(payload_json)
                if (not isinstance(payload, dict) or
                        set(payload) != {'nonce', 'decision', 'action', 'synthetic'} or
                        payload['synthetic'] is not True or
                        payload['nonce'] != nonce or
                        payload['decision'] != approval['decision_id']):
                    raise FictionalDeliveryError('fictional staged payload malformed')
                if _digest({'payload': payload, 'approval_digest': digest}) != binding:
                    raise FictionalDeliveryError('fictional outbox binding changed')
                source = db.execute('SELECT receipt_json FROM receipts WHERE nonce=?',
                                    (nonce,)).fetchone()
                if source is None or self._payload(nonce, source[0]) != payload:
                    raise FictionalDeliveryError('fictional source receipt changed')
                revoked = db.execute('''SELECT 1 FROM fictional_revocations
                                        WHERE token_sha256=?''', (digest,)).fetchone()
                if revoked:
                    if status == 'pending':
                        db.execute('''UPDATE fictional_atomic_outbox_v14
                                      SET status='cancelled' WHERE nonce=?''', (nonce,))
                        db.commit()
                    raise FictionalDeliveryError('fictional approval revoked at dispatch')
                if status == 'cancelled':
                    raise FictionalDeliveryError('fictional pending work cancelled')
                existing = db.execute('''SELECT payload_digest,ack_json
                                         FROM fictional_atomic_sink_v14
                                         WHERE nonce=?''', (nonce,)).fetchone()
                expected_ack = {'nonce': nonce, 'synthetic': True,
                                'simulated_actions': 1, 'external_actions': 0,
                                'payload_digest': _digest(payload)}
                if status == 'acked':
                    if (existing is None or existing[0] != _digest(payload) or
                            existing[1] != ack_json or _decode(ack_json) != expected_ack):
                        raise FictionalDeliveryError('fictional stored acknowledgment invalid')
                    db.commit()
                    return {**expected_ack, 'outbox_replay': True}
                if existing is not None:
                    raise FictionalDeliveryError('unexpected fictional preexisting sink row')
                db.execute('INSERT INTO fictional_atomic_sink_v14 VALUES(?,?,?)',
                           (nonce, _digest(payload), _json(expected_ack)))
                db.execute('''UPDATE fictional_atomic_outbox_v14
                              SET status='acked',ack_json=? WHERE nonce=?''',
                           (_json(expected_ack), nonce))
                if failure_point == 'before_commit':
                    raise RuntimeError('fictional injected crash before commit')
                db.commit()
                if failure_point == 'after_commit':
                    raise RuntimeError('fictional injected crash after commit')
                return {**expected_ack, 'outbox_replay': False}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise
