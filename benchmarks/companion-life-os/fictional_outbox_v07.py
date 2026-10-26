"""Fictional durable outbox + idempotent SQLite sink. NO external connector.

The sink is a *different* SQLite database to expose the crash window between
simulated delivery and local acknowledgment. Idempotency is an adapter contract,
not a claim of exactly-once execution for arbitrary external services.
"""
import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path


class OutboxContractError(ValueError):
    pass


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _decode(value):
    def reject(token):
        raise OutboxContractError('non-finite JSON: ' + token)
    def unique_object(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise OutboxContractError('duplicate JSON key: ' + key)
            result[key] = item
        return result
    try:
        parsed = json.loads(value, parse_constant=reject, object_pairs_hook=unique_object)
        def check_finite(item):
            if isinstance(item, float) and not math.isfinite(item):
                raise OutboxContractError('non-finite numeric JSON value')
            if isinstance(item, dict):
                for nested in item.values():
                    check_finite(nested)
            elif isinstance(item, list):
                for nested in item:
                    check_finite(nested)
        check_finite(parsed)
        return parsed
    except OutboxContractError:
        raise
    except (TypeError, ValueError) as exc:
        raise OutboxContractError('invalid stored JSON') from exc


def _payload(nonce, receipt_json):
    receipt = _decode(receipt_json)
    if not isinstance(receipt, dict) or receipt.get('synthetic') is not True or (
        type(receipt.get('external_actions')) is not int or receipt['external_actions'] != 0
    ) or receipt.get('nonce') != nonce:
        raise OutboxContractError('original fictional receipt binding mismatch')
    for key in ('decision', 'action'):
        if not isinstance(receipt.get(key), str) or not receipt[key].strip():
            raise OutboxContractError('original receipt missing ' + key)
    return {'nonce': nonce, 'decision': receipt['decision'], 'action': receipt['action'],
            'synthetic': True}


def _digest(payload):
    return hashlib.sha256(_canonical(payload).encode('utf-8')).hexdigest()


def _validated_ack(ack, nonce, digest, *, stored=False):
    """Validate both new and persisted fictional adapter acknowledgments."""
    if not isinstance(ack, dict) or ack.get('nonce') != nonce or (
        ack.get('digest') != digest or ack.get('synthetic') is not True or
        type(ack.get('external_actions')) is not int or ack['external_actions'] != 0 or
        type(ack.get('simulated_actions')) is not int or ack['simulated_actions'] != 1
    ):
        raise OutboxContractError('stored acknowledgment mismatch' if stored else
                                  'untrusted fictional adapter acknowledgment')
    return ack


class FictionalIdempotentSink:
    """Fake local adapter with a UNIQUE nonce; no actual task changes."""

    def __init__(self, path):
        self.path = str(Path(path))
        if self.path == ':memory:':
            raise ValueError('sink must be on disk')
        with closing(self._connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS simulated_deliveries
                (nonce TEXT PRIMARY KEY, digest TEXT NOT NULL, ack_json TEXT NOT NULL)''')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15.0, isolation_level=None)

    def apply(self, payload):
        # The fake sink is a separate trust boundary: validate its own input
        # even when the caller is not FictionalOutbox.dispatch.
        if not isinstance(payload, dict) or set(payload) != {
            'nonce', 'decision', 'action', 'synthetic'
        } or payload.get('synthetic') is not True:
            raise OutboxContractError('invalid fictional sink payload')
        nonce = payload['nonce']
        if any(not isinstance(payload[key], str) or not payload[key].strip()
               for key in ('nonce', 'decision', 'action')):
            raise OutboxContractError('invalid fictional sink payload')
        digest = _digest(payload)
        with closing(self._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                existing = db.execute('SELECT digest,ack_json FROM simulated_deliveries WHERE nonce=?',
                                      (nonce,)).fetchone()
                if existing:
                    if existing[0] != digest:
                        raise OutboxContractError('sink nonce bound to different payload')
                    # A persisted acknowledgment is not trustworthy merely
                    # because the payload digest column still matches.
                    ack = _validated_ack(_decode(existing[1]), nonce, digest, stored=True)
                    db.commit()
                    return {**ack, 'sink_replay': True}
                ack = {'nonce': nonce, 'digest': digest, 'synthetic': True,
                       'simulated_actions': 1, 'external_actions': 0}
                db.execute('INSERT INTO simulated_deliveries VALUES(?,?,?)',
                           (nonce, digest, _canonical(ack)))
                db.commit()
                return {**ack, 'sink_replay': False}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def count(self):
        with closing(self._connect()) as db:
            return db.execute('SELECT COUNT(*) FROM simulated_deliveries').fetchone()[0]


class FictionalOutbox:
    """Local staging and acknowledgment. No real identity, clocks, or external effects."""

    def __init__(self, path):
        self.path = str(Path(path))
        if self.path == ':memory:':
            raise ValueError('outbox must be on disk')
        with closing(self._connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS fictional_outbox (
                nonce TEXT PRIMARY KEY, payload_json TEXT NOT NULL,
                digest TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','acked')),
                ack_json TEXT)''')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15.0, isolation_level=None)

    def stage(self, nonce):
        if not isinstance(nonce, str) or not nonce.strip():
            raise OutboxContractError('nonce required')
        with closing(self._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                try:
                    row = db.execute('SELECT receipt_json FROM receipts WHERE nonce=?',
                                     (nonce,)).fetchone()
                except sqlite3.OperationalError as exc:
                    raise OutboxContractError('original receipt store missing') from exc
                if row is None:
                    raise OutboxContractError('original receipt missing')
                payload = _payload(nonce, row[0]); digest = _digest(payload)
                old = db.execute('SELECT digest FROM fictional_outbox WHERE nonce=?',
                                 (nonce,)).fetchone()
                if old and old[0] != digest:
                    raise OutboxContractError('staged nonce payload mismatch')
                if not old:
                    db.execute('INSERT INTO fictional_outbox VALUES(?,?,?,?,?)',
                               (nonce, _canonical(payload), digest, 'pending', None))
                db.commit()
                return {'nonce': nonce, 'digest': digest, 'stage_replay': bool(old)}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def dispatch(self, nonce, sink, *, failure_point=None):
        if failure_point not in (None, 'after_sink_before_ack'):
            raise ValueError('unsupported failure injection')
        with closing(self._connect()) as db:
            row = db.execute('SELECT payload_json,digest,status,ack_json FROM fictional_outbox WHERE nonce=?',
                             (nonce,)).fetchone()
            if row is None:
                raise OutboxContractError('outbox item not staged')
            payload = _decode(row[0]); digest = _digest(payload)
            if digest != row[1]:
                raise OutboxContractError('outbox payload checksum mismatch')
            receipt = db.execute('SELECT receipt_json FROM receipts WHERE nonce=?',
                                 (nonce,)).fetchone()
            if receipt is None or _payload(nonce, receipt[0]) != payload:
                raise OutboxContractError('source receipt changed or missing')
            if row[2] == 'acked':
                stored_ack = _validated_ack(_decode(row[3]), nonce, digest, stored=True)
                return {**stored_ack, 'outbox_replay': True}
        ack = sink.apply(payload)
        _validated_ack(ack, nonce, digest)
        if failure_point == 'after_sink_before_ack':
            raise RuntimeError('injected crash after sink before outbox ack')
        stored_ack = {k: v for k, v in ack.items() if k != 'sink_replay'}
        with closing(self._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                current = db.execute('SELECT digest,status,ack_json FROM fictional_outbox WHERE nonce=?',
                                     (nonce,)).fetchone()
                if current is None or current[0] != digest:
                    raise OutboxContractError('outbox changed before ack')
                if current[1] == 'acked':
                    if _decode(current[2]) != stored_ack:
                        raise OutboxContractError('conflicting adapter acknowledgment')
                else:
                    db.execute('UPDATE fictional_outbox SET status=?,ack_json=? WHERE nonce=?',
                               ('acked', _canonical(stored_ack), nonce))
                db.commit()
                return {**stored_ack, 'outbox_replay': current[1] == 'acked',
                        'sink_replay': ack.get('sink_replay', False)}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def status(self, nonce):
        with closing(self._connect()) as db:
            row = db.execute('SELECT status FROM fictional_outbox WHERE nonce=?', (nonce,)).fetchone()
            return row[0] if row else None
