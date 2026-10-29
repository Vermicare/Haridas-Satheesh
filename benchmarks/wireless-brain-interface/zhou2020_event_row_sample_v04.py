#!/usr/bin/env python3
"""Zhou2020 pinned three-file EVENT ROW COUNT diagnostic; no label interpretation.

Only counts rows and tab delimiters in three public TSV blobs. This is an
exploratory structural check, NOT full-cohort event reconciliation, label-blind
preregistration, signal validation, or EEG performance evidence.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

REF = "a291ed8a2afab3f93b85a540134dceb98092fcaf"
REPO = "nemarDatasets/nm000237"
HEADER = b"onset\tduration\ttrial_type\tvalue\tsample"
MAX_BYTES = 131072
PINS = (
    ("sub-1/ses-0/eeg/sub-1_ses-0_task-imagery_run-0_events.tsv",
     "0997cba4376368265a05a10f6958218dee6fb0f5", 40),
    ("sub-20/ses-0/eeg/sub-20_ses-0_task-imagery_run-0_events.tsv",
     "de1390ba9e0a19c678dffe638dbb32e708029be0", 80),
    ("sub-20/ses-5/eeg/sub-20_ses-5_task-imagery_run-7_events.tsv",
     "e184dfdf8454a1fde7da15e369fe459ed3e25de9", 40),
)


def git_blob_sha1(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def count_event_rows(raw):
    """Count structurally valid rows WITHOUT parsing trial_type/value contents."""
    if not raw or len(raw) > MAX_BYTES or b"\0" in raw:
        raise ValueError("empty, oversized or NUL-containing TSV")
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    if b"\r" in raw.replace(b"\r\n", b""):
        raise ValueError("unsupported bare CR")
    lines = raw.replace(b"\r\n", b"\n").split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    if not lines or lines[0] != HEADER:
        raise ValueError("unexpected TSV header")
    if not lines[1:] or any(not line or line.count(b"\t") != 4 for line in lines[1:]):
        raise ValueError("blank or malformed event row")
    return len(lines) - 1


def verify_bytes(raw, expected_sha, expected_rows):
    sha = git_blob_sha1(raw)
    if sha != expected_sha:
        raise ValueError(f"Git blob mismatch: {sha}")
    rows = count_event_rows(raw)
    if rows != expected_rows:
        raise ValueError(f"event-row count mismatch: {rows} != {expected_rows}")
    return {"git_blob_sha1": sha, "event_rows": rows, "byte_count": len(raw)}


def fetch_raw(path):
    url = f"https://raw.githubusercontent.com/{REPO}/{REF}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "wbi-event-row-sample-v04"})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("upstream TSV exceeded bounded read")
    return raw


def audit(fetch=fetch_raw):
    if len(PINS) != len({path for path, _, _ in PINS}):
        raise ValueError("duplicate sample path")
    observed = []
    for path, sha, expected_rows in PINS:
        result = verify_bytes(fetch(path), sha, expected_rows)
        observed.append({"path": path, **result})
    return {
        "schema": "ZHOU2020_EVENT_ROW_SAMPLE_V04",
        "upstream_ref": REF,
        "upstream_repository": REPO,
        "selection": "three prespecified illustrative paths, not a random sample",
        "observations": observed,
        "event_row_count_sum_for_three_files": sum(x["event_rows"] for x in observed),
        "full_cohort_event_row_total": "TBD",
        "event_label_values_parsed_by_this_verifier": False,
        "prior_exploratory_human_view_of_three_TSV_previews": True,
        "original_npz_bytes_verified": False,
        "maturity_advanced": False,
        "limitations": "Structural event-row counts only. A prior exploratory inspection exposed event TSV previews; do not call this label-blind preregistration. No decoding, drift-gate benefit or full event count established.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit()
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.output is None:
        sys.stdout.buffer.write(payload)
    else:
        args.output.write_bytes(payload)
    print("PASS: 3 pinned public event TSV blobs; row counts 40, 80, 40; no labels parsed by verifier", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TimeoutError) as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        sys.exit(1)
