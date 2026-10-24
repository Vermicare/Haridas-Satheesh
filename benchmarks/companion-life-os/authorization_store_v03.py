"""Fictional SQLite-backed idempotency experiment. No real connector or identity proof.

Not an authentication or distributed exactly-once system. Uses the v0.2 guard for
fictional contract validation; SQLite serializes competing local writers.
"""
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from authorization_guard_v02 import ContractError, simulate_once


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def _fingerprint(scenario, requested_scope, principal):
    return hashlib.sha256(_canonical({
        'scenario': scenario, 'scope': requested_scope, 'principal': principal,
    }).encode('utf-8')).hexdigest()


class FictionalDurableStore:
    """Single-host local SQLite sandbox. Callers supply a fictional principal/clock."""

    def __init__(self, database_path):
        self.path = str(Path(database_path))
        if self.path == ':memory:':
            raise ValueError('durability requires a filesystem path')
        with closing(self._connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS receipts (
                nonce TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
                receipt_json TEXT NOT NULL)''')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15.0, isolation_level=None)

    def execute(self, scenario, requested_scope, *, principal, now, trusted_principals,
                failure_point=None):
        """Return first receipt or an idempotent copy; never perform external actions.

        failure_point is a test-only crash injector: 'before_commit'/'after_commit'.
        A real connector requires an outbox/ack protocol, not this local simulation.
        """
        if failure_point not in (None, 'before_commit', 'after_commit'):
            raise ValueError('unsupported failure injection')
        # Validate the entire fictional contract *before* revealing a prior receipt.
        receipt = simulate_once(scenario, requested_scope, principal=principal,
                                now=now, consumed=set(),
                                trusted_principals=trusted_principals)
        nonce = receipt['nonce']
        fingerprint = _fingerprint(scenario, requested_scope, principal)
        db = self._connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT fingerprint, receipt_json FROM receipts WHERE nonce=?',
                             (nonce,)).fetchone()
            if row is not None:
                if row[0] != fingerprint:
                    raise ContractError('nonce already bound to different request')
                db.commit()
                return {**json.loads(row[1]), 'idempotent_replay': True}
            db.execute('INSERT INTO receipts(nonce,fingerprint,receipt_json) VALUES(?,?,?)',
                       (nonce, fingerprint, _canonical(receipt)))
            if failure_point == 'before_commit':
                raise RuntimeError('injected failure before commit')
            db.commit()
            if failure_point == 'after_commit':
                raise RuntimeError('injected failure after commit')
            return {**receipt, 'idempotent_replay': False}
        except BaseException:
            if db.in_transaction:
                db.rollback()
            raise
        finally:
            db.close()

    def receipt_count(self):
        with closing(self._connect()) as db:
            return db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]
