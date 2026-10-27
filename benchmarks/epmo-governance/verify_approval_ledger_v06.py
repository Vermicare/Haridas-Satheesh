"""Read-only structural integrity audit of the *fictional* v0.5 SQLite gate.

This is not authentication, tamper-proof logging, trusted time, or evidence of
an external action. A privileged writer can forge mutually consistent tables.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

ORIGIN = "FICTIONAL_SYNTHETIC"
APPROVAL_COLUMNS = ("approval_id", "actor_id", "action", "scope", "nonce",
                    "expires_at", "consumed_request", "consumed_receipt")
RECEIPT_COLUMNS = ("receipt_id", "request_id", "approval_id", "actor_id",
                   "action", "scope", "nonce", "consumed_at")


class LedgerIntegrityError(ValueError):
    """Fictional database violates a declared structural invariant."""


def _nonblank(value):
    return type(value) is str and bool(value.strip())


def _valid_time(value):
    return type(value) is int and value >= 0


def _rows(db, table, columns):
    actual = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
    if not set(columns) <= actual:
        raise LedgerIntegrityError(f"missing required {table} schema")
    rows = db.execute(f"SELECT {', '.join(columns)} FROM {table} ORDER BY {columns[0]}")
    return [dict(zip(columns, row)) for row in rows]


def verify(path: str | Path, *, origin: str = ORIGIN) -> dict:
    """Inspect one consistent read-only SQLite snapshot; never mutate it."""
    if origin != ORIGIN:
        raise LedgerIntegrityError("only explicitly fictional origin is permitted")
    path = Path(path)
    if not path.is_file():
        raise LedgerIntegrityError("fictional database not found")
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            db.execute("PRAGMA query_only=ON")
            db.execute("BEGIN")
            approvals = _rows(db, "approvals", APPROVAL_COLUMNS)
            receipts = _rows(db, "consumption_receipts", RECEIPT_COLUMNS)
            db.execute("COMMIT")
    except sqlite3.Error as exc:
        raise LedgerIntegrityError(f"database unreadable or malformed: {exc}") from exc

    by_approval = {}
    nonces = set()
    for a in approvals:
        if any(not _nonblank(a[k]) for k in APPROVAL_COLUMNS[:5]):
            raise LedgerIntegrityError("malformed approval identifiers")
        if not _valid_time(a["expires_at"]):
            raise LedgerIntegrityError("invalid approval expiry")
        if a["approval_id"] in by_approval or a["nonce"] in nonces:
            raise LedgerIntegrityError("duplicate approval ID or nonce")
        by_approval[a["approval_id"]] = a
        nonces.add(a["nonce"])
        pair = (a["consumed_request"], a["consumed_receipt"])
        if pair != (None, None) and not all(_nonblank(x) for x in pair):
            raise LedgerIntegrityError("partially consumed or malformed approval")

    seen_receipts, seen_requests, seen_approvals = set(), set(), set()
    for r in receipts:
        if any(not _nonblank(r[k]) for k in RECEIPT_COLUMNS[:7]):
            raise LedgerIntegrityError("malformed receipt identifiers")
        if not _valid_time(r["consumed_at"]):
            raise LedgerIntegrityError("invalid receipt time")
        if (r["receipt_id"] in seen_receipts or r["request_id"] in seen_requests
                or r["approval_id"] in seen_approvals):
            raise LedgerIntegrityError("duplicate receipt/request/approval consumption")
        seen_receipts.add(r["receipt_id"])
        seen_requests.add(r["request_id"])
        seen_approvals.add(r["approval_id"])
        a = by_approval.get(r["approval_id"])
        if a is None:
            raise LedgerIntegrityError("orphan receipt")
        if (a["consumed_request"], a["consumed_receipt"]) != (r["request_id"], r["receipt_id"]):
            raise LedgerIntegrityError("receipt and approval consumption mismatch")
        if any(a[k] != r[k] for k in ("actor_id", "action", "scope", "nonce")):
            raise LedgerIntegrityError("receipt binding mismatch")
        if r["consumed_at"] >= a["expires_at"]:
            raise LedgerIntegrityError("receipt outside approval validity interval")

    for a in approvals:
        consumed = a["consumed_request"] is not None
        if consumed != (a["approval_id"] in seen_approvals):
            raise LedgerIntegrityError("missing receipt or unconsumed approval has receipt")

    serialized = json.dumps({"approvals": approvals, "receipts": receipts},
                            sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {"origin": ORIGIN, "structurally_consistent": True,
            "approvals": len(approvals), "consumed_approvals": len(seen_approvals),
            "receipts": len(receipts),
            "snapshot_sha256": hashlib.sha256(serialized.encode("ascii")).hexdigest(),
            "identity_authenticated": False, "trusted_clock": False,
            "tamper_proof": False, "external_actions": 0}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sqlite_file", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.sqlite_file), sort_keys=True, indent=2))
