#!/usr/bin/env python3
"""Illustrative, synthetic-only CORTEX -> PROV-O JSON-LD mapping.

Not an RDF/OWL conformance checker, historical-authenticity proof, or extractor.
This maps author-created *ground truth* only; do not score it as model output.
"""
import json
import re
import sys
from pathlib import Path

PROV = "http://www.w3.org/ns/prov#"
CORTEX = "https://example.org/cortex#"
KINDS = ("decisions", "actions", "risks", "dependencies", "conditional_followups")
SINGULAR = {"decisions": "decision", "actions": "action", "risks": "risk",
            "dependencies": "dependency", "conditional_followups": "conditional_followup"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")


def _id(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError("invalid fictional identifier")
    return value


def _ref(kind, value):
    return {"@id": f"urn:cortex:synthetic:{kind}:{_id(value)}"}


def map_fixture(fixture):
    """Fail closed on missing/ambiguous links; never invent historical facts."""
    if not isinstance(fixture, dict) or fixture.get("synthetic") is not True:
        raise ValueError("synthetic-only fixture required")
    meeting, gold, history = fixture["meeting"], fixture["ground_truth"], fixture.get("history", {})
    utterances = meeting["utterances"]
    if not isinstance(utterances, list) or not isinstance(gold, dict):
        raise ValueError("invalid fixture structure")
    utterance_ids = [_id(row["id"]) for row in utterances]
    if len(set(utterance_ids)) != len(utterance_ids):
        raise ValueError("duplicate utterance")
    nodes = [
        {"@id": _ref("utterance", uid)["@id"], "@type": "prov:Entity"}
        for uid in sorted(utterance_ids)
    ]
    records = history.get("records", [])
    historical = gold.get("historical_decisions", [])
    if not isinstance(records, list) or not isinstance(historical, list):
        raise ValueError("invalid archive")
    by_ref = {}
    for row in records:
        ref, decision = _id(row["record_ref"]), _id(row["decision_id"])
        if ref in by_ref:
            raise ValueError("duplicate archive record")
        if not isinstance(row.get("text"), str) or not row["text"].strip():
            raise ValueError("archive record has no content")
        by_ref[ref] = decision
        nodes.append({"@id": _ref("archive", ref)["@id"], "@type": "prov:Entity"})
    history_ids = set()
    for row in historical:
        old, ref = _id(row["id"]), _id(row["record_ref"])
        if old in history_ids:
            raise ValueError("duplicate historical decision")
        history_ids.add(old)
        if by_ref.get(ref) != old:
            raise ValueError("historical decision has no matching archive")
        nodes.append({
            "@id": _ref("decision", old)["@id"], "@type": "prov:Entity",
            "prov:wasDerivedFrom": [_ref("archive", ref)]
        })
    negatives = {uid for row in gold.get("negative_examples", [])
                 for uid in row.get("source", [])}
    seen = set()
    for kind in KINDS:
        rows = gold.get(kind, [])
        if not isinstance(rows, list):
            raise ValueError("invalid ground-truth category")
        for row in rows:
            obj_id = _id(row["id"])
            key = (kind, obj_id)
            if key in seen:
                raise ValueError("duplicate object identifier")
            seen.add(key)
            sources = row["source"]
            if not isinstance(sources, list) or not sources:
                raise ValueError("object without sources")
            if len(set(sources)) != len(sources) or any(
                _id(uid) not in utterance_ids for uid in sources
            ):
                raise ValueError("duplicate or unknown source")
            if any(uid in negatives for uid in sources):
                raise ValueError("negative utterance promoted to governance fact")
            node = {
                "@id": _ref(SINGULAR[kind], obj_id)["@id"],
                "@type": "prov:Entity",
                "prov:wasDerivedFrom": [_ref("utterance", uid) for uid in sorted(sources)]
            }
            if kind == "decisions" and row.get("supersedes") is not None:
                old = _id(row["supersedes"])
                if old == obj_id or old not in history_ids:
                    raise ValueError("unresolved or self-superseding decision")
                # Domain-specific supersession is NOT PROV-O revision.
                node["cortex:supersedes"] = _ref("decision", old)
            nodes.append(node)
    if any(row.get("supersedes") for row in gold.get("decisions", [])) and not historical:
        raise ValueError("missing explicit fictional historical records")
    return {
        "@context": {"prov": PROV, "cortex": CORTEX},
        "@graph": sorted(nodes, key=lambda x: x["@id"])
    }


def main(argv):
    if len(argv) != 1:
        raise SystemExit("usage: python prov_o_mapping_v01.py independent_scenario_v03.json")
    try:
        fixture = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
        result = map_fixture(fixture)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"synthetic": True, "valid": False,
                          "error": type(exc).__name__, "scores": "TBD"}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
