#!/usr/bin/env python3
"""Frozen fictional CORTEX provenance projection; NOT a general PROV validator.

Only emits a small, explicitly reviewed set of edges from a pinned fictional
case/archive. Replacing a historical decision is NOT automatically a PROV
revision or a proof that the earlier decision was factually correct.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

VERSION = "cortex-prov-boundary-v0.5"
CASE_SHA256 = "f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d"
ARCHIVE_SHA256 = "897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046"
MAX_BYTES = 100_000

# Static mapping for the *frozen* fictional source. Do not generalize it to
# arbitrary meetings or infer edges from similar-looking words.
TRIPLES = (
    ("ex:source-b03", "a", "prov:Entity"),
    ("ex:source-b07", "a", "prov:Entity"),
    ("ex:archive-H11", "a", "prov:Entity"),
    ("ex:archive-H12", "a", "prov:Entity"),
    ("ex:hold-H11", "a", "prov:Entity"),
    ("ex:hold-H11", "prov:wasDerivedFrom", "ex:archive-H11"),
    ("ex:checklist-H12", "a", "prov:Entity"),
    ("ex:checklist-H12", "prov:wasDerivedFrom", "ex:archive-H12"),
    ("ex:checklist-B", "a", "prov:Entity"),
    ("ex:checklist-B", "prov:wasDerivedFrom", "ex:source-b07"),
    ("ex:checklist-B", "cortex:supersedes", "ex:checklist-H12"),
    ("ex:hold-clarification", "a", "prov:Entity"),
    ("ex:hold-clarification", "prov:wasDerivedFrom", "ex:source-b03"),
    ("ex:hold-clarification", "cortex:clarifies", "ex:hold-H11"),
)

# These are intentionally absent: a new decision is not necessarily a content
# revision of an old one; archived text is not authenticated first-hand source;
# and there is no explicit event proving invalidation of the public hold.
FORBIDDEN_PREDICATES = frozenset({
    "prov:wasRevisionOf", "prov:hadPrimarySource", "prov:wasInvalidatedBy"
})


def _read_pinned(path: str, expected: str) -> dict:
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("oversized_input")
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("frozen_hash_mismatch")
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("invalid_document_shape")
    return value


def validate_structure(case: dict, archive: dict) -> None:
    """Narrow structural checks; hashes, not keyword rules, pin the semantics."""
    if case.get("synthetic") is not True or archive.get("synthetic") is not True:
        raise ValueError("not_explicitly_fictional")
    if case.get("provenance") != "AUTHOR_CREATED_FICTIONAL" or archive.get("provenance") != "AUTHOR_CREATED_FICTIONAL":
        raise ValueError("unexpected_provenance")
    if case.get("case_id") != "CORTEX-BLIND-20261024-A" or archive.get("archive_id") != "CORTEX-BLIND-ARCHIVE-20261024-A":
        raise ValueError("wrong_fixture_identity")
    utterances = case.get("meeting", {}).get("utterances")
    records = archive.get("records")
    if not isinstance(utterances, list) or not isinstance(records, list):
        raise ValueError("missing_sources")
    utterance_ids = [u.get("id") for u in utterances if isinstance(u, dict)]
    record_ids = [r.get("decision_id") for r in records if isinstance(r, dict)]
    if len(utterance_ids) != len(utterances) or any(not isinstance(x, str) for x in utterance_ids) or len(set(utterance_ids)) != len(utterance_ids):
        raise ValueError("duplicate_or_invalid_utterance")
    if len(record_ids) != len(records) or any(not isinstance(x, str) for x in record_ids) or len(set(record_ids)) != len(record_ids):
        raise ValueError("duplicate_or_invalid_archive_record")
    if not {"b03", "b07"}.issubset(utterance_ids) or not {"H-11", "H-12"}.issubset(record_ids):
        raise ValueError("unresolved_fictional_source")
    if any(predicate in FORBIDDEN_PREDICATES for _, predicate, _ in TRIPLES):
        raise ValueError("unsupported_prov_relation")
    if ("ex:checklist-B", "cortex:supersedes", "ex:checklist-H12") not in TRIPLES:
        raise ValueError("missing_domain_supersession")
    if any(s == "ex:hold-H11" and p == "cortex:supersedes" for s, p, _ in TRIPLES):
        raise ValueError("false_hold_supersession")


def render_turtle(case: dict, archive: dict) -> str:
    validate_structure(case, archive)
    header = (
        "# AUTHOR-CREATED FICTIONAL provenance example; NOT a general RDF/OWL validation.\n"
        "# Archive existence is not authenticity; replacement is not necessarily revision.\n"
        "@prefix prov: <http://www.w3.org/ns/prov#> .\n"
        "@prefix cortex: <https://example.org/cortex-fictional/vocab#> .\n"
        "@prefix ex: <https://example.org/cortex-fictional/20261024/> .\n\n"
    )
    return header + "".join(f"{s} {p} {o} .\n" for s, p, o in TRIPLES)


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 3 or args[0] != "export":
        print("usage: cortex_prov_boundary_v05.py export FROZEN_CASE FROZEN_ARCHIVE", file=sys.stderr)
        return 2
    try:
        case = _read_pinned(args[1], CASE_SHA256)
        archive = _read_pinned(args[2], ARCHIVE_SHA256)
        print(render_turtle(case, archive), end="")
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, AttributeError, KeyError) as exc:
        # Do not leak user-supplied paths, identifiers or source text.
        code = str(exc) if isinstance(exc, ValueError) and str(exc) in {
            "oversized_input", "frozen_hash_mismatch", "invalid_document_shape",
            "not_explicitly_fictional", "unexpected_provenance", "wrong_fixture_identity",
            "missing_sources", "duplicate_or_invalid_utterance", "duplicate_or_invalid_archive_record",
            "unresolved_fictional_source", "unsupported_prov_relation",
            "missing_domain_supersession", "false_hold_supersession"
        } else "invalid_or_unreadable_input"
        print(json.dumps({"schema": VERSION, "valid": False, "error": code}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
