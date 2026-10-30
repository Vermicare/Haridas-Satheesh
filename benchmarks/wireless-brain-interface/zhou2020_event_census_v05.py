#!/usr/bin/env python3
"""Label-uninterpreted pinned Zhou2020 event TSV row census, not EEG validation.

Counts structural TSV rows, never extracts trial_type/value into output. Earlier
human preview of three event files means this research is not fully label-blind.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request
import zhou2020_tree_inventory_v03 as inventory
import zhou2020_event_row_sample_v04 as sample

SCHEMA = "ZHOU2020_EVENT_ROW_CENSUS_V05"
EXPECTED_FILES = 833
MAX_WORKERS = 8
BLOB = re.compile(r"[0-9a-f]{40}\Z")


def extract_events(root: dict, trees: dict) -> list[tuple[str, str, int, int]]:
    """Require v0.3 structural pairing audit before enumerating event blob SHAs."""
    structure = inventory.audit(root, trees)
    if structure["observed_event_metadata_files"] != EXPECTED_FILES or structure["metadata_pairing"] != "PASS":
        raise ValueError("unexpected_event_inventory")
    result = []
    for subject in range(1, 21):
        for entry in trees[subject]["tree"]:
            path = entry.get("path", "")
            if entry.get("type") != "blob" or not path.endswith("_events.tsv"):
                continue
            match = inventory.RECORDING.fullmatch(path)
            if not match or match.group(5) != "events":
                raise ValueError("unexpected_event_path")
            session, embedded_subject, embedded_session, run, _ = match.groups()
            if int(embedded_subject) != subject or session != embedded_session:
                raise ValueError("event_path_identity_mismatch")
            sha = entry.get("sha", "")
            if not isinstance(sha, str) or not BLOB.fullmatch(sha):
                raise ValueError("invalid_event_blob_sha")
            size = entry.get("size")
            if not isinstance(size, int) or size < 1 or size > sample.MAX_BYTES:
                raise ValueError("invalid_event_blob_size")
            result.append((f"sub-{subject}/{path}", sha, subject, int(session)))
    if len(result) != EXPECTED_FILES or len({x[0] for x in result}) != EXPECTED_FILES:
        raise ValueError("missing_or_duplicate_event_paths")
    return sorted(result)


def fetch_public_blob(path: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{sample.REPO}/{sample.REF}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "wbi-structural-census-v05"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=35) as response:
                data = response.read(sample.MAX_BYTES + 1)
            if len(data) > sample.MAX_BYTES:
                raise ValueError("oversized_public_tsv")
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            transient = isinstance(exc, (urllib.error.URLError, TimeoutError)) or (
                isinstance(exc, urllib.error.HTTPError) and exc.code in (429, 500, 502, 503, 504))
            if not transient or attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise RuntimeError("unreachable")


def verify_one(entry: tuple[str, str, int, int], fetch=fetch_public_blob) -> dict:
    path, sha, subject, session = entry
    raw = fetch(path)
    if sample.git_blob_sha1(raw) != sha:
        raise ValueError("pinned_git_blob_mismatch")
    rows = sample.count_event_rows(raw)
    return {"path": path, "git_blob_sha1": sha, "subject": subject,
            "session": session, "event_rows": rows, "byte_count": len(raw)}


def census(entries: list, fetch=fetch_public_blob, workers=6) -> dict:
    if not 1 <= workers <= MAX_WORKERS:
        raise ValueError("invalid_worker_limit")
    if len(entries) != EXPECTED_FILES or len({x[0] for x in entries}) != EXPECTED_FILES:
        raise ValueError("incomplete_or_duplicate_census")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        observed = list(pool.map(lambda entry: verify_one(entry, fetch), entries))
    by_subject = defaultdict(lambda: {"files": 0, "event_rows": 0})
    by_session = defaultdict(lambda: {"files": 0, "event_rows": 0})
    for item in observed:
        for group, key in ((by_subject, str(item["subject"])),
                           (by_session, f'{item["subject"]}/ses-{item["session"]}')):
            group[key]["files"] += 1
            group[key]["event_rows"] += item["event_rows"]
    total = sum(item["event_rows"] for item in observed)
    return {
        "schema": SCHEMA, "source_repository": sample.REPO,
        "pinned_source_ref": sample.REF, "files": len(observed),
        "total_event_rows": total, "publisher_reported_trial_count": 33534,
        "nominal_trial_count": 33600,
        "row_total_minus_publisher_trial_count": total - 33534,
        "row_total_minus_nominal_trial_count": total - 33600,
        "event_rows_per_file_histogram": dict(sorted(Counter(str(x["event_rows"]) for x in observed).items(), key=lambda kv: int(kv[0]))),
        "by_subject": dict(sorted(by_subject.items(), key=lambda kv: int(kv[0]))),
        "by_subject_session": dict(sorted(by_session.items())),
        "file_provenance": observed,
        "trial_type_or_value_interpreted": False,
        "prior_human_exploratory_label_preview_disclosed": True,
        "original_EEG_recording_bytes_verified": False,
        "source_archive_authenticated": False,
        "maturity_advanced": False,
        "limitations": "Git-pinned corrected event TSV row census only; rows are not necessarily independent trials; original EEG bytes and event semantics unverified; prior exploratory label exposure prevents a fully label-blind claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.workers <= MAX_WORKERS:
        raise ValueError("invalid_worker_limit")
    root = inventory.get_json(inventory.API + inventory.REF)
    subjects = {int(m.group(1)): e["sha"] for e in root.get("tree", [])
                if (m := inventory.SUBJECT.fullmatch(e.get("path", ""))) and e.get("type") == "tree"}
    if set(subjects) != set(range(1, 21)):
        raise ValueError("unexpected_subject_tree_set")
    trees = {s: inventory.get_json(inventory.API + sha + "?recursive=1") for s, sha in sorted(subjects.items())}
    entries = extract_events(root, trees)
    result = census(entries, workers=args.workers)
    args.output.write_bytes((json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(f'PASS: {result["files"]} pinned TSVs; {result["total_event_rows"]} structural event rows; no labels interpreted', file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError, TimeoutError) as exc:
        print(f"FAIL CLOSED: {type(exc).__name__}", file=sys.stderr)
        sys.exit(1)
