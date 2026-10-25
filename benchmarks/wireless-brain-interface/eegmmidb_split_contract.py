#!/usr/bin/env python3
"""Pre-register subject-disjoint PhysioNet EEGMMIDB splits; NO EEG is loaded.

This is a public-data *preflight*, not EEG decoding or validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DATASET = "PhysioNet EEG Motor Movement/Imagery Dataset"
VERSION = "1.0.0"
DOI = "10.13026/C28G6P"
LICENSE = "ODC-By-1.0"
SEED_TAG = "WBI-EEGMMIDB-V1-SUBJECT-DISJOINT-20261024"
SUBJECTS = tuple(range(1, 110))
RUNS = (4, 8, 12)  # Imagined left/right fist only, not movement or hands/feet.
SPLIT_SIZES = {"train": 70, "calibration": 19, "test": 20}
# MOABB documentation identifies these as 128-Hz recordings, not 160 Hz.
SAMPLING_RATE_EXCEPTIONS = (88, 92, 100)


def subject_id(n: int) -> str:
    if not isinstance(n, int) or n not in SUBJECTS:
        raise ValueError("subject must be an integer from 1 through 109")
    return f"S{n:03d}"


def ordered_subjects() -> list[int]:
    return sorted(SUBJECTS, key=lambda n: (
        hashlib.sha256(f"{SEED_TAG}|{subject_id(n)}".encode("ascii")).hexdigest(), n
    ))


def generate() -> dict:
    order = ordered_subjects()
    partitions = {}
    offset = 0
    for split, count in SPLIT_SIZES.items():
        partitions[split] = sorted(order[offset:offset + count])
        offset += count
    assert offset == len(SUBJECTS)
    files = {split: [f"{subject_id(n)}/{subject_id(n)}R{run:02d}.edf"
                     for n in ids for run in RUNS]
             for split, ids in partitions.items()}
    return {
        "scope": "PLANNED SPLITS ONLY; EEG FILES NOT ACQUIRED OR ANALYZED",
        "dataset": DATASET, "version": VERSION, "doi": DOI, "license": LICENSE,
        "split_seed_tag": SEED_TAG,
        "split_algorithm": "sort by SHA256(ASCII seed_tag + '|' + subject_id), then subject number; 70/19/20",
        "design": "subject-disjoint, cross-subject held-out test; same-session runs; NOT longitudinal",
        "imagery_runs": list(RUNS),
        "event_mapping": {"T0": "rest-exclude", "T1": "imagined-left-fist", "T2": "imagined-right-fist"},
        "sampling_rate_exceptions_subjects_128hz": list(SAMPLING_RATE_EXCEPTIONS),
        "sampling_rate_check": "TBD: inspect each actual EDF before preprocessing; do not assume 160 Hz",
        "subject_splits": {k: [subject_id(n) for n in v] for k, v in partitions.items()},
        "expected_edf_files": files,
        "data_access": "NOT PERFORMED", "actual_file_sha256": "TBD",
        "preprocessing": "TBD: fit exclusively on train, calibration-only thresholds, locked test",
        "performance": "TBD", "clinical_or_device_validation": "NONE",
    }


def validate(manifest: dict) -> None:
    expected = generate()
    if manifest != expected:
        raise ValueError("manifest differs from frozen preregistered split contract")
    groups = [set(ids) for ids in manifest["subject_splits"].values()]
    if any(groups[i] & groups[j] for i in range(len(groups)) for j in range(i + 1, len(groups))):
        raise ValueError("subject leakage between splits")
    if set.union(*groups) != {subject_id(n) for n in SUBJECTS}:
        raise ValueError("missing or duplicate subjects")
    for split, files in manifest["expected_edf_files"].items():
        if len(files) != len(manifest["subject_splits"][split]) * len(RUNS):
            raise ValueError("incomplete run assignment")


def canonical_json(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("eegmmidb_subject_splits.json"))
    args = parser.parse_args()
    report = generate()
    validate(report)
    payload = canonical_json(report)
    args.out.write_bytes(payload)
    print(f"PRE-REGISTRATION ONLY; no EEG read; train=70 calibration=19 test=20; "
          f"expected EDF files=327; SHA256={hashlib.sha256(payload).hexdigest()}")


if __name__ == "__main__":
    main()
