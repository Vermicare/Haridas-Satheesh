#!/usr/bin/env python3
"""Prospective, fictional-only CORTEX v0.2 annotation shape gate.

This gate checks that an annotation is structurally capable of later semantic
adjudication. It does NOT determine whether any claim is true, whether a
reviewer is independent, or whether reported time was actually measured.
Completed reviewer submissions must remain private and outside Git checkout.
"""
from __future__ import annotations

from datetime import date
import json
import sys

VERSION = "cortex-fictional-annotation-v0.2"
KINDS = {"decisions", "actions", "risks", "dependencies", "conditional_followups"}
COMMON = {"kind", "record_id", "source", "archive_sources"}
FIELDS = {
    "decisions": {"statement", "status", "supersedes"},
    "actions": {"action", "owner", "due"},
    "risks": {"statement", "status"},
    "dependencies": {"statement"},
    "conditional_followups": {"condition", "action"},
}
REQUIRED = {
    "decisions": {"statement", "status"},
    "actions": {"action", "owner", "due"},
    "risks": {"statement", "status"},
    "dependencies": {"statement"},
    "conditional_followups": {"condition", "action"},
}
TEXT_FIELDS = {"statement", "action", "condition"}
MAX_TEXT_LENGTH = 500


def _text(value: object, max_length: int = MAX_TEXT_LENGTH) -> bool:
    return (isinstance(value, str) and 0 < len(value.strip()) <= max_length
            and not any(ord(ch) < 32 and ch not in "\t\n" for ch in value))


def _date_or_unknown(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or len(value) != 10:
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def validate_semantic_annotation(submission: object) -> list[str]:
    """Aggregate error *codes only*; never return or print annotation text."""
    if not isinstance(submission, dict):
        return ["v02:invalid_submission"]
    errors: list[str] = []
    if submission.get("annotation_schema_version") != VERSION:
        errors.append("v02:wrong_schema_version")
    if submission.get("method") != "manual_structured_notes":
        errors.append("v02:manual_method_required")
    if submission.get("reviewer_code") == "R00":
        errors.append("v02:template_reviewer_code")
    objects = submission.get("objects")
    if not isinstance(objects, list):
        return sorted(set(errors + ["v02:invalid_objects"]))
    for index, obj in enumerate(objects):
        label = f"v02:object[{index}]"
        if not isinstance(obj, dict):
            errors.append(label + ":invalid_object")
            continue
        kind = obj.get("kind")
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(label + ":unknown_kind")
            continue
        if set(obj) - (COMMON | FIELDS[kind]):
            errors.append(label + ":unsupported_fields")
        if REQUIRED[kind] - set(obj):
            errors.append(label + ":missing_semantic_fields")
        for field in TEXT_FIELDS & FIELDS[kind]:
            if field in obj and not _text(obj[field]):
                errors.append(label + ":invalid_" + field)
        if kind == "actions":
            if "owner" in obj and obj["owner"] is not None and not _text(obj["owner"], 120):
                errors.append(label + ":invalid_owner")
            if "due" in obj and not _date_or_unknown(obj["due"]):
                errors.append(label + ":invalid_due")
        if kind in {"decisions", "risks"} and "status" in obj:
            if obj["status"] not in (None, "active", "superseded", "open", "closed"):
                errors.append(label + ":invalid_status")
        if kind == "decisions" and "supersedes" in obj:
            if obj["supersedes"] is not None and not _text(obj["supersedes"], 120):
                errors.append(label + ":invalid_supersedes")
    return sorted(set(errors))


def check_files(case_path: str, archive_path: str, submission_path: str) -> tuple[int, dict]:
    """Run existing byte-hash, source and archive gates before the new shape gate."""
    from blind_review_preflight import _load, validate_submission
    from archive_citation_gate_v04 import validate_archive_citations
    from reviewer_pair_preflight_v01 import EXPECTED_CASE_SHA256, EXPECTED_ARCHIVE_SHA256, MAX_INPUT_BYTES
    from pathlib import Path

    try:
        paths = [case_path, archive_path, submission_path]
        if any(Path(path).stat().st_size > MAX_INPUT_BYTES for path in paths):
            raise ValueError("oversized input")
        case, case_sha = _load(case_path)
        archive, archive_sha = _load(archive_path)
        submission, _ = _load(submission_path)
        errors = validate_submission(case, archive, submission, case_sha, archive_sha)
        errors.extend(validate_archive_citations(archive, submission))
        errors.extend(validate_semantic_annotation(submission))
        if case_sha != EXPECTED_CASE_SHA256 or archive_sha != EXPECTED_ARCHIVE_SHA256:
            errors.append("v02:unrecognized_frozen_packet")
    except (OSError, UnicodeError, ValueError, TypeError, OverflowError, KeyError):
        errors = ["v02:unreadable_or_invalid_input"]
    errors = sorted(set(errors))
    return (1 if errors else 0), {"fictional": True, "schema": VERSION,
                                 "structurally_ready": not errors, "errors": errors,
                                 "semantic_accuracy": "TBD", "human_independence": "TBD",
                                 "correction_burden": "TBD"}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 4 or args[0] != "check":
        raise SystemExit("usage: semantic_annotation_contract_v02.py check CASE ARCHIVE PRIVATE_SUBMISSION")
    code, result = check_files(*args[1:])
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
