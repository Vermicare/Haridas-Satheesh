#!/usr/bin/env python3
"""Additive fictional CORTEX archive-citation integrity gate.

A structural provenance check only. It does not prove that any cited text
supports a decision, that a reviewer is independent, or that a historical
record is authentic. Existing v0.1 intake and hashes remain unchanged.
"""
from __future__ import annotations

import json
import sys


def validate_archive_citations(archive: object, submission: object) -> list[str]:
    """Require an exact archived source record for every claimed supersession.

    A predecessor ID names a *decision*, whereas archive_sources names the
    specific archived *record* documenting that decision. This distinction
    prevents a valid predecessor identifier alone from masquerading as a
    complete evidence chain. Source semantic relevance is not established.
    """
    if not isinstance(archive, dict) or not isinstance(archive.get("records"), list):
        return ["archive_citation:invalid_archive"]
    if not isinstance(submission, dict) or not isinstance(submission.get("objects"), list):
        return ["archive_citation:invalid_submission"]

    records = archive["records"]
    by_ref: dict[str, str] = {}
    issues: list[str] = []
    for row in records:
        if not isinstance(row, dict):
            return ["archive_citation:invalid_archive"]
        ref, decision_id = row.get("record_ref"), row.get("decision_id")
        if not isinstance(ref, str) or not ref.strip() or not isinstance(decision_id, str) or not decision_id.strip():
            return ["archive_citation:invalid_archive"]
        if ref in by_ref:
            return ["archive_citation:duplicate_archive_record_ref"]
        by_ref[ref] = decision_id

    for idx, obj in enumerate(submission["objects"]):
        prefix = f"object[{idx}]:"
        if not isinstance(obj, dict):
            issues.append(prefix + "invalid_object")
            continue
        citations = obj.get("archive_sources", [])
        if not isinstance(citations, list) or any(
            not isinstance(c, str) or not c.strip() for c in citations
        ):
            issues.append(prefix + "invalid_archive_sources")
            continue
        if len(citations) != len(set(citations)):
            issues.append(prefix + "duplicate_archive_source")
        if any(c not in by_ref for c in citations):
            issues.append(prefix + "unknown_archive_source")
        predecessor = obj.get("supersedes") if obj.get("kind") == "decisions" else None
        if predecessor is not None:
            if not isinstance(predecessor, str) or not predecessor.strip():
                issues.append(prefix + "invalid_predecessor")
            elif not any(by_ref.get(ref) == predecessor for ref in citations):
                issues.append(prefix + "missing_matching_predecessor_archive_source")
    return sorted(set(issues))


def check_files(case_path: str, archive_path: str, submission_path: str) -> tuple[int, dict]:
    """Use the existing strict byte-hashed v0.1 intake; never echo private data."""
    from blind_review_preflight import _load, validate_submission
    try:
        case, case_sha = _load(case_path)
        archive, archive_sha = _load(archive_path)
        submission, _ = _load(submission_path)
    except (OSError, UnicodeError, ValueError, OverflowError):
        return 1, {"fictional": True, "submission_valid": False,
                   "errors": ["input:invalid_json_or_read"], "scores": "TBD"}
    issues = sorted(set(validate_submission(case, archive, submission, case_sha, archive_sha)
                        + validate_archive_citations(archive, submission)))
    return (1 if issues else 0), {
        "fictional": True, "submission_valid": not issues,
        "errors": issues, "scores": "TBD", "external_review": "TBD"
    }


def demo() -> str:
    """Reproducible 30–60 second fictional negative-control demonstration."""
    archive = {"records": [{"record_ref": "SYN-ARC-11", "decision_id": "H-11"},
                           {"record_ref": "SYN-ARC-12", "decision_id": "H-12"}]}
    old = {"objects": [{"kind": "decisions", "source": ["b07"],
                        "supersedes": "H-12"}]}
    corrected = {"objects": [{"kind": "decisions", "source": ["b07"],
                              "supersedes": "H-12",
                              "archive_sources": ["SYN-ARC-12"]}]}
    report = {"fictional": True, "old_missing_citation_issues":
              validate_archive_citations(archive, old),
              "corrected_citation_issues": validate_archive_citations(archive, corrected),
              "real_reviewers": 0, "semantic_validity": "TBD"}
    return json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["demo"]:
        print(demo(), end="")
        return 0
    if len(args) != 4 or args[0] != "check":
        raise SystemExit("usage: archive_citation_gate_v04.py check CASE ARCHIVE PRIVATE_SUBMISSION")
    status, report = check_files(*args[1:])
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
