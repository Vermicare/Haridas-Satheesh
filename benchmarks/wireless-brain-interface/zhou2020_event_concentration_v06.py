"""Read-only v0.6 concentration audit of the frozen public Zhou2020 v0.5 event census.

Only structural metadata is read; no EEG signal or event-type labels.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

PINNED_JSON_SHA256 = "b891a3edfd8b1c535bc50032f7d46717de4f45d0eddbfd500f06430e757ec6b1"
PINNED_SOURCE_REF = "a291ed8a2afab3f93b85a540134dceb98092fcaf"
EXPECTED_FILES = 833
EXPECTED_ROWS = 33534
NOMINAL_ROWS_PER_FILE = 40


def analyze(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema") != "ZHOU2020_EVENT_ROW_CENSUS_V05":
        raise ValueError("unexpected_census_schema")
    if data.get("pinned_source_ref") != PINNED_SOURCE_REF:
        raise ValueError("source_ref_mismatch")
    records = data.get("file_provenance")
    if not isinstance(records, list) or len(records) != EXPECTED_FILES or data.get("files") != EXPECTED_FILES:
        raise ValueError("file_count_mismatch")
    paths = set()
    by_subject = defaultdict(lambda: {"files": 0, "event_rows": 0, "non40_files": 0, "delta_from_40_per_file": 0})
    by_session = defaultdict(lambda: {"files": 0, "event_rows": 0, "non40_files": 0, "delta_from_40_per_file": 0})
    by_subject_session = defaultdict(lambda: {"files": 0, "event_rows": 0, "non40_files": 0, "delta_from_40_per_file": 0})
    hist = Counter()
    for rec in records:
        if not isinstance(rec, dict):
            raise ValueError("invalid_record")
        s, ses, rows, path, blob = (rec.get(k) for k in ("subject", "session", "event_rows", "path", "git_blob_sha1"))
        if type(s) is not int or not 1 <= s <= 20 or type(ses) is not int or not 0 <= ses <= 6 or type(rows) is not int or rows < 1:
            raise ValueError("invalid_subject_session_or_rows")
        if not isinstance(path, str) or not path.startswith(f"sub-{s}/ses-{ses}/eeg/") or path in paths:
            raise ValueError("duplicate_or_invalid_path")
        if not isinstance(blob, str) or len(blob) != 40 or any(c not in "0123456789abcdef" for c in blob):
            raise ValueError("invalid_git_blob")
        paths.add(path)
        hist[rows] += 1
        for bucket in (by_subject[str(s)], by_session[f"ses-{ses}"], by_subject_session[f"sub-{s}/ses-{ses}"]):
            bucket["files"] += 1
            bucket["event_rows"] += rows
            bucket["non40_files"] += int(rows != NOMINAL_ROWS_PER_FILE)
            bucket["delta_from_40_per_file"] += rows - NOMINAL_ROWS_PER_FILE
    total = sum(r["event_rows"] for r in by_subject.values())
    if total != EXPECTED_ROWS or data.get("total_event_rows") != EXPECTED_ROWS:
        raise ValueError("row_total_mismatch")
    if {str(k): v for k, v in sorted(hist.items())} != data.get("event_rows_per_file_histogram"):
        raise ValueError("histogram_mismatch")
    for s, v in by_subject.items():
        if {k: v[k] for k in ("files", "event_rows")} != data.get("by_subject", {}).get(s):
            raise ValueError("subject_rollup_mismatch")
    for key, v in by_subject_session.items():
        subject, session = key.split("/")
        original_key = subject.removeprefix("sub-") + "/" + session
        if {k: v[k] for k in ("files", "event_rows")} != data.get("by_subject_session", {}).get(original_key):
            raise ValueError("session_rollup_mismatch")
    if len(by_subject) != 20 or len(by_subject_session) != 139:
        raise ValueError("subject_session_denominator_mismatch")
    return {
        "schema": "ZHOU2020_EVENT_CONCENTRATION_V06",
        "source_census_json_sha256": PINNED_JSON_SHA256,
        "source_upstream_git_ref": PINNED_SOURCE_REF,
        "baseline_rows_per_file_assumption": NOMINAL_ROWS_PER_FILE,
        "files": EXPECTED_FILES,
        "structural_event_rows": total,
        "non40_files": sum(x["non40_files"] for x in by_subject.values()),
        "subjects_with_non40_files": sum(v["non40_files"] > 0 for v in by_subject.values()),
        "session0_non40_files": by_session["ses-0"]["non40_files"],
        "session0_delta_from_40_per_file": by_session["ses-0"]["delta_from_40_per_file"],
        "total_delta_from_40_per_file": total - NOMINAL_ROWS_PER_FILE * EXPECTED_FILES,
        "by_subject": dict(sorted(by_subject.items(), key=lambda kv: int(kv[0]))),
        "by_session": dict(sorted(by_session.items())),
        "by_subject_session": dict(sorted(by_subject_session.items())),
        "limitations": ["corrected public event TSV row counts only", "no original NPZ byte verification", "no EEG decoding", "no trial-type inspection", "not an independent trial authenticity check"],
        "maturity_advanced": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("census_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.census_json.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINNED_JSON_SHA256:
        raise SystemExit("FAIL: census JSON SHA-256 does not match frozen v0.5")
    payload = json.dumps(analyze(json.loads(raw)), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_bytes(payload.encode("utf-8"))
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
