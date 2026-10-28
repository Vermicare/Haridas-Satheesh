#!/usr/bin/env python3
"""Synthetic-only CORTEX recall-aware citation audit (additive; frozen scorer unchanged).

A matched-only exact-source ratio can remain perfect when candidate records vanish.
This diagnostic makes the denominator explicit and separately fails on duplicates.
No real reviewer records, source text, or private inputs are emitted.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from baseline import baseline
from evaluator import KINDS, evaluate
from source_span_completeness_v01 import audit_sources


def audit_gold_coverage(fixture: dict, candidate: dict) -> dict:
    """Count exact citations over *all gold records*, not just matched predictions."""
    audit = audit_sources(fixture, candidate)  # validates synthetic fixture and shape
    gold_count = sum(len(fixture["ground_truth"][kind]) for kind in KINDS)
    matched = audit["matched_objects"]
    if matched > gold_count:
        raise ValueError("matched predictions exceed gold count")
    exact = audit["counts"]["exact"]
    unsupported = audit["counts"]["unsupported_or_duplicate"]
    omitted = gold_count - matched
    return {
        "synthetic": True,
        "scope": "gold-denominator exact-field and exact-citation coverage; not semantic accuracy",
        "gold_records": gold_count,
        "matched_records": matched,
        "omitted_gold_records": omitted,
        "exact_citation_records": exact,
        "unsupported_or_duplicate_candidates": unsupported,
        "matched_only_exact_ratio": audit["strict_exact_source_ratio"],
        "gold_denominator_exact_ratio": round(exact / gold_count, 6) if gold_count else None,
        "complete_clean_gate": bool(gold_count and exact == gold_count and unsupported == 0),
        "human_agreement": "TBD",
        "semantic_accuracy": "TBD",
        "review_time_minutes": "TBD",
        "external_validation": "TBD",
    }


def demo() -> dict:
    fixture = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))
    original = baseline(fixture)
    missing = copy.deepcopy(original)
    missing["decisions"].pop()
    duplicated = copy.deepcopy(original)
    duplicated["decisions"].append(copy.deepcopy(duplicated["decisions"][0]))
    original_legacy = evaluate(fixture, original)["metrics"]["source_span_traceability"]
    missing_legacy = evaluate(fixture, missing)["metrics"]["source_span_traceability"]
    return {
        "fictional": True,
        "negative_control": "one gold decision omitted; one extra duplicate candidate",
        "original": audit_gold_coverage(fixture, original),
        "omitted": audit_gold_coverage(fixture, missing),
        "duplicate": audit_gold_coverage(fixture, duplicated),
        "frozen_traceability_original": original_legacy,
        "frozen_traceability_omitted": missing_legacy,
        "real_workflow_metrics": "TBD",
    }


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args != ["demo"]:
        raise SystemExit("usage: python source_span_gold_coverage_v02.py demo")
    print(json.dumps(demo(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
