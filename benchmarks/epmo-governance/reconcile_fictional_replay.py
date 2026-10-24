"""Read-only consistency check between two FICTIONAL EPMO experiments.

This checks replay-to-ledger agreement, not identity, authorization or physical actions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from durable_receipt_sandbox import snapshot
from governance_demo import evaluate, verify_audit


class ReconciliationError(ValueError):
    """Fictional replay and durable ledger do not agree."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def reconcile(scenario: dict, database: str | Path) -> dict:
    """Re-evaluate the exact fictional scenario and compare ALL accepted actions.

    No writes. Caller is responsible for an immutable scenario and quiescent DB.
    """
    if not isinstance(scenario, dict) or scenario.get("origin") != "FICTIONAL_SYNTHETIC":
        raise ReconciliationError("only explicitly fictional scenarios permitted")
    result = evaluate(scenario)
    if not verify_audit(result):
        raise ReconciliationError("replay audit chain invalid")
    expected = {}
    for event, record in zip(scenario["events"], result["audit"]):
        if not record["accepted"]:
            continue
        request_id, kind, payload = event["request_id"], event["type"], event["payload"]
        if kind == "execute":
            receipt_id = payload["receipt_id"]
            if receipt_id in expected:
                raise ReconciliationError("duplicate accepted receipt")
            expected[receipt_id] = {
                "receipt_id": receipt_id,
                "request_id": request_id,
                "approval_id": payload["approval_id"],
                "action": payload["action"],
                "scope": payload["scope"],
                "status": "reserved",
                "correction_reason": None,
            }
        elif kind == "correct":
            receipt_id = payload["receipt_id"]
            if receipt_id not in expected or expected[receipt_id]["request_id"] != request_id:
                raise ReconciliationError("accepted correction without matching execution")
            expected[receipt_id]["status"] = "corrected"
            expected[receipt_id]["correction_reason"] = payload["reason"]
    rows = snapshot(database)
    observed = {}
    for row in rows:
        if row["receipt_id"] in observed:
            raise ReconciliationError("duplicate durable receipt")
        observed[row["receipt_id"]] = row
    if observed != expected:
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        changed = sorted(k for k in set(expected) & set(observed) if expected[k] != observed[k])
        raise ReconciliationError(f"ledger mismatch: missing={missing} extra={extra} changed={changed}")
    return {
        "origin": "FICTIONAL_SYNTHETIC",
        "reconciled": True,
        "accepted_events": result["accepted"],
        "rejected_events": result["rejected"],
        "accepted_executions": len(expected),
        "corrected_receipts": sum(r["status"] == "corrected" for r in expected.values()),
        "scenario_sha256": digest(scenario),
        "ledger_rows_sha256": digest(rows),
        "audit_tip_sha256": result["audit_tip_sha256"],
        "external_actions": 0,
        "identity_authenticated": False,
        "durable_policy_enforced": False,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Read-only fictional replay/SQLite reconciliation")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("sqlite_file", type=Path)
    args = parser.parse_args()
    report = reconcile(json.loads(args.scenario.read_text(encoding="utf-8")), args.sqlite_file)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
