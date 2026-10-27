#!/usr/bin/env python3
"""Fail-closed A02T source-metadata acceptance gate; no EEG samples or labels.

This validates *metadata emitted by the separate A02T inspector*. Matching
source bytes is not publisher authentication. Passing does not measure EEG
decoding, action safety, or clinical performance.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXPECTED_SHA256 = "5ddd5cb520b1692c3ba1363f48d98f58f0e46f3699ee50d749947950fc39db27"
EXPECTED_BYTES = 43068077
EXPECTED_SOURCE = "https://bnci-horizon-2020.eu/database/data-sets/001-2014/A02T.mat"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_int(value, expected):
    return type(value) is int and value == expected


def validate(report):
    """Return bounded metadata summary or raise ValueError; no silent warnings."""
    require(type(report) is dict, "metadata must be a JSON object")
    for key, value in (
        ("dataset", "BNCI2014_001"), ("file", "A02T.mat"),
        ("session", "T_training"), ("source_url", EXPECTED_SOURCE),
        ("source_sha256", EXPECTED_SHA256),
    ):
        require(report.get(key) == value, "unexpected " + key)
    require(re.fullmatch(r"[0-9a-f]{64}", report["source_sha256"]) is not None,
            "invalid source hash")
    require(exact_int(report.get("source_bytes"), EXPECTED_BYTES),
            "source byte identity changed")
    for key, expected in (
        ("sha256_is_provider_authenticated", False),
        ("class_label_values_inspected", False),
        ("raw_eeg_persisted_or_uploaded", False),
        ("evaluation_session_or_labels_accessed", False),
        ("six_task_runs_48_cues_each", True),
    ):
        require(type(report.get(key)) is bool and report[key] is expected,
                "unexpected or missing privacy/provenance flag: " + key)
    for key, expected in (
        ("blocks", 9), ("cue_free_baseline_blocks", 3),
        ("cued_task_blocks", 6), ("cues_total", 288),
    ):
        require(exact_int(report.get(key), expected), "unexpected summary: " + key)
    require(report.get("decode_accuracy") == "TBD" and
            report.get("false_action_risk") == "TBD",
            "unverified performance claim in source metadata")
    blocks = report.get("block_metadata")
    require(type(blocks) is list and len(blocks) == 9, "invalid block list")
    for i, block in enumerate(blocks):
        require(type(block) is dict, "invalid block object")
        require(exact_int(block.get("block_index_zero_based"), i),
                "wrong or reordered block index")
        require(type(block.get("samples")) is int and block["samples"] > 0,
                "invalid sample count")
        require(exact_int(block.get("channels"), 25), "unexpected channel count")
        require(type(block.get("sampling_rate_hz")) in (int, float) and
                block["sampling_rate_hz"] == 250.0,
                "unexpected sampling frequency")
        require(exact_int(block.get("cue_count"), 0 if i < 3 else 48),
                "baseline/task block mismatch")
    return {
        "file": "A02T.mat",
        "source_sha256": EXPECTED_SHA256,
        "blocks": 9,
        "baseline_blocks": 3,
        "task_blocks": 6,
        "cues": 288,
        "accepted_as": "metadata-only training-source structural evidence",
        "decoder_and_safety_metrics": "TBD",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Existing metadata JSON; never raw MAT")
    args = parser.parse_args()
    with Path(args.input).open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    print(json.dumps(validate(report), sort_keys=True))


if __name__ == "__main__":
    main()
