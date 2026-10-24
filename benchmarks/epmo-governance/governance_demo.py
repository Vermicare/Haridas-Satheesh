"""Fictional, side-effect-free EPMO governance event replay; NOT authenticated authorization."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timezone is required")
    return dt.timestamp()


def evaluate(scenario):
    """Deterministically replay a fictional scenario; never execute external actions."""
    if scenario.get("origin") != "FICTIONAL_SYNTHETIC":
        raise ValueError("only explicitly fictional fixtures are accepted")
    roles = scenario["declared_roles"]
    if not isinstance(roles, dict) or not isinstance(scenario["events"], list):
        raise ValueError("invalid scenario structure")
    requests, seen, receipt_ids, audit, previous_hash = {}, set(), set(), [], "GENESIS"
    for index, event in enumerate(scenario["events"]):
        accepted, reason = False, ""
        event_hash = digest(event)
        event_id = event.get("event_id") if isinstance(event, dict) else None
        request_id = event.get("request_id") if isinstance(event, dict) else None
        try:
            if not isinstance(event, dict):
                raise ValueError("event must be object")
            if set(event) != {"event_id", "request_id", "type", "actor", "at", "payload"}:
                raise ValueError("invalid event keys")
            if not isinstance(event_id, str) or not event_id or event_id in seen:
                raise ValueError("missing or duplicate event_id")
            # Even rejected events consume an ID; a bad attempt cannot later be replayed.
            seen.add(event_id)
            if not isinstance(request_id, str) or not request_id:
                raise ValueError("missing request_id")
            if not isinstance(event["payload"], dict):
                raise ValueError("payload must be object")
            at = timestamp(event["at"])
            role = roles.get(event["actor"])
            if role is None:
                raise ValueError("undeclared actor")
            state = requests.get(request_id)
            if state is not None and at < state["last_at"]:
                raise ValueError("non-monotonic request time")
            typ, payload = event["type"], event["payload"]
            if typ == "submit":
                if state is not None or role != "requester":
                    raise ValueError("submission requires new request and requester role")
                if set(payload) != {"action", "scope"} or not all(isinstance(payload[k], str) and payload[k] for k in payload):
                    raise ValueError("invalid request action/scope")
                requests[request_id] = {"status": "submitted", "requester": event["actor"], "action": payload["action"], "scope": payload["scope"], "last_at": at, "approval_id": None, "expires_at": None, "receipt_id": None}
            elif typ == "approve":
                if state is None or state["status"] != "submitted":
                    raise ValueError("approval requires submitted request")
                if role != "reviewer" or event["actor"] == state["requester"]:
                    raise ValueError("reviewer separation-of-duties failure")
                if set(payload) != {"action", "scope", "expires_at"} or payload["action"] != state["action"] or payload["scope"] != state["scope"]:
                    raise ValueError("approval scope mismatch")
                expiry = timestamp(payload["expires_at"])
                if not (at < expiry <= at + 3600):
                    raise ValueError("approval expiry must be within one hour")
                state.update(status="approved", approval_id=event_id, expires_at=expiry, last_at=at)
            elif typ == "execute":
                if state is None or state["status"] != "approved":
                    raise ValueError("execution requires unused approval")
                if role != "executor" or set(payload) != {"approval_id", "action", "scope", "receipt_id"}:
                    raise ValueError("invalid executor or receipt schema")
                if payload["approval_id"] != state["approval_id"] or payload["action"] != state["action"] or payload["scope"] != state["scope"]:
                    raise ValueError("approval binding mismatch")
                if not isinstance(payload["receipt_id"], str) or not payload["receipt_id"]:
                    raise ValueError("missing receipt id")
                if at >= state["expires_at"]:
                    raise ValueError("expired approval")
                if payload["receipt_id"] in receipt_ids:
                    raise ValueError("duplicate receipt_id across requests")
                receipt_ids.add(payload["receipt_id"])
                state.update(status="executed", receipt_id=payload["receipt_id"], last_at=at)
            elif typ == "correct":
                if state is None or state["status"] != "executed":
                    raise ValueError("correction requires executed request")
                if role != "auditor" or set(payload) != {"receipt_id", "reason"} or payload["receipt_id"] != state["receipt_id"]:
                    raise ValueError("correction receipt binding failure")
                if not isinstance(payload["reason"], str) or not payload["reason"].strip():
                    raise ValueError("correction requires reason")
                state.update(status="corrected", last_at=at)
            else:
                raise ValueError("unknown event type")
            accepted = True
            reason = "accepted"
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            reason = str(exc)
        record = {"index": index, "event_id": event_id, "request_id": request_id, "input_sha256": event_hash, "accepted": accepted, "reason": reason, "prev_hash": previous_hash}
        record["record_hash"] = digest(record)
        previous_hash = record["record_hash"]
        audit.append(record)
    return {"fixture_origin": scenario["origin"], "accepted": sum(r["accepted"] for r in audit), "rejected": sum(not r["accepted"] for r in audit), "requests": {key: {k: v for k, v in state.items() if k != "last_at" and k != "expires_at"} for key, state in sorted(requests.items())}, "audit": audit, "audit_tip_sha256": previous_hash, "external_actions": 0}


def verify_audit(result):
    previous = "GENESIS"
    for record in result["audit"]:
        if record["prev_hash"] != previous or record["record_hash"] != digest({k: v for k, v in record.items() if k != "record_hash"}):
            return False
        previous = record["record_hash"]
    return result["audit_tip_sha256"] == previous


def main():
    parser = argparse.ArgumentParser(description="Replay FICTIONAL EPMO approvals without side effects")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = evaluate(json.loads(args.scenario.read_text(encoding="utf-8")))
    if not verify_audit(result):
        raise SystemExit("audit integrity failure")
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
