#!/usr/bin/env python3
"""Metadata-only A04T training-file preflight; no labels or EEG are exported.

The official BCI IV-2a description documents a shortened EOG calibration block
for A04T. Do not silently require the A02T three-baseline layout. This is
source-structure evidence only, not decoder or clinical validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

import bnci_a02t_metadata_v03 as base

FILE = "A04T.mat"
SOURCE = "https://bnci-horizon-2020.eu/database/data-sets/001-2014/" + FILE
ALLOWED = {
    ("bnci-horizon-2020.eu", "/database/data-sets/001-2014/" + FILE),
    ("lampx.tugraz.at", "/~bci/database/001-2014/" + FILE),
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def validate_url(url: str) -> None:
    require(type(url) is str, "invalid URL")
    p = urlparse(url)
    require(p.scheme == "https" and (p.hostname, p.path) in ALLOWED and
            not p.username and not p.password and p.port is None and
            not p.query and not p.fragment, "unapproved source or redirect")


class StrictRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_bytes() -> bytes:
    validate_url(SOURCE)
    opener = build_opener(StrictRedirect())
    req = Request(SOURCE, headers={"Accept-Encoding": "identity", "User-Agent": "WBI-training-structure/0.5"})
    with opener.open(req, timeout=90) as response:
        validate_url(response.geturl())
        require(response.status == 200, "unexpected HTTP status")
        declared = response.headers.get("Content-Length")
        if declared is not None:
            require(declared.isascii() and declared.isdecimal() and
                    128 <= int(declared) <= base.MAX_BYTES, "invalid declared size")
        blocks, size = [], 0
        while True:
            part = response.read(1024 * 1024)
            if not part:
                break
            size += len(part)
            require(size <= base.MAX_BYTES, "source exceeds byte limit")
            blocks.append(part)
        if declared is not None:
            require(size == int(declared), "truncated transfer")
    return b"".join(blocks)


def validate_derived(report: dict, raw: bytes) -> dict:
    """Enforce exception-aware structure, but do NOT pretend to pin unknown source bytes."""
    require(type(report) is dict, "invalid report")
    require(report.get("source_sha256") == hashlib.sha256(raw).hexdigest(), "source digest mismatch")
    require(type(report.get("source_bytes")) is int and report["source_bytes"] == len(raw), "source length mismatch")
    require(re.fullmatch(r"[0-9a-f]{64}", report["source_sha256"]) is not None, "invalid digest")
    for key, expected in (
        ("dataset", "BNCI2014_001"), ("session", "T_training"),
        ("sha256_is_provider_authenticated", False),
        ("class_label_values_inspected", False),
        ("raw_eeg_persisted_or_uploaded", False),
        ("evaluation_session_or_labels_accessed", False),
        ("decode_accuracy", "TBD"), ("false_action_risk", "TBD"),
    ):
        require(type(report.get(key)) is type(expected) and report[key] == expected,
                "unexpected provenance or performance field: " + key)
    blocks = report.get("block_metadata")
    require(type(blocks) is list and 7 <= len(blocks) <= 9, "unexpected block count")
    n_baseline = len(blocks) - 6
    require(1 <= n_baseline <= 3, "unexpected baseline count")
    require(type(report.get("blocks")) is int and report["blocks"] == len(blocks), "block summary mismatch")
    require(type(report.get("cue_free_baseline_blocks")) is int and
            report["cue_free_baseline_blocks"] == n_baseline, "baseline summary mismatch")
    require(type(report.get("cued_task_blocks")) is int and report["cued_task_blocks"] == 6,
            "task summary mismatch")
    require(type(report.get("cues_total")) is int and report["cues_total"] == 288,
            "cue summary mismatch")
    for i, block in enumerate(blocks):
        require(type(block) is dict and type(block.get("block_index_zero_based")) is int and
                block["block_index_zero_based"] == i, "invalid block index")
        require(type(block.get("samples")) is int and block["samples"] > 0,
                "invalid sample count")
        require(type(block.get("channels")) is int and block["channels"] == 25,
                "unexpected channel count")
        require(type(block.get("sampling_rate_hz")) in (float, int) and
                block["sampling_rate_hz"] == 250.0, "unexpected sample rate")
        require(type(block.get("cue_count")) is int and
                block["cue_count"] == (0 if i < n_baseline else 48),
                "baseline/task sequence mismatch")
    require(report.get("six_task_runs_48_cues_each") is True,
            "task-run count flag mismatch")
    return report


def inspect_training_bytes(raw: bytes) -> dict:
    # Reuse the existing MAT reader; override only source-specific metadata.
    report = base.inspect_bytes(raw)
    report.update(file=FILE, source_url=SOURCE)
    validate_derived(report, raw)
    report["a04t_eog_exception_allowed"] = True
    report["source_hash_status"] = "observed, not independently pinned"
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    target = Path(args.output)
    if target.exists():
        raise SystemExit("refusing to overwrite evidence")
    report = inspect_training_bytes(fetch_bytes())
    target.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
          ("file", "source_sha256", "source_bytes", "blocks", "cue_free_baseline_blocks",
           "cued_task_blocks", "cues_total", "source_hash_status")}, sort_keys=True))


if __name__ == "__main__":
    main()
