"""Fictional EPMO reviewer-burden packet; no human measurements or external actions.

Public source can reveal the key: procedural blinding only, not cryptographic.
Keep keys and participant responses private, outside the repository.
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
import statistics
from pathlib import Path

ORIGIN = "FICTIONAL_SYNTHETIC"
VERSION = "0.8"
SEED = 20261026


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def event(event_id, kind, at, actor, payload):
    return dict(event_id=event_id, request_id="fictional-RAID-01", type=kind,
                actor=actor, at=f"2026-01-01T{at}Z", payload=payload)


def cases():
    """Predeclared fictional cases aligned to governance_demo.evaluate."""
    submit = event("s1", "submit", "09:00:00", "requester", {"action": "publish_status", "scope": "fictional-program"})
    approve = event("a1", "approve", "09:02:00", "reviewer", {"action": "publish_status", "scope": "fictional-program", "expires_at": "2026-01-01T09:32:00Z"})
    execute = event("x1", "execute", "09:03:00", "executor", {"approval_id": "a1", "action": "publish_status", "scope": "fictional-program", "receipt_id": "r1"})
    correct = event("c1", "correct", "09:04:00", "auditor", {"receipt_id": "r1", "reason": "fictional typo"})

    def change(source, **kwargs):
        result = copy.deepcopy(source)
        for k, v in kwargs.items():
            if k.startswith("payload__"):
                result["payload"][k.split("__", 1)[1]] = v
            else:
                result[k] = v
        return result

    specs = [
        ("A01", [submit], approve),
        ("A02", [submit], change(approve, actor="requester")),
        ("A03", [submit], change(approve, payload__scope="wrong-program")),
        ("A04", [submit], change(approve, payload__expires_at="2026-01-01T11:05:00Z")),
        ("A05", [submit, approve], execute),
        ("A06", [submit], execute),
        ("A07", [submit, approve], change(execute, at="2026-01-01T09:32:00Z")),
        ("A08", [submit, approve], change(execute, payload__scope="wrong-program")),
        ("A09", [submit, approve], change(execute, actor="reviewer")),
        ("A10", [submit, approve, execute], correct),
        ("A11", [submit, approve, execute], change(correct, payload__receipt_id="wrong")),
        ("A12", [submit, approve, execute], change(execute, event_id="x2", at="2026-01-01T09:05:00Z")),
        ("A13", [submit, approve], change(execute, event_id="a1")),
        ("A14", [submit, approve, execute], change(correct, payload__reason="  ")),
        ("A15", [submit, approve], change(execute, at="2026-01-01T09:01:00Z")),
        ("A16", [submit, approve], change(execute, actor="unknown-actor")),
    ]
    return [{"case_id": cid, "context": copy.deepcopy(context), "candidate": copy.deepcopy(candidate)}
            for cid, context, candidate in specs]


def generate(evaluator):
    """Generate two ordered review packets and a separate private oracle key."""
    items = cases()
    roles = {"requester": "requester", "reviewer": "reviewer",
             "executor": "executor", "auditor": "auditor"}
    gold = {}
    for item in items:
        scenario = {"origin": ORIGIN, "declared_roles": roles,
                    "events": item["context"] + [item["candidate"]]}
        audit = evaluator(scenario)["audit"]
        if not all(row["accepted"] for row in audit[:-1]):
            raise ValueError(f"invalid context for {item['case_id']}")
        gold[item["case_id"]] = {"accept": bool(audit[-1]["accepted"]),
                                 "reason": audit[-1]["reason"]}
    order = [item["case_id"] for item in items]
    random.Random(SEED).shuffle(order)
    by_id = {item["case_id"]: item for item in items}

    def packet(arm, ids):
        return {"origin": ORIGIN, "version": VERSION, "arm": arm,
                "policy": "governance_demo.py declared-role fictional policy",
                "instruction": "Mark accept true/false and review seconds for each candidate; no external actions.",
                "cases": [{"case_id": cid, "context": by_id[cid]["context"],
                           "candidate": by_id[cid]["candidate"]} for cid in ids]}

    manual = packet("manual_notes", order)
    structured = packet("structured_packet", list(reversed(order)))
    private_gold = {"origin": ORIGIN, "version": VERSION, "labels": gold,
                    "packet_sha256_by_arm": {
                        "manual_notes": sha(manual),
                        "structured_packet": sha(structured)}}
    return manual, structured, private_gold


def score(packet, gold, response):
    """Score a COMPLETE self-reported response; not independent human verification."""
    if any(x.get("origin") != ORIGIN or x.get("version") != VERSION
           for x in (packet, gold, response)):
        raise ValueError("origin/version mismatch")
    if response.get("arm") != packet.get("arm"):
        raise ValueError("arm mismatch")
    bindings = gold.get("packet_sha256_by_arm")
    if not isinstance(bindings, dict) or set(bindings) != {"manual_notes", "structured_packet"}:
        raise ValueError("missing or invalid packet hash bindings")
    arm = packet.get("arm")
    if type(arm) is not str or type(bindings.get(arm)) is not str or sha(packet) != bindings[arm]:
        raise ValueError("review packet content does not match the private gold binding")
    labels = gold.get("labels")
    if not isinstance(labels, dict) or any(
            not isinstance(item, dict) or type(item.get("accept")) is not bool
            or type(item.get("reason")) is not str for item in labels.values()):
        raise ValueError("invalid private gold label schema")
    ids = [item["case_id"] for item in packet["cases"]]
    if len(ids) != len(set(ids)) or set(ids) != set(gold["labels"]):
        raise ValueError("packet/key mismatch")
    rows = response.get("decisions")
    if not isinstance(rows, list) or len(rows) != len(ids):
        raise ValueError("incomplete reviewer response")
    seen, false_approvals, true_approvals, correct, seconds = set(), 0, 0, 0, []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"case_id", "accept", "seconds"}:
            raise ValueError("invalid response schema")
        cid = row["case_id"]
        if type(cid) is not str or cid not in ids or cid in seen or type(row["accept"]) is not bool:
            raise ValueError("duplicate/unknown case or invalid decision")
        t = row["seconds"]
        if type(t) not in (int, float) or not (0 <= t <= 3600) or t != t:
            raise ValueError("invalid review duration")
        seen.add(cid)
        seconds.append(t)
        expected = gold["labels"][cid]["accept"]
        correct += row["accept"] == expected
        false_approvals += row["accept"] and not expected
        true_approvals += row["accept"] and expected
    negatives = sum(not v["accept"] for v in gold["labels"].values())
    positives = len(ids) - negatives
    return {"origin": ORIGIN, "version": VERSION, "arm": packet["arm"],
            "cases": len(ids), "correct": correct,
            "false_approvals": false_approvals, "negative_cases": negatives,
            "false_approval_rate": false_approvals / negatives if negatives else None,
            "true_approval_recall": true_approvals / positives if positives else None,
            "total_review_seconds": sum(seconds),
            "median_review_seconds": statistics.median(seconds),
            "participant_count_claimed": 1, "independently_verified_human_data": False,
            "source_packet_sha256": sha(packet), "source_gold_sha256": sha(gold)}


def strict_json(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON field")
            obj[key] = value
        return obj
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def main():
    import argparse
    from governance_demo import evaluate
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="PRIVATE new local directory; never commit key/responses")
    mode.add_argument("--score", action="store_true", help="Score private self-reported responses")
    for name in ("packet", "gold", "response"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    if args.score:
        if not all((args.packet, args.gold, args.response)):
            parser.error("--score requires --packet --gold --response")
        print(canonical(score(strict_json(args.packet), strict_json(args.gold),
                              strict_json(args.response))))
        return
    if any((args.packet, args.gold, args.response)):
        parser.error("--packet/--gold/--response are only valid with --score")
    manual, structured, gold = generate(evaluate)
    args.out.mkdir(parents=True, exist_ok=False)
    for name, value in (("manual_packet.json", manual),
                        ("structured_packet.json", structured),
                        ("PRIVATE_gold.json", gold)):
        (args.out / name).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(canonical({"origin": ORIGIN, "version": VERSION, "cases": len(gold["labels"]),
                     "manual_sha256": sha(manual), "structured_sha256": sha(structured),
                     "gold_sha256": sha(gold), "human_review_results": "TBD",
                     "external_actions": 0}))


if __name__ == "__main__":
    main()
