"""Fictional SQLite approval consumption; NOT authenticated or production-safe.

A transaction binds a declared actor/action/scope/nonce to one receipt.
All clocks and identities are caller-supplied TEST VALUES. No external actions.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

ORIGIN = "FICTIONAL_SYNTHETIC"


class FictionalInputError(ValueError):
    pass


class InjectedFailure(RuntimeError):
    pass


def _check(origin, **fields):
    if origin != ORIGIN:
        raise FictionalInputError("only explicitly fictional inputs accepted")
    if any(type(value) is not str or not value.strip() for value in fields.values()):
        raise FictionalInputError("all identifiers must be nonblank strings")


def _time(value):
    if type(value) is not int or value < 0:
        raise FictionalInputError("test clock must be a nonnegative integer")


def _db(path):
    db = sqlite3.connect(str(path), timeout=15, isolation_level=None)
    db.execute("PRAGMA busy_timeout=15000")
    return db


def initialize(path: str | Path):
    """Initialize before launching concurrent workers."""
    with closing(_db(path)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS approvals (
            approval_id TEXT PRIMARY KEY, actor_id TEXT NOT NULL,
            action TEXT NOT NULL, scope TEXT NOT NULL,
            nonce TEXT NOT NULL UNIQUE, expires_at INTEGER NOT NULL,
            consumed_request TEXT UNIQUE, consumed_receipt TEXT UNIQUE
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS consumption_receipts (
            receipt_id TEXT PRIMARY KEY, request_id TEXT NOT NULL UNIQUE,
            approval_id TEXT NOT NULL UNIQUE,
            actor_id TEXT NOT NULL, action TEXT NOT NULL,
            scope TEXT NOT NULL, nonce TEXT NOT NULL,
            consumed_at INTEGER NOT NULL
        )""")


def seed_fictional_approval(path, *, approval_id, actor_id, action, scope,
                            nonce, expires_at, origin=ORIGIN):
    """TEST SEED ONLY: does not verify who issued an approval."""
    _check(origin, approval_id=approval_id, actor_id=actor_id, action=action,
           scope=scope, nonce=nonce)
    _time(expires_at)
    with closing(_db(path)) as db:
        db.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?,NULL,NULL)",
                   (approval_id, actor_id, action, scope, nonce, expires_at))


def consume_fictional_approval(path, *, approval_id, request_id, receipt_id,
                               actor_id, action, scope, nonce, now,
                               origin=ORIGIN, failpoint=None):
    """One durable fictional consumption; identical retries return idempotent.

    `now` and `actor_id` are untrusted caller assertions, NOT security inputs.
    The returned receipt is a database record, not proof of an external action.
    """
    _check(origin, approval_id=approval_id, request_id=request_id,
           receipt_id=receipt_id, actor_id=actor_id, action=action,
           scope=scope, nonce=nonce)
    _time(now)
    if failpoint not in (None, "before_commit", "after_commit"):
        raise FictionalInputError("unknown failpoint")
    db = _db(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT actor_id, action, scope, nonce, expires_at, "
                         "consumed_request, consumed_receipt FROM approvals "
                         "WHERE approval_id=?", (approval_id,)).fetchone()
        reason = None
        if row is None:
            reason = "unknown_approval"
        elif row[5] is not None:
            prior = db.execute("SELECT request_id, receipt_id, approval_id, actor_id, "
                               "action, scope, nonce FROM consumption_receipts "
                               "WHERE approval_id=?", (approval_id,)).fetchone()
            expected = (request_id, receipt_id, approval_id, actor_id, action, scope, nonce)
            if row[5:7] == (request_id, receipt_id) and prior == expected:
                db.execute("COMMIT")
                return {"outcome": "idempotent", "receipt_id": receipt_id,
                        "external_actions": 0, "identity_authenticated": False}
            reason = "already_consumed"
        elif row[:4] != (actor_id, action, scope, nonce):
            reason = "binding_mismatch"
        elif now >= row[4]:
            reason = "expired"
        if reason:
            db.execute("COMMIT")
            return {"outcome": "rejected", "reason": reason,
                    "external_actions": 0, "identity_authenticated": False}
        # A request or receipt collision across distinct approvals is rejected
        # atomically. The approval stays unconsumed on rollback.
        try:
            db.execute("INSERT INTO consumption_receipts VALUES (?,?,?,?,?,?,?,?)",
                       (receipt_id, request_id, approval_id, actor_id,
                        action, scope, nonce, now))
        except sqlite3.IntegrityError:
            db.execute("ROLLBACK")
            return {"outcome": "rejected", "reason": "receipt_or_request_collision",
                    "external_actions": 0, "identity_authenticated": False}
        db.execute("UPDATE approvals SET consumed_request=?, consumed_receipt=? "
                   "WHERE approval_id=? AND consumed_request IS NULL",
                   (request_id, receipt_id, approval_id))
        if failpoint == "before_commit":
            raise InjectedFailure("fictional crash before commit")
        db.execute("COMMIT")
        if failpoint == "after_commit":
            raise InjectedFailure("fictional crash after commit")
        return {"outcome": "consumed", "receipt_id": receipt_id,
                "external_actions": 0, "identity_authenticated": False}
    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()


def snapshot(path):
    with closing(_db(path)) as db:
        approvals = db.execute("SELECT approval_id, consumed_request, consumed_receipt "
                               "FROM approvals ORDER BY approval_id").fetchall()
        receipts = db.execute("SELECT receipt_id, request_id, approval_id, actor_id, "
                              "action, scope, nonce, consumed_at FROM consumption_receipts "
                              "ORDER BY receipt_id").fetchall()
    return {"origin": ORIGIN,
            "approvals": [dict(zip(("approval_id", "consumed_request", "consumed_receipt"), r))
                          for r in approvals],
            "receipts": [dict(zip(("receipt_id", "request_id", "approval_id", "actor_id",
                                   "action", "scope", "nonce", "consumed_at"), r))
                         for r in receipts],
            "external_actions": 0, "identity_authenticated": False,
            "trusted_clock": False}
