"""Atomic, local-only revocation fixture for the fictional Companion signed boundary.

The revocation operator and clock are TEST-HARNESS supplied, not authenticated.
This cannot revoke a real identity or authorization, and performs no external action.
"""
import hashlib
import json
import sqlite3
from contextlib import closing

from authorization_guard_v02 import ContractError, _utc, simulate_once
from authorization_store_v03 import (
    FictionalDurableStore, _check_fictional_evidence_identity, _fingerprint, _canonical
)
from sandbox_issuer_v10 import FictionalSignedBoundary, _verify, APPROVAL_KEYS


def _token_digest(token):
    if not isinstance(token, str) or not token.isascii():
        raise ContractError('non-ASCII fictional token')
    return hashlib.sha256(token.encode('ascii')).hexdigest()


class FictionalRevocableStore(FictionalDurableStore):
    """Serialize local revocations and fictional receipt inserts in ONE SQLite DB."""

    def __init__(self, database_path):
        super().__init__(database_path)
        with closing(self._connect()) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS fictional_revocations (
                token_sha256 TEXT PRIMARY KEY,
                revoked_at TEXT NOT NULL,
                reason TEXT NOT NULL)''')

    def execute(self, *args, **kwargs):
        # Prevent bypassing the revocation gate via the inherited v0.3 API.
        raise ContractError('use FictionalRevocableBoundary for signed fictional execution')

    def revoke_digest(self, digest, *, now, reason):
        # The caller is a synthetic test operator. This does not authenticate them.
        if not isinstance(digest, str) or len(digest) != 64 or any(
            ch not in '0123456789abcdef' for ch in digest
        ):
            raise ContractError('invalid fictional token digest')
        _utc(now)
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 160:
            raise ContractError('invalid fictional revocation reason')
        with closing(self._connect()) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                old = db.execute('SELECT revoked_at,reason FROM fictional_revocations WHERE token_sha256=?',
                                 (digest,)).fetchone()
                if old is None:
                    db.execute('INSERT INTO fictional_revocations VALUES(?,?,?)', (digest, now, reason))
                db.commit()
                return {'synthetic': True, 'token_sha256': digest,
                        'new_revocation': old is None, 'external_actions': 0}
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def _execute_checked(self, scenario, requested_scope, *, principal, now,
                         trusted_principals, approval_digest):
        """Called only AFTER v1.0 token validation; never call as a public API."""
        if not isinstance(approval_digest, str) or len(approval_digest) != 64 or any(
            ch not in '0123456789abcdef' for ch in approval_digest
        ):
            raise ContractError('invalid fictional token digest')
        _check_fictional_evidence_identity(scenario, trusted_principals)
        receipt = simulate_once(scenario, requested_scope, principal=principal,
                                now=now, consumed=set(), trusted_principals=trusted_principals)
        nonce = receipt['nonce']
        fingerprint = _fingerprint(scenario, requested_scope, principal)
        with closing(self._connect()) as db:
            try:
                # BEGIN IMMEDIATE serializes revocation and receipt insertion.
                # No separate precheck-to-insert time-of-check/time-of-use window.
                db.execute('BEGIN IMMEDIATE')
                revoked = db.execute('SELECT 1 FROM fictional_revocations WHERE token_sha256=?',
                                     (approval_digest,)).fetchone()
                if revoked:
                    raise ContractError('fictional approval revoked')
                existing = db.execute('SELECT fingerprint,receipt_json FROM receipts WHERE nonce=?',
                                      (nonce,)).fetchone()
                if existing:
                    if existing[0] != fingerprint:
                        raise ContractError('nonce already bound to different request')
                    # Retain existing v0.3 replay behavior after revocation check.
                    result = {**json.loads(existing[1]), 'idempotent_replay': True}
                else:
                    db.execute('INSERT INTO receipts(nonce,fingerprint,receipt_json) VALUES(?,?,?)',
                               (nonce, fingerprint, _canonical(receipt)))
                    result = {**receipt, 'idempotent_replay': False}
                db.commit()
                return result
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise

    def revocation_count(self):
        with closing(self._connect()) as db:
            return db.execute('SELECT COUNT(*) FROM fictional_revocations').fetchone()[0]


class _RevocationBoundStore:
    """Adapter passed only to the pre-existing signed boundary's execute method."""

    def __init__(self, store, digest):
        self.store = store
        self.digest = digest

    def execute(self, scenario, requested_scope, *, principal, now, trusted_principals):
        return self.store._execute_checked(scenario, requested_scope,
                                           principal=principal, now=now,
                                           trusted_principals=trusted_principals,
                                           approval_digest=self.digest)


class FictionalRevocableBoundary:
    """v1.0 signature verification + atomic local test-only revocation contract."""

    def __init__(self, store, identity_key, approval_key):
        if not isinstance(store, FictionalRevocableStore):
            raise TypeError('fictional revocable SQLite store required')
        self.store = store
        self.approval_key = approval_key
        self.signed = FictionalSignedBoundary(identity_key, approval_key)

    def execute(self, scenario, requested_scope, *, identity_token, approval_token, now):
        digest = _token_digest(approval_token)
        # Reuses ALL v1.0 signature, audience, scope, scenario and time gates.
        return self.signed.execute(_RevocationBoundStore(self.store, digest),
                                   scenario, requested_scope,
                                   identity_token=identity_token,
                                   approval_token=approval_token, now=now)

    def revoke(self, approval_token, *, now, reason):
        # This is an explicitly UNAUTHENTICATED test-harness operation.
        _verify(approval_token, self.approval_key, 'approval', APPROVAL_KEYS)
        return self.store.revoke_digest(_token_digest(approval_token), now=now, reason=reason)
