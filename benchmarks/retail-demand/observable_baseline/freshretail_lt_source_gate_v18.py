"""Fail-closed source-byte gate for FreshRetailNet-LT (2025 temporal transfer).

This module hashes files ONLY; it never parses or inspects evaluation labels.
It is not a forecasting benchmark and cannot assert unseen-label provenance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

DATASET = "Dingdong-Inc/FreshRetailNet-LT"
REVISION = "01c3bb306415e09d3ccd2fe762f33eb3aeb2affd"
TRAIN_SHA256 = "e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3"
EVAL_SHA256 = "370ca7f995d2a059744e1659eb681e60db694bec2f80a84252426afdd2b6d626"
TRAIN_BYTES = 315398578
EVAL_BYTES = 2009424
FORECAST_ORIGIN = "2025-07-14"
FORECAST_LAST_DAY = "2025-07-20"

class SourceGateError(ValueError):
    pass


def hash_file(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            total += len(block)
            h.update(block)
    return total, h.hexdigest()


def verify_file(path: Path, expected_bytes: int, expected_sha256: str) -> dict:
    """Checks exact bytes, never trusts a filename or publisher URL as attestation."""
    if type(expected_bytes) is not int or expected_bytes <= 0:
        raise SourceGateError("invalid expected byte count")
    if (type(expected_sha256) is not str or len(expected_sha256) != 64 or
            any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise SourceGateError("invalid expected SHA-256")
    if not path.is_file():
        raise SourceGateError("source missing or not a regular file")
    size, digest = hash_file(path)
    if size != expected_bytes or digest != expected_sha256:
        raise SourceGateError("source byte size/hash differs from pinned publisher LFS pointer")
    return {"bytes": size, "sha256": digest, "verified_against": "PUBLISHER_LFS_POINTER_NOT_INDEPENDENT_AUTHENTICITY"}


def audit_sources(train: Path, evaluation: Path) -> dict:
    """Production gate uses ONLY frozen constants. No user-supplied hash overrides."""
    if train.resolve() == evaluation.resolve():
        raise SourceGateError("TRAIN and EVAL resolve to the same path")
    t = verify_file(train, TRAIN_BYTES, TRAIN_SHA256)
    e = verify_file(evaluation, EVAL_BYTES, EVAL_SHA256)
    # This does not inspect labels, date ranges, cohort membership, or features.
    return {
        "experiment": "retail-freshretail-lt-source-gate-v18",
        "dataset": DATASET,
        "publisher_revision": REVISION,
        "train": t,
        "eval": e,
        "forecast_origin": FORECAST_ORIGIN,
        "forecast_end": FORECAST_LAST_DAY,
        "evaluation_labels_read": False,
        "temporal_generalization_measured": "TBD",
        "model_comparison_measured": "TBD",
        "source_authenticity_beyond_publisher_host": "TBD",
        "maturity_change": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--eval", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() in (args.train.resolve(), args.eval.resolve()):
        raise SystemExit("refusing to overwrite existing output or source")
    report = audit_sources(args.train, args.eval)
    # Exclusive create prevents clobber if the output appeared after the check.
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print("SOURCE_BYTES_MATCH_PUBLISHER_POINTER; EVAL_LABELS_NOT_READ; METRICS_TBD")


if __name__ == "__main__":
    main()
