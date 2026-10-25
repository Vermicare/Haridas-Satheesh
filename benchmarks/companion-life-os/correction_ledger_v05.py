"""Fictional-only SQLite correction lineage experiment.

No real identity authentication, clock attestation, external action, or tamper proof.
The receipt schema is the one created by authorization_store_v03.py.
"""
import hashlib
import json
import re
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path


class CorrectionContractError(ValueError):
    """Malformed or unauthorized *fictional* correction request."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def _utc(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        raise CorrectionContractError('canonical UTC timestamp required')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise CorrectionContractError('invalid UTC timestamp') from exc


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise CorrectionContractError('canonical YYYY-MM-DD required')
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise CorrectionContractError('invalid calendar date') from exc


def _validate(original_nonce, correction, principal, now, trusted_principals):
    if not isinstance(trusted_principals, (set, frozenset)) or not trusted_principals or any(
        not isinstance(p, str) or not p.strip() for p in trusted_principals
    ):
        raise CorrectionContractError('fictional trust set required')
    if not isinstance(principal, str) or principal not in trusted_principals:
        raise CorrectionContractError('untrusted fictional principal')
    if not isinstance(original_nonce, str) or not original_nonce:
        raise CorrectionContractError('original nonce required')
    if not isinstance(correction, dict) or set(correction) != {
        'id', 'parent_event_id', 'approved_by', 'decision', 'action', 'grant'
    }:
        raise CorrectionContractError('invalid correction schema')
    for key in ('id', 'parent_event_id', 'approved_by', 'decision', 'action'):
        if not isinstance(correction[key], str) or not correction[key].strip():
            raise CorrectionContractError('invalid correction field: ' + key)
    if correction['id'] == original_nonce or correction['parent_event_id'] == correction['id']:
        raise CorrectionContractError('invalid correction lineage self-reference')
    if correction['approved_by'] != principal:
        raise CorrectionContractError('correction principal mismatch')
    grant = correction['grant']
    if not isinstance(grant, dict) or set(grant) != {
        'id', 'nonce', 'approved_by', 'issued_at', 'expires_at', 'scope'
    }:
        raise CorrectionContractError('invalid correction grant schema')
    if any(not isinstance(grant[k], str) or not grant[k].strip() for k in (
        'id', 'nonce', 'approved_by', 'issued_at', 'expires_at'
    )):
        raise CorrectionContractError('invalid grant fields')
    if grant['approved_by'] != principal or grant['nonce'] == original_nonce:
        raise CorrectionContractError('grant principal/nonce mismatch')
    scope = grant['scope']
    if not isinstance(scope, dict) or set(scope) != {
        'operation', 'original_nonce', 'parent_event_id', 'new_due'
    }:
        raise CorrectionContractError('invalid correction scope')
    if scope['operation'] != 'restore_due_date' or scope['original_nonce'] != original_nonce or (
        scope['parent_event_id'] != correction['parent_event_id']
    ):
        raise CorrectionContractError('correction scope mismatch')
    _date(scope['new_due'])
    if not _utc(grant['issued_at']) <= _utc(now) < _utc(grant['expires_at']):
        raise CorrectionContractError('fictional correction grant not valid / expired')
    return grant


class FictionalCorrectionLedger:
    """Local SQLite logical append-only correction events; DB owner can still mutate bytes."""

    def __init__(self, database_path):
        self.path = str(Path(database_path))
        if self.path == ':memory:':
            raise ValueError('durability requires filesystem path')
        with closing(self._connect()) as db:
            # Do not create receipts: original receipt must preexist in v0.3 store.
            db.execute('''CREATE TABLE IF NOT EXISTS correction_events (
                correction_id TEXT PRIMARY KEY,
                original_nonce TEXT NOT NULL,
                parent_event_id TEXT NOT NULL UNIQUE,
                grant_nonce TEXT NOT NULL UNIQUE,
                fingerprint TEXT NOT NULL,
                event_json TEXT NOT NULL)''')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15.0, isolation_level=None)

    def record(self, original_nonce, correction, *, principal, now, trusted_principals,
               failure_point=None):
        if failure_point not in (None, 'before_commit', 'after_commit'):
            raise ValueError('invalid injected failure point')
        grant = _validate(original_nonce, correction, principal, now, trusted_principals)
        digest = hashlib.sha256(canonical({
            'original_nonce': original_nonce, 'correction': correction,
            'principal': principal
        }).encode('utf-8')).hexdigest()
        db = self._connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            try:
                original = db.execute('SELECT receipt_json FROM receipts WHERE nonce=?',
                                      (original_nonce,)).fetchone()
            except sqlite3.OperationalError as exc:
                raise CorrectionContractError('original receipt store missing') from exc
            if original is None:
                raise CorrectionContractError('original receipt not found')
            original_receipt = json.loads(original[0])
            if not isinstance(original_receipt, dict) or (
                original_receipt.get('synthetic') is not True or
                original_receipt.get('external_actions') != 0 or
                original_receipt.get('nonce') != original_nonce or
                original_receipt.get('decision') != correction['decision'] or
                original_receipt.get('action') != correction['action']
            ):
                raise CorrectionContractError('original fictional receipt binding mismatch')
            existing = db.execute('SELECT fingerprint, event_json FROM correction_events WHERE correction_id=?',
                                  (correction['id'],)).fetchone()
            if existing is not None:
                if existing[0] != digest:
                    raise CorrectionContractError('correction id already bound to different request')
                db.commit()
                return {**json.loads(existing[1]), 'idempotent_replay': True}
            parent = correction['parent_event_id']
            if parent != original_nonce:
                row = db.execute('SELECT original_nonce FROM correction_events WHERE correction_id=?',
                                 (parent,)).fetchone()
                if row is None or row[0] != original_nonce:
                    raise CorrectionContractError('unknown or cross-chain correction parent')
            if db.execute('SELECT 1 FROM correction_events WHERE parent_event_id=?', (parent,)).fetchone():
                raise CorrectionContractError('correction fork rejected')
            if db.execute('SELECT 1 FROM correction_events WHERE grant_nonce=?',
                          (grant['nonce'],)).fetchone():
                raise CorrectionContractError('correction grant nonce replay')
            event = {
                'synthetic': True, 'correction_id': correction['id'],
                'original_nonce': original_nonce, 'parent_event_id': parent,
                'decision': correction['decision'], 'action': correction['action'],
                'new_due': grant['scope']['new_due'], 'grant_id': grant['id'],
                'grant_nonce': grant['nonce'], 'external_actions': 0,
                'result': 'fictional-correction-recorded'
            }
            db.execute('''INSERT INTO correction_events
                (correction_id,original_nonce,parent_event_id,grant_nonce,fingerprint,event_json)
                VALUES(?,?,?,?,?,?)''', (
                    correction['id'], original_nonce, parent, grant['nonce'], digest, canonical(event)))
            if failure_point == 'before_commit':
                raise RuntimeError('injected failure before commit')
            db.commit()
            if failure_point == 'after_commit':
                raise RuntimeError('injected failure after commit')
            return {**event, 'idempotent_replay': False}
        except BaseException:
            if db.in_transaction:
                db.rollback()
            raise
        finally:
            db.close()

    def correction_count(self):
        with closing(self._connect()) as db:
            return db.execute('SELECT COUNT(*) FROM correction_events').fetchone()[0]
