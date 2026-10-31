#!/usr/bin/env python3
"""Package only pinned fictional CORTEX sources for private first-pass review.

No claim of reviewer blinding or independence. No reviewer data is processed.
"""
from __future__ import annotations
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED

from blind_review_preflight import (_unique_members, _reject_non_json_constant,
                                    _finite_float, validate_packet)

CASE = "blind_case_20261024.json"
ARCHIVE = "blind_archive_20261024.json"
PINS = {
    CASE: "f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d",
    ARCHIVE: "897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046",
}
INSTRUCTIONS = (
    "CORTEX — FICTIONAL SOURCE-ONLY FIRST-PASS REVIEW\n"
    "This is a simulated governance case, not an employer or client record.\n"
    "Read only the case and archive supplied here before your first-pass annotation.\n"
    "Do not consult the public repository, its example outputs, tests or interpretations\n"
    "until after your first-pass annotation is locked. Declare prior exposure privately\n"
    "to the coordinator; this package cannot establish that you were blinded.\n"
    "Annotate decisions, actions, risks, dependencies and conditional follow-ups.\n"
    "Cite exact utterance IDs and archive record references. Mark unknown fields\n"
    "unknown; do not infer an approval or assignment from a suggestion.\n"
    "Record actual review time privately. Do not publish completed annotations,\n"
    "reviewer identities, contact details, or private timing records to GitHub.\n"
    "There are no ground-truth labels, expected interpretations or scores here.\n"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(data: bytes):
    return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_members,
                      parse_constant=_reject_non_json_constant,
                      parse_float=_finite_float)


def build_packet(case_bytes: bytes, archive_bytes: bytes):
    sources = {CASE: case_bytes, ARCHIVE: archive_bytes}
    if any(sha256(raw) != PINS[name] for name, raw in sources.items()):
        raise ValueError("frozen source hash mismatch; never silently normalize or replace inputs")
    errors = validate_packet(strict_json(case_bytes), strict_json(archive_bytes))
    if errors:
        raise ValueError("fictional packet failed structural validation")
    members = [(CASE, case_bytes), (ARCHIVE, archive_bytes),
               ("REVIEWER_INSTRUCTIONS.txt", INSTRUCTIONS.encode("utf-8"))]
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_STORED) as z:
        for name, data in members:
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    bundle = buffer.getvalue()
    manifest = {
        "status": "FICTIONAL_SOURCE_ONLY_PRE_REVIEW_NOT_BLINDING_PROOF",
        "bundle_sha256": sha256(bundle),
        "members": {name: sha256(data) for name, data in members},
        "reviewers": "TBD", "semantic_accuracy": "TBD",
        "correction_time": "TBD", "prior_exposure": "TBD",
    }
    return bundle, manifest


def write_packet(output: Path, repo_root: Path, case_bytes: bytes, archive_bytes: bytes):
    target = output.expanduser().resolve(strict=False)
    if target.is_relative_to(repo_root.resolve()):
        raise ValueError("private reviewer bundle output must be outside the public repository")
    bundle, manifest = build_packet(case_bytes, archive_bytes)
    with target.open("xb") as f:
        f.write(bundle)
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True,
                   help="new private ZIP path OUTSIDE the repository; existing files are not overwritten")
    args = p.parse_args(argv)
    here = Path(__file__).resolve().parent
    try:
        manifest = write_packet(args.output, here.parents[1],
                                (here / CASE).read_bytes(), (here / ARCHIVE).read_bytes())
    except (OSError, ValueError, UnicodeError):
        p.exit(1, "FAIL CLOSED: source identity, structure or private output constraint failed\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
