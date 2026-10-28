#!/usr/bin/env python3
"""CORTEX v0.4: privacy-minimal exact-disagreement triage for fictional pairs.

Not semantic agreement, adjudication, identity verification or an extractor.
Completed human submissions must remain private. Only counts leave this module.
"""
from __future__ import annotations

from collections import defaultdict
import json
import sys

from reviewer_pair_semantic_gate_v03 import compare_semantic_pair, _bounded_load
from semantic_annotation_contract_v02 import FIELDS

VERSION = "cortex-fictional-exact-disagreement-v0.4"


def _key(obj):
    return (obj["kind"], tuple(sorted(obj["source"])),
            obj.get("supersedes") if obj["kind"] == "decisions" else None)


def _groups(submission):
    groups = defaultdict(list)
    for obj in submission["objects"]:
        groups[_key(obj)].append(obj)
    return groups


def compare_exact_disagreement(case, archive, first, second, case_sha, archive_sha):
    """Count exact differences only after both pre-existing contracts pass."""
    gate = compare_semantic_pair(case, archive, first, second, case_sha, archive_sha)
    report = {
        "fictional": True, "schema": VERSION,
        "pair_ready": gate["pair_ready"], "errors": gate["errors"],
        "semantic_agreement": "TBD", "human_independence": "TBD",
        "adjudicated_gold": "TBD", "correction_burden": "TBD",
        "independent_adjudication_still_required": True,
    }
    if not gate["pair_ready"]:
        report["exact_disagreement_detected"] = "TBD"
        return report
    a, b = _groups(first), _groups(second)
    unique_matches = 0
    exact_matches = 0
    different = 0
    ambiguous = 0
    missing = 0
    mismatches = {field: 0 for field in sorted(set().union(*FIELDS.values()) | {"archive_sources"})}
    for signature in a.keys() | b.keys():
        left, right = a.get(signature, []), b.get(signature, [])
        if not left or not right:
            missing += 1
            continue
        if len(left) != 1 or len(right) != 1:
            ambiguous += 1
            continue  # never arbitrarily pair duplicate-source objects
        unique_matches += 1
        kind = signature[0]
        fields = FIELDS[kind] | {"archive_sources"}
        changed = False
        for field in fields:
            left_value = left[0].get(field)
            right_value = right[0].get(field)
            if field == "archive_sources":
                left_value = tuple(sorted(left_value)) if isinstance(left_value, list) else left_value
                right_value = tuple(sorted(right_value)) if isinstance(right_value, list) else right_value
            if left_value != right_value:
                mismatches[field] += 1
                changed = True
        if changed:
            different += 1
        else:
            exact_matches += 1
    report.update({
        "matched_unique_source_groups": unique_matches,
        "exact_field_match_groups": exact_matches,
        "exact_field_mismatch_groups": different,
        "unmatched_source_groups": missing,
        "ambiguous_duplicate_source_groups": ambiguous,
        "field_mismatch_counts": mismatches,
        "exact_disagreement_detected": bool(different or missing or ambiguous),
        "exact_match_is_semantic_agreement": False,
    })
    return report


def check_files(case_path, archive_path, first_path, second_path):
    try:
        case, case_sha = _bounded_load(case_path)
        archive, archive_sha = _bounded_load(archive_path)
        first, _ = _bounded_load(first_path)
        second, _ = _bounded_load(second_path)
        report = compare_exact_disagreement(case, archive, first, second, case_sha, archive_sha)
    except (OSError, UnicodeError, ValueError, OverflowError, TypeError,
            KeyError, AttributeError):
        report = {"fictional": True, "schema": VERSION, "pair_ready": False,
                  "errors": ["input:invalid_or_unreadable"],
                  "exact_disagreement_detected": "TBD", "semantic_agreement": "TBD",
                  "independent_adjudication_still_required": True}
    return (0 if report["pair_ready"] else 1), report


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 5 or args[0] != "check":
        raise SystemExit("usage: reviewer_pair_exact_disagreement_v04.py check CASE ARCHIVE PRIVATE_A PRIVATE_B")
    code, report = check_files(*args[1:])
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
