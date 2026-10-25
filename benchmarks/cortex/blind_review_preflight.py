#!/usr/bin/env python3
"""Validate a fictional blinded CORTEX reviewer packet and optional annotations.

No extractor, ground-truth labels, identities or reviewer results are bundled.
Usage:
  python blind_review_preflight.py manifest blind_case_20261024.json blind_archive_20261024.json
  python blind_review_preflight.py check blind_case_20261024.json blind_archive_20261024.json private_submission.json
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

KINDS = {"decisions", "actions", "risks", "dependencies", "conditional_followups"}
PSEUDONYM = re.compile(r"R[0-9]{2}\Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _unique_members(pairs):
    """Fail closed on ambiguous JSON object names (RFC 8259, section 4)."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _finite_float(token):
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("out-of-range JSON number")
    return value


def _reject_non_json_constant(token):
    raise ValueError("non-JSON numeric constant")


def _load(path):
    data = Path(path).read_bytes()
    document = json.loads(
        data.decode("utf-8"),
        object_pairs_hook=_unique_members,
        parse_constant=_reject_non_json_constant,
        parse_float=_finite_float,
    )
    return document, digest(data)


def validate_packet(case, archive):
    errors = []
    for label, obj in (("case", case), ("archive", archive)):
        if not isinstance(obj, dict) or obj.get("synthetic") is not True or obj.get("provenance") != "AUTHOR_CREATED_FICTIONAL":
            errors.append(label + ":not_explicitly_fictional")
    if errors:
        return errors
    meeting = case.get("meeting")
    if not isinstance(meeting, dict):
        meeting = {}
        errors.append("case:missing_meeting")
    utterances = meeting.get("utterances", [])
    records = archive.get("records", [])
    if not isinstance(utterances, list) or not utterances:
        errors.append("case:missing_utterances")
        utterances = []
    if not isinstance(records, list) or not records:
        errors.append("archive:missing_records")
        records = []
    seen_u, seen_a, seen_d = set(), set(), set()
    for u in utterances:
        if not isinstance(u, dict):
            errors.append("case:malformed_utterance"); continue
        uid = u.get("id")
        if not isinstance(uid, str) or not uid.strip() or uid in seen_u:
            errors.append("case:invalid_or_duplicate_utterance_id")
        else:
            seen_u.add(uid)
        if not isinstance(u.get("text"), str) or not u["text"].strip():
            errors.append("case:empty_utterance_text")
    for rec in records:
        if not isinstance(rec, dict):
            errors.append("archive:malformed_record"); continue
        ref, did = rec.get("record_ref"), rec.get("decision_id")
        if not isinstance(ref, str) or not ref.strip() or ref in seen_a:
            errors.append("archive:invalid_or_duplicate_record_ref")
        else:
            seen_a.add(ref)
        if not isinstance(did, str) or not did.strip() or did in seen_d:
            errors.append("archive:invalid_or_duplicate_decision_id")
        else:
            seen_d.add(did)
        if not isinstance(rec.get("text"), str) or not rec["text"].strip():
            errors.append("archive:empty_record_text")
    return sorted(set(errors))


def validate_submission(case, archive, submission, case_sha, archive_sha):
    errors = validate_packet(case, archive)
    if not isinstance(submission, dict):
        return sorted(set(errors + ["submission:not_object"]))
    if submission.get("case_sha256") != case_sha or submission.get("archive_sha256") != archive_sha:
        errors.append("submission:source_hash_mismatch")
    if submission.get("synthetic") is not True:
        errors.append("submission:synthetic_flag_missing")
    if not isinstance(submission.get("reviewer_code"), str) or not PSEUDONYM.fullmatch(submission["reviewer_code"]):
        errors.append("submission:invalid_pseudonym")
    if submission.get("method") not in ("manual_structured_notes", "extractor_correction"):
        errors.append("submission:invalid_method")
    for field in ("review_seconds", "correction_seconds"):
        v = submission.get(field)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v < float("inf"):
            errors.append("submission:invalid_" + field)
    objects = submission.get("objects")
    if not isinstance(objects, list):
        return sorted(set(errors + ["submission:objects_not_list"]))
    # validate_packet reports malformed inputs, but submission checking must
    # still fail closed rather than raise on None, arrays, or unhashable IDs.
    if not isinstance(case, dict) or not isinstance(archive, dict):
        return sorted(set(errors + ["submission:invalid_packet"]))
    meeting = case.get("meeting")
    utterances = meeting.get("utterances") if isinstance(meeting, dict) else None
    records = archive.get("records")
    source_ids = {
        u["id"] for u in (utterances if isinstance(utterances, list) else [])
        if isinstance(u, dict) and isinstance(u.get("id"), str)
    }
    archive_ids = {
        r["decision_id"] for r in (records if isinstance(records, list) else [])
        if isinstance(r, dict) and isinstance(r.get("decision_id"), str)
    }
    record_ids = set()
    for idx, obj in enumerate(objects):
        tag = "object[%d]" % idx
        if not isinstance(obj, dict):
            errors.append(tag + ":malformed"); continue
        kind, rid, sources = obj.get("kind"), obj.get("record_id"), obj.get("source")
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(tag + ":unknown_kind")
        if not isinstance(rid, str) or not rid.strip() or rid in record_ids:
            errors.append(tag + ":invalid_or_duplicate_record_id")
        else:
            record_ids.add(rid)
        if not isinstance(sources, list) or not sources or any(not isinstance(s, str) or s not in source_ids for s in sources) or len(set(map(str, sources))) != len(sources):
            errors.append(tag + ":invalid_source")
        if kind == "decisions" and obj.get("supersedes") is not None:
            predecessor = obj["supersedes"]
            if not isinstance(predecessor, str) or predecessor not in archive_ids:
                errors.append(tag + ":unresolved_archived_predecessor")
    return sorted(set(errors))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) not in (3, 4) or argv[0] not in ("manifest", "check") or (argv[0] == "manifest") != (len(argv) == 3):
        raise SystemExit("usage: blind_review_preflight.py manifest CASE ARCHIVE | check CASE ARCHIVE PRIVATE_SUBMISSION")
    try:
        case, case_sha = _load(argv[1])
        archive, archive_sha = _load(argv[2])
        if argv[0] == "check":
            submission, _ = _load(argv[3])
    except (OSError, UnicodeError, ValueError):
        # Never echo private submission contents, paths or parser diagnostics.
        print(json.dumps({"fictional": True, "errors": ["input:invalid_json_or_read"],
                          "scores": "TBD"}, sort_keys=True, indent=2))
        return 1
    if argv[0] == "manifest":
        errors = validate_packet(case, archive)
        meeting = case.get("meeting") if isinstance(case, dict) else None
        utterances = meeting.get("utterances") if isinstance(meeting, dict) else None
        records = archive.get("records") if isinstance(archive, dict) else None
        result = {"fictional": True, "case_sha256": case_sha, "archive_sha256": archive_sha,
                  "utterance_count": len(utterances) if isinstance(utterances, list) else 0,
                  "archive_record_count": len(records) if isinstance(records, list) else 0,
                  "errors": errors, "reviewer_study": "TBD", "ground_truth": "TBD"}
    else:
        errors = validate_submission(case, archive, submission, case_sha, archive_sha)
        result = {"fictional": True, "submission_valid": not errors, "errors": errors, "scores": "TBD"}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
