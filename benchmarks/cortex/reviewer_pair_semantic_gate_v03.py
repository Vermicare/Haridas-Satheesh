#!/usr/bin/env python3
"""CORTEX v0.3 private reviewer-pair readiness gate; fictional inputs only.

A v0.1 pair may pass with source-only objects, while v0.2 checks semantic
annotation fields one submission at a time. This additive gate requires both
checks for BOTH reviewers. It never claims semantic agreement or independence.
Do not commit completed reviewer submissions or identifying information.
"""
from __future__ import annotations

import json
import sys

from reviewer_pair_preflight_v01 import compare_pair, _bounded_load
from semantic_annotation_contract_v02 import validate_semantic_annotation

VERSION = "cortex-fictional-pair-v0.3"


def compare_semantic_pair(case: object, archive: object, first: object,
                          second: object, case_sha: str, archive_sha: str) -> dict:
    """Return only aggregate counts or bounded error codes, never source text."""
    legacy = compare_pair(case, archive, first, second, case_sha, archive_sha)
    errors = list(legacy.get("errors", []))
    for index, submission in enumerate((first, second)):
        if validate_semantic_annotation(submission):
            errors.append(f"reviewer[{index}]:semantic_shape_invalid")
    if errors:
        return {
            "fictional": True, "schema": VERSION, "pair_ready": False,
            "errors": sorted(set(errors)), "semantic_agreement": "TBD",
            "human_independence": "TBD", "correction_burden": "TBD",
        }
    return {
        "fictional": True, "schema": VERSION, "pair_ready": True,
        "errors": [], "kind_counts": legacy["kind_counts"],
        "source_signature_overlap_is_semantic_agreement": False,
        "semantic_agreement": "TBD", "human_independence": "TBD",
        "adjudicated_gold": "TBD", "correction_burden": "TBD",
    }


def check_files(case_path: str, archive_path: str,
                first_path: str, second_path: str) -> tuple[int, dict]:
    try:
        case, case_sha = _bounded_load(case_path)
        archive, archive_sha = _bounded_load(archive_path)
        first, _ = _bounded_load(first_path)
        second, _ = _bounded_load(second_path)
        report = compare_semantic_pair(
            case, archive, first, second, case_sha, archive_sha)
    except (OSError, UnicodeError, ValueError, OverflowError, TypeError,
            KeyError, AttributeError):
        report = {
            "fictional": True, "schema": VERSION, "pair_ready": False,
            "errors": ["input:invalid_or_unreadable"],
            "semantic_agreement": "TBD", "human_independence": "TBD",
            "correction_burden": "TBD",
        }
    return (0 if report["pair_ready"] else 1), report


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 5 or args[0] != "check":
        raise SystemExit(
            "usage: reviewer_pair_semantic_gate_v03.py check CASE ARCHIVE PRIVATE_A PRIVATE_B")
    code, report = check_files(*args[1:])
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
