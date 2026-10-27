"""Fictional EPMO reviewer treatment v0.9: distinct aids, zero human results.

This is NOT authenticated authorization or a human-performance result. Gold and
responses must remain private; the public deterministic source reveals labels.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from blinded_review_preflight_v08 import (ORIGIN, generate as generate_v08,
                                           score as score_v08, sha)
from governance_demo import evaluate

VERSION = "0.9"
QUESTIONS = [
    "Compare declared actor role and separation of duties.",
    "Compare requested action and scope with approval and candidate.",
    "Check event ordering, expiry, reused IDs and receipt references.",
    "Record accept or reject; do not execute any action.",
]


def worksheet(case):
    """Derived display fields only; never compute a policy verdict or reason."""
    context = case["context"]
    candidate = case["candidate"]
    submissions = [e for e in context if e["type"] == "submit"]
    approvals = [e for e in context if e["type"] == "approve"]
    receipts = [e for e in context if e["type"] in ("execute", "correct")]

    def row(e):
        return {"event_id": e["event_id"], "actor": e["actor"],
                "at": e["at"], "request_id": e["request_id"],
                "type": e["type"], "payload": copy.deepcopy(e["payload"])}

    return {"case_id": case["case_id"],
            "submission_fields": [row(e) for e in submissions],
            "approval_fields": [row(e) for e in approvals],
            "prior_execution_or_correction": [row(e) for e in receipts],
            "candidate_fields": row(candidate),
            "review_questions": list(QUESTIONS)}


def generate():
    """Same raw 16 cases and order, with/without a deterministic comparison aid."""
    old_manual, old_structured, old_gold = generate_v08(evaluate)
    manual = copy.deepcopy(old_manual)
    structured = copy.deepcopy(old_structured)
    by_id = {case["case_id"]: case for case in structured["cases"]}
    structured["cases"] = [copy.deepcopy(by_id[c["case_id"]]) for c in manual["cases"]]
    for packet, presentation in ((manual, "raw_event_notes"),
                                 (structured, "field_comparison_worksheet")):
        packet["version"] = VERSION
        packet["presentation"] = presentation
        packet["instruction"] = ("Inspect the fictional events, then record one "
                                 "accept/reject decision and elapsed seconds per case. "
                                 "Do not execute actions. No automated verdict is shown.")
    structured["review_aid"] = [worksheet(c) for c in structured["cases"]]
    gold = {"origin": ORIGIN, "version": VERSION,
            "labels": copy.deepcopy(old_gold["labels"]),
            "packet_sha256_by_arm": {"manual_notes": sha(manual),
                                     "structured_packet": sha(structured)},
            "source_v08_gold_sha256": sha(old_gold)}
    return manual, structured, gold


def score(packet, gold, response):
    """Fail closed on packet/key drift; delegate metrics to frozen v0.8 scorer."""
    expected_manual, expected_structured, expected_gold = generate()
    expected = {"manual_notes": expected_manual,
                "structured_packet": expected_structured}
    if not isinstance(packet, dict) or not isinstance(gold, dict) or not isinstance(response, dict):
        raise ValueError("packet/key/response must be objects")
    arm = packet.get("arm")
    if type(arm) is not str or arm not in expected or packet != expected[arm]:
        raise ValueError("unrecognized or modified review treatment")
    if gold != expected_gold:
        raise ValueError("private key does not match frozen treatment")
    if set(response) != {"origin", "version", "arm", "decisions"}:
        raise ValueError("invalid response fields")
    if (response["origin"], response["version"], response["arm"]) != (ORIGIN, VERSION, arm):
        raise ValueError("response origin/version/arm mismatch")
    old_manual, old_structured, old_gold = generate_v08(evaluate)
    old_packet = old_manual if arm == "manual_notes" else old_structured
    old_response = copy.deepcopy(response)
    old_response["version"] = "0.8"
    result = score_v08(old_packet, old_gold, old_response)
    result.update(version=VERSION, source_packet_sha256=sha(packet),
                  source_gold_sha256=sha(gold), treatment=packet["presentation"],
                  independently_verified_human_data=False)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path, help="new PRIVATE directory outside Git")
    group.add_argument("--demo", action="store_true", help="display treatment difference only")
    args = parser.parse_args()
    manual, structured, gold = generate()
    if args.demo:
        print(json.dumps({"origin": ORIGIN, "version": VERSION,
                          "cases": len(manual["cases"]),
                          "identical_raw_cases": manual["cases"] == structured["cases"],
                          "manual_aid_count": len(manual.get("review_aid", [])),
                          "structured_aid_count": len(structured["review_aid"]),
                          "manual_sha256": sha(manual),
                          "structured_sha256": sha(structured),
                          "human_results": "TBD", "external_actions": 0}, sort_keys=True))
        return
    target = args.out.resolve()
    if any((parent / ".git").exists() for parent in (target, *target.parents)):
        parser.error("private output must be outside every Git checkout or worktree")
    if target.exists():
        parser.error("private output directory already exists")
    target.mkdir(parents=True)
    for name, value in (("manual_packet.json", manual),
                        ("structured_packet.json", structured),
                        ("PRIVATE_gold.json", gold)):
        (target / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("Generated fictional reviewer packets and PRIVATE gold; no human results.")


if __name__ == "__main__":
    main()
