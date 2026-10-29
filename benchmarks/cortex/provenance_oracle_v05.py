#!/usr/bin/env python3
"""CORTEX v0.5: post-hoc, gold-aware provenance audit for fictional fixtures.

This is an EVALUATION oracle, not an extractor, runtime guard, or semantic judge.
Only aggregate counts are emitted. Completed human annotations stay private.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

KINDS = ("decisions", "actions", "risks", "dependencies", "conditional_followups")
FIELDS = {
    "decisions": ("statement", "status", "supersedes"),
    "actions": ("owner", "due", "action"),
    "risks": ("status", "statement"),
    "dependencies": ("statement",),
    "conditional_followups": ("condition", "action"),
}
VERSION = "cortex-fictional-provenance-oracle-v0.5"


def _norm(value):
    return None if value is None else " ".join(str(value).strip().lower().split())


def _signature(kind, obj):
    return tuple(_norm(obj.get(field)) for field in FIELDS[kind])


def audit(fixture: dict, candidate: dict) -> dict:
    """Compare source provenance to frozen gold; never claim semantic accuracy."""
    if fixture.get("synthetic") is not True or not isinstance(candidate, dict):
        raise ValueError("fictional fixture required")
    meeting = fixture["meeting"]["utterances"]
    gold = fixture["ground_truth"]
    valid_ids = [u["id"] for u in meeting]
    if len(valid_ids) != len(set(valid_ids)):
        raise ValueError("duplicate fixture utterance IDs")
    valid = set(valid_ids)
    negative = {s for x in gold.get("negative_examples", []) for s in x["source"]}
    counts = Counter()
    gold_duplicate_signatures = 0
    for kind in KINDS:
        expected = gold.get(kind, [])
        if not isinstance(expected, list) or not isinstance(candidate.get(kind, []), list):
            raise ValueError("object arrays required")
        signatures = [_signature(kind, obj) for obj in expected]
        gold_duplicate_signatures += len(signatures) - len(set(signatures))
        lookup = {_signature(kind, obj): obj for obj in expected}
        for obj in candidate.get(kind, []):
            if not isinstance(obj, dict):
                raise ValueError("objects must be mappings")
            counts["candidate_objects"] += 1
            sources = obj.get("source")
            if not isinstance(sources, list) or not sources or not all(isinstance(s, str) for s in sources):
                counts["missing_or_malformed_source"] += 1
                continue
            source_set = set(sources)
            if len(source_set) != len(sources):
                counts["duplicate_source_ids"] += 1
            if source_set - valid:
                counts["unknown_source_ids_objects"] += 1
            if source_set & negative:
                counts["negative_source_objects"] += 1
            matched = lookup.get(_signature(kind, obj))
            if matched is None:
                counts["unmatched_semantic_signature_objects"] += 1
                continue
            counts["gold_signature_matched_objects"] += 1
            gold_sources = set(matched.get("source", []))
            if source_set == gold_sources and len(sources) == len(source_set):
                counts["exact_gold_source_objects"] += 1
            elif source_set < gold_sources:
                counts["incomplete_gold_source_objects"] += 1
            else:
                counts["other_gold_source_mismatch_objects"] += 1
    # The original fixture names D0 as a predecessor but has no D0 archive.
    # This must remain explicitly unresolved, not treated as verified lineage.
    local_decision_ids = {d.get("id") for d in gold.get("decisions", [])}
    unresolved = sum(bool(d.get("supersedes")) and d["supersedes"] not in local_decision_ids
                     for d in gold.get("decisions", []))
    hard_fail = sum(counts[k] for k in (
        "missing_or_malformed_source", "duplicate_source_ids", "unknown_source_ids_objects",
        "negative_source_objects", "incomplete_gold_source_objects",
        "other_gold_source_mismatch_objects", "unmatched_semantic_signature_objects"))
    return {
        "schema": VERSION, "fictional": True, "evaluation_only": True,
        "source_integrity_gate": ("NOT_EVALUABLE" if not counts["candidate_objects"]
                                  else "FAIL" if hard_fail or gold_duplicate_signatures else "PASS"),
        "counts": {key: counts[key] for key in (
            "candidate_objects", "gold_signature_matched_objects", "exact_gold_source_objects",
            "incomplete_gold_source_objects", "other_gold_source_mismatch_objects",
            "unknown_source_ids_objects", "duplicate_source_ids", "negative_source_objects",
            "missing_or_malformed_source", "unmatched_semantic_signature_objects")},
        "gold_duplicate_signatures": gold_duplicate_signatures,
        "unresolved_external_predecessor_refs": unresolved,
        "external_predecessor_validation": "TBD" if unresolved else "NOT_APPLICABLE",
        "human_independence": "TBD", "semantic_accuracy": "TBD",
        "correction_burden": "TBD", "real_world_validity": "TBD",
    }


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit("usage: provenance_oracle_v05.py FICTIONAL_FIXTURE.json CANDIDATE.json")
    for path in args:
        if Path(path).stat().st_size > 1024 * 1024:
            raise SystemExit("input exceeds 1 MiB")
    fixture = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    candidate = json.loads(Path(args[1]).read_text(encoding="utf-8"))
    print(json.dumps(audit(fixture, candidate), sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
