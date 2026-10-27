#!/usr/bin/env python3
"""Additive synthetic-only CORTEX source-span completeness audit.

The frozen evaluator intentionally remains unchanged. This audit measures a
narrow evidence-integrity property, NOT semantic correctness or human utility.
It never prints utterance text, object identifiers, or private submissions.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from baseline import baseline
from evaluator import evaluate, signature, KINDS


def _sources(obj, known, *, gold=False):
    if not isinstance(obj, dict):
        raise ValueError("object is not a mapping")
    values = obj.get("source")
    if not isinstance(values, list):
        if gold:
            raise ValueError("gold object lacks source list")
        return None
    if not values:
        if gold:
            raise ValueError("gold object has no source")
        return set()
    if any(not isinstance(s, str) or not s or s not in known for s in values):
        if gold:
            raise ValueError("gold object cites unknown source")
        return None
    if len(set(values)) != len(values):
        if gold:
            raise ValueError("gold object repeats source")
        return None
    return set(values)


def audit_sources(fixture, candidate):
    """Classify source completeness for exact-field-matched fictional objects.

    Matched fields are *not* a semantic equivalence test. Invalid/missing
    candidate sources are classified rather than silently counted as valid.
    """
    if not isinstance(fixture, dict) or fixture.get("synthetic") is not True:
        raise ValueError("synthetic fixture required")
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be mapping")
    meeting = fixture.get("meeting")
    gold = fixture.get("ground_truth")
    if not isinstance(meeting, dict) or not isinstance(gold, dict):
        raise ValueError("invalid fixture")
    utterances = meeting.get("utterances")
    if not isinstance(utterances, list) or not utterances:
        raise ValueError("missing utterances")
    known = set()
    for row in utterances:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"] or row["id"] in known:
            raise ValueError("invalid or duplicate utterance id")
        known.add(row["id"])
    labels = ("exact", "partial", "extra", "mixed", "missing", "invalid", "unsupported_or_duplicate")
    totals = {name: 0 for name in labels}
    by_kind = {}
    legacy_credit = 0
    for kind in KINDS:
        gs, ps = gold.get(kind), candidate.get(kind)
        if not isinstance(gs, list) or not isinstance(ps, list):
            raise ValueError("missing or invalid category")
        gold_by_sig = {}
        for item in gs:
            if not isinstance(item, dict):
                raise ValueError("malformed gold object")
            key = signature(kind, item)
            if key in gold_by_sig:
                raise ValueError("duplicate gold signature")
            gold_by_sig[key] = _sources(item, known, gold=True)
        counts = {name: 0 for name in labels}
        seen = set()
        for item in ps:
            if not isinstance(item, dict):
                raise ValueError("malformed candidate object")
            key = signature(kind, item)
            if key not in gold_by_sig or key in seen:
                classification = "unsupported_or_duplicate"
            else:
                seen.add(key)
                observed = _sources(item, known)
                expected = gold_by_sig[key]
                if observed is None:
                    classification = "invalid"
                elif not observed:
                    classification = "missing"
                elif observed == expected:
                    classification = "exact"
                elif observed < expected:
                    classification = "partial"
                elif expected < observed:
                    classification = "extra"
                else:
                    classification = "mixed"
                if observed and observed <= expected:
                    legacy_credit += 1
            counts[classification] += 1
            totals[classification] += 1
        by_kind[kind] = counts
    matched = sum(totals[k] for k in labels if k != "unsupported_or_duplicate")
    return {
        "synthetic": True,
        "scope": "exact-field-matched source-span completeness only",
        "matched_objects": matched,
        "counts": totals,
        "by_kind": by_kind,
        "legacy_nonempty_subset_credit_count": legacy_credit,
        "legacy_nonempty_subset_credit_ratio": round(legacy_credit / matched, 6) if matched else None,
        "strict_exact_source_ratio": round(totals["exact"] / matched, 6) if matched else None,
        "semantic_accuracy": "TBD",
        "human_review": "TBD",
        "external_validation": "TBD",
    }


def demo():
    """Frozen original vs one-source-omission negative control; no real data."""
    fixture = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))
    original = baseline(fixture)
    changed = copy.deepcopy(original)
    # The frozen D2 decision cites u06 and u07. Deliberately omit u07.
    if changed["decisions"][1]["source"] != ["u06", "u07"]:
        raise ValueError("frozen fixture/baseline contract changed")
    changed["decisions"][1]["source"] = ["u06"]
    original_eval = evaluate(fixture, original)
    changed_eval = evaluate(fixture, changed)
    if (original_eval["metrics"]["source_span_traceability"] != 1.0
            or changed_eval["metrics"]["source_span_traceability"] != 1.0):
        raise ValueError("frozen evaluator behavior changed")
    if any(original_eval["metrics"][k]["f1"] != changed_eval["metrics"][k]["f1"] for k in KINDS):
        raise ValueError("frozen exact-field matching changed")
    return {
        "fictional": True,
        "negative_control": "one required decision source omitted",
        "original": audit_sources(fixture, original),
        "omitted_source": audit_sources(fixture, changed),
        "frozen_evaluator_source_traceability_original": original_eval["metrics"]["source_span_traceability"],
        "frozen_evaluator_source_traceability_omitted": changed_eval["metrics"]["source_span_traceability"],
        "frozen_evaluator_kind_f1_unchanged": True,
        "real_workflow_metrics": "TBD",
    }


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args != ["demo"]:
        raise SystemExit("usage: python source_span_completeness_v01.py demo")
    print(json.dumps(demo(), sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
