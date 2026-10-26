#!/usr/bin/env python3
"""Metadata-only split gate for BNCI2014_001; NOT an EEG decoder or validation.

Input JSON object: {"dataset": "BNCI2014_001", "trials": [
  {"subject": 1, "session": "T", "run": 1, "trial_id": "..."}, ...]}
All 9 subjects, 2 sessions, 6 runs/session, 48 trials/run are required.
Do not include EEG samples, labels, subject identifiers other than public dataset IDs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SUBJECTS = tuple(range(1, 10))
SESSIONS = ("T", "E")
RUNS = tuple(range(1, 7))
TRIALS_PER_RUN = 48
FIELDS = {"subject", "session", "run", "trial_id"}


def _hash_ids(ids):
    return hashlib.sha256(("\n".join(sorted(ids)) + "\n").encode("utf-8")).hexdigest()


def validate(payload):
    if not isinstance(payload, dict) or set(payload) != {"dataset", "trials"}:
        raise ValueError("manifest requires exactly dataset and trials")
    if payload["dataset"] != "BNCI2014_001" or not isinstance(payload["trials"], list):
        raise ValueError("wrong dataset or non-list trials")
    seen = set()
    counts = Counter()
    groups = {}
    for row in payload["trials"]:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("trial fields must be subject, session, run, trial_id only")
        s, sess, run, tid = (row[k] for k in ("subject", "session", "run", "trial_id"))
        if type(s) is not int or s not in SUBJECTS or sess not in SESSIONS or type(run) is not int or run not in RUNS:
            raise ValueError("invalid subject/session/run")
        if not isinstance(tid, str) or not tid or tid.strip() != tid or len(tid) > 128:
            raise ValueError("invalid trial_id")
        if tid in seen:
            raise ValueError("duplicate trial_id across source")
        seen.add(tid)
        counts[s, sess, run] += 1
        groups.setdefault((s, sess, run), []).append(tid)
    expected = {(s, sess, run): TRIALS_PER_RUN for s in SUBJECTS for sess in SESSIONS for run in RUNS}
    if counts != Counter(expected):
        bad = [(k, counts[k], n) for k, n in expected.items() if counts[k] != n]
        raise ValueError(f"missing or unexpected run counts: {bad[:4]}")
    return groups


def _ids(groups, subjects, session, runs):
    return [tid for s in subjects for run in runs for tid in groups[s, session, run]]


def build(payload):
    groups = validate(payload)
    folds = []
    for subject in SUBJECTS:
        for protocol in ("cross_session", "subject_disjoint"):
            train_subjects = (subject,) if protocol == "cross_session" else tuple(s for s in SUBJECTS if s != subject)
            train = _ids(groups, train_subjects, "T", (1, 2, 3, 4))
            calibration = _ids(groups, train_subjects, "T", (5, 6))
            test = _ids(groups, (subject,), "E", RUNS)
            if (set(train) & set(calibration) or set(train) & set(test) or set(calibration) & set(test)):
                raise AssertionError("split overlap")
            folds.append({"protocol": protocol, "held_out_subject": subject,
                          "train_n": len(train), "calibration_n": len(calibration), "test_n": len(test),
                          "train_ids_sha256": _hash_ids(train), "calibration_ids_sha256": _hash_ids(calibration),
                          "test_ids_sha256": _hash_ids(test)})
    return {"status": "METADATA SPLIT PREFLIGHT ONLY — NO EEG READ OR MODEL FIT",
            "dataset": "BNCI2014_001", "expected_trials": 9 * 2 * 6 * 48,
            "protocols": {"cross_session": "same subject T runs 1-4 train, T runs 5-6 calibration, E all runs test",
                          "subject_disjoint": "other subjects T runs 1-4 train, T runs 5-6 calibration, held-out subject E all runs test"},
            "source_file_sha256": "TBD", "loader_version": "TBD", "EEG_results": "TBD", "folds": folds}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    payload = json.loads(a.input.read_text(encoding="utf-8"))
    report = build(payload)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("METADATA ONLY: 18 folds validated; no EEG data or outcomes examined")


if __name__ == "__main__":
    main()
