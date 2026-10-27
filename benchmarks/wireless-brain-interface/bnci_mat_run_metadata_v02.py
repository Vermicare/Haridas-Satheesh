#!/usr/bin/env python3
"""Inspect public BNCI A01T MAT run metadata only; no raw EEG or labels published."""
from __future__ import annotations
import argparse
from io import BytesIO
import hashlib
import json
import platform
from urllib.request import Request, build_opener
import numpy as np
from scipy import __version__ as scipy_version
from scipy.io import loadmat
from bnci2014_001_source_probe import SOURCE_URL, MAX_BYTES, CHUNK_BYTES, PinnedRedirect, validate_source_url

EXPECTED_BYTES = 42806453
EXPECTED_SHA256 = "054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325"

def inspect_mat_bytes(raw: bytes, *, expected_sha256: str = EXPECTED_SHA256, expected_bytes: int = EXPECTED_BYTES) -> dict:
    if len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("A01T source byte identity differs from prior hosted acquisition")
    if not raw.startswith(b"MATLAB 5.0 MAT-file"):
        raise ValueError("not a MATLAB 5 file")
    obj = loadmat(BytesIO(raw), struct_as_record=False, squeeze_me=True, variable_names=["data"])
    if "data" not in obj:
        raise ValueError("missing data variable")
    container = obj["data"]
    runs = list(np.asarray(container, dtype=object).flat) if isinstance(container, np.ndarray) else [container]
    if not runs or len(runs) > 20:
        raise ValueError("unexpected number of recording blocks")
    report_runs = []
    for index, run in enumerate(runs):
        if not all(hasattr(run, k) for k in ("X", "fs", "trial", "y")):
            raise ValueError(f"run {index} missing required structural fields")
        shape = np.shape(run.X)
        if len(shape) != 2 or shape[0] <= 0 or shape[1] <= 0:
            raise ValueError(f"run {index} has invalid signal shape")
        fs = np.asarray(run.fs)
        if fs.size != 1 or float(fs.reshape(-1)[0]) <= 0:
            raise ValueError(f"run {index} has invalid sample rate")
        trials = np.asarray(run.trial).reshape(-1)
        labels = np.asarray(run.y).reshape(-1)
        if trials.size != labels.size:
            raise ValueError(f"run {index} trial/label cardinality mismatch")
        if trials.size and (not np.issubdtype(trials.dtype, np.number)
                            or np.any(trials < 1) or np.any(trials > shape[0])
                            or np.unique(trials).size != trials.size):
            raise ValueError(f"run {index} has invalid trial indices")
        report_runs.append({
            "mat_block_index_zero_based": index,
            "sample_count": int(shape[0]),
            "channel_count": int(shape[1]),
            "sampling_rate_hz": float(fs.reshape(-1)[0]),
            "cue_count": int(trials.size),
            "has_cues": bool(trials.size),
        })
    task_runs = [r for r in report_runs if r["has_cues"]]
    baseline_runs = [r for r in report_runs if not r["has_cues"]]
    return {
        "dataset": "BNCI2014_001", "file": "A01T.mat", "session": "T_training_only",
        "source_sha256": expected_sha256, "source_bytes": expected_bytes,
        "mat_blocks": len(report_runs), "baseline_blocks_without_cues": len(baseline_runs),
        "task_blocks_with_cues": len(task_runs),
        "task_cues_total": sum(r["cue_count"] for r in task_runs),
        "run_metadata": report_runs,
        "documented_six_task_runs_48_cues_each": len(task_runs) == 6 and all(r["cue_count"] == 48 for r in task_runs),
        "mat_block_indices_are_not_task_run_indices": bool(baseline_runs),
        "scipy_version": scipy_version, "numpy_version": np.__version__,
        "python_version": platform.python_version(),
        "raw_eeg_saved_or_uploaded": False, "class_labels_reported": False,
        "evaluation_session_or_labels_accessed": False,
        "decoding_accuracy": "TBD", "false_action_risk": "TBD",
        "source_authenticity": "TBD; hash only identifies previously fetched bytes",
        "maturity": "Research / Simulation (unchanged)",
    }

def fetch_mat_bytes() -> bytes:
    opener = build_opener(PinnedRedirect())
    with opener.open(Request(SOURCE_URL, headers={"User-Agent": "WBI-metadata-preflight/0.2", "Accept-Encoding": "identity"}), timeout=90) as response:
        validate_source_url(response.geturl())
        if response.status != 200:
            raise ValueError("source did not return HTTP 200")
        length = response.headers.get("Content-Length")
        if length is not None and (not length.isascii() or not length.isdecimal() or int(length) != EXPECTED_BYTES):
            raise ValueError("unexpected source Content-Length")
        chunks = []
        total = 0
        while True:
            block = response.read(CHUNK_BYTES)
            if not block:
                break
            total += len(block)
            if total > MAX_BYTES or total > EXPECTED_BYTES:
                raise ValueError("source exceeds pinned size")
            chunks.append(block)
        if total != EXPECTED_BYTES:
            raise ValueError("incomplete source")
        return b"".join(chunks)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Metadata-only JSON path")
    args = parser.parse_args()
    try:
        report = inspect_mat_bytes(fetch_mat_bytes())
    except Exception as exc:
        print(f"MAT_METADATA_FAILED: {type(exc).__name__}: {str(exc)[:160]}")
        return 2
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
