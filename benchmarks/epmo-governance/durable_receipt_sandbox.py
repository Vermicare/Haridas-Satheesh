"""Fictional EPMO SQLite receipt persistence experiment; NO authorization or external actions.

This is an isolated storage primitive, not an authenticated approval gate.
It does not import the production-like (also fictional) governance replay.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import sqlite3
import tempfile
from pathlib import Path

ORIGIN = "FICTIONAL_SYNTHETIC"


class ReceiptConflict(ValueError):
    """An identifier or correction was reused with incompatible content."""


class InjectedFailure(RuntimeError):
    """A controlled simulated crash point, never a real external action."""


def _require_fields(origin, **fields):
    if origin != ORIGIN:
        raise ValueError("only explicitly fictional input is accepted")
    if any(not isinstance(v, str) or not v.strip() for v in fields.values()):
        raise ValueError("all identifiers and fields must be nonblank strings")


def _connect(path):
    conn = sqlite3.connect(str(path), timeout=15, isolation_level=None)
    conn.execute("PRAGMA busy_timeout=15000")
    return conn


def initialize(path):
    """Create the fixture-only schema. Run before concurrent workers start."""
    with closing(_connect(path)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS receipts (
            receipt_id TEXT PRIMARY KEY,
            request_id TEXT NOT NULL UNIQUE,
            approval_id TEXT NOT NULL,
            action TEXT NOT NULL,
            scope TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('reserved','corrected')),
            correction_reason TEXT
        )""")


def record_simulated_receipt(path, *, origin=ORIGIN, request_id, receipt_id,
                             approval_id, action, scope, failpoint=None):
    """Atomically reserve a *fictional* receipt; identical retries are idempotent.

    An approval_id is merely a caller-provided string: this function does NOT
    authenticate actors or validate approval policy, expiry or execution.
    """
    _require_fields(origin, request_id=request_id, receipt_id=receipt_id,
                    approval_id=approval_id, action=action, scope=scope)
    if failpoint not in (None, "before_commit", "after_commit"):
        raise ValueError("unknown failpoint")
    db = _connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute("SELECT receipt_id, request_id, approval_id, action, scope "
                         "FROM receipts WHERE receipt_id=? OR request_id=?",
                         (receipt_id, request_id)).fetchall()
        requested = (receipt_id, request_id, approval_id, action, scope)
        if old:
            if len(old) != 1 or old[0] != requested:
                raise ReceiptConflict("receipt/request identifier collision or changed binding")
            db.execute("COMMIT")
            return {"outcome": "idempotent", "receipt_id": receipt_id, "external_actions": 0}
        db.execute("INSERT INTO receipts VALUES (?,?,?,?,?,'reserved',NULL)", requested)
        if failpoint == "before_commit":
            raise InjectedFailure("fictional crash before transaction commit")
        db.execute("COMMIT")
        if failpoint == "after_commit":
            raise InjectedFailure("fictional crash after transaction commit")
        return {"outcome": "created", "receipt_id": receipt_id, "external_actions": 0}
    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()


def record_simulated_correction(path, *, origin=ORIGIN, request_id, receipt_id,
                                reason, failpoint=None):
    """Persist a fictional correction marker; no real rollback/compensation."""
    _require_fields(origin, request_id=request_id, receipt_id=receipt_id, reason=reason)
    if failpoint not in (None, "before_commit", "after_commit"):
        raise ValueError("unknown failpoint")
    db = _connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT request_id, status, correction_reason FROM receipts "
                         "WHERE receipt_id=?", (receipt_id,)).fetchone()
        if row is None or row[0] != request_id:
            raise ReceiptConflict("correction receipt/request binding mismatch")
        if row[1] == "corrected":
            if row[2] != reason:
                raise ReceiptConflict("correction reason changed on replay")
            db.execute("COMMIT")
            return {"outcome": "idempotent", "receipt_id": receipt_id, "external_actions": 0}
        db.execute("UPDATE receipts SET status='corrected', correction_reason=? "
                   "WHERE receipt_id=?", (reason, receipt_id))
        if failpoint == "before_commit":
            raise InjectedFailure("fictional correction crash before commit")
        db.execute("COMMIT")
        if failpoint == "after_commit":
            raise InjectedFailure("fictional correction crash after commit")
        return {"outcome": "corrected", "receipt_id": receipt_id, "external_actions": 0}
    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()


def snapshot(path):
    """Deterministic inspectable fictional state, excluding filesystem metadata."""
    with closing(_connect(path)) as db:
        rows = db.execute("SELECT receipt_id, request_id, approval_id, action, scope, "
                          "status, correction_reason FROM receipts ORDER BY receipt_id").fetchall()
    return [dict(zip(("receipt_id", "request_id", "approval_id", "action", "scope",
                      "status", "correction_reason"), row)) for row in rows]


def demonstration():
    with tempfile.TemporaryDirectory(prefix="epmo-fictional-") as folder:
        path = Path(folder) / "ledger.sqlite3"
        initialize(path)
        kwargs = dict(request_id="fictional-request-01", receipt_id="fictional-receipt-01",
                      approval_id="fictional-approval-01", action="publish_fictional_status",
                      scope="fictional-program")
        created = record_simulated_receipt(path, **kwargs)
        replay = record_simulated_receipt(path, **kwargs)
        corrected = record_simulated_correction(path, request_id=kwargs["request_id"],
                                                receipt_id=kwargs["receipt_id"],
                                                reason="fictional correction")
        return {"origin": ORIGIN, "outcomes": [created["outcome"], replay["outcome"],
                                               corrected["outcome"]],
                "rows": snapshot(path), "external_actions": 0,
                "identity_authenticated": False, "approval_policy_verified": False}


def main():
    parser = argparse.ArgumentParser(description="Run fictional durable receipt demo (stdlib only)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(demonstration(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
