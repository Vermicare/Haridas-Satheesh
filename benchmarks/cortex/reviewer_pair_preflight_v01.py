#!/usr/bin/env python3
"""Private two-reviewer *structural* preflight for a frozen fictional CORTEX packet.

Never writes reviewer submissions, identity codes, source text, or object IDs.
The output is only aggregate, non-semantic source-signature overlap. This does
not establish independent reviewers, label accuracy, consensus, or real timing.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

MAX_INPUT_BYTES = 1_048_576
EXPECTED_CASE_SHA256 = "f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d"
EXPECTED_ARCHIVE_SHA256 = "897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046"
KINDS = ("decisions", "actions", "risks", "dependencies", "conditional_followups")


def _signatures(submission: dict) -> Counter:
    """Multiset prevents two same-source objects being silently collapsed."""
    return Counter((obj["kind"], tuple(sorted(obj["source"])),
                    obj.get("supersedes") if obj["kind"] == "decisions" else None)
                   for obj in submission["objects"])


def compare_pair(case: object, archive: object, first: object, second: object,
                 case_sha: str, archive_sha: str) -> dict:
    """Validate both reviewers against existing v0.1 + v0.4 gates first."""
    from blind_review_preflight import validate_submission
    from archive_citation_gate_v04 import validate_archive_citations

    errors: list[str] = []
    if (case_sha != EXPECTED_CASE_SHA256 or archive_sha != EXPECTED_ARCHIVE_SHA256):
        errors.append("pair:unrecognized_frozen_packet")
    for index, submission in enumerate((first, second)):
        problems = validate_submission(case, archive, submission, case_sha, archive_sha)
        problems += validate_archive_citations(archive, submission)
        if problems:
            errors.append(f"reviewer[{index}]:invalid_submission")
        if isinstance(submission, dict):
            if submission.get("method") != "manual_structured_notes":
                errors.append(f"reviewer[{index}]:requires_manual_notes")
            elapsed = submission.get("review_seconds")
            if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not (0 < elapsed < float("inf")):
                errors.append(f"reviewer[{index}]:invalid_review_time")
            if submission.get("correction_seconds") != 0 or isinstance(submission.get("correction_seconds"), bool):
                errors.append(f"reviewer[{index}]:unexpected_correction_time")
    if isinstance(first, dict) and isinstance(second, dict) and first.get("reviewer_code") == second.get("reviewer_code"):
        errors.append("pair:duplicate_pseudonym")
    if errors:
        return {"fictional": True, "pair_valid": False, "errors": sorted(set(errors)),
                "human_independence": "TBD", "semantic_agreement": "TBD", "scores": "TBD"}

    left, right = _signatures(first), _signatures(second)
    matched = left & right
    kinds = {kind: {"first_count": sum(n for (k, _, _), n in left.items() if k == kind),
                    "second_count": sum(n for (k, _, _), n in right.items() if k == kind),
                    "shared_source_signature_count": sum(n for (k, _, _), n in matched.items() if k == kind)}
             for kind in KINDS}
    return {"fictional": True, "pair_valid": True, "errors": [],
            "kind_counts": kinds,
            "source_signature_overlap_is_semantic_agreement": False,
            "human_independence": "TBD", "semantic_agreement": "TBD",
            "adjudicated_gold": "TBD", "scores": "TBD"}


def _bounded_load(path: str):
    from blind_review_preflight import _load
    if Path(path).stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("input too large")
    return _load(path)


def check_files(case_path: str, archive_path: str, first_path: str, second_path: str) -> tuple[int, dict]:
    try:
        case, case_sha = _bounded_load(case_path)
        archive, archive_sha = _bounded_load(archive_path)
        first, _ = _bounded_load(first_path)
        second, _ = _bounded_load(second_path)
        result = compare_pair(case, archive, first, second, case_sha, archive_sha)
    except (OSError, UnicodeError, ValueError, OverflowError, TypeError, KeyError):
        result = {"fictional": True, "pair_valid": False,
                  "errors": ["input:invalid_or_unreadable"], "scores": "TBD"}
    return (0 if result["pair_valid"] else 1), result


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 5 or args[0] != "check":
        raise SystemExit("usage: reviewer_pair_preflight_v01.py check CASE ARCHIVE PRIVATE_A PRIVATE_B")
    code, report = check_files(*args[1:])
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
