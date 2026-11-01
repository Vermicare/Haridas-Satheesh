"""FreshRetailNet-LT v2.7: fail-closed *coverage* gate, NOT a scorer.

Official forecasting requires one finite, nonnegative prediction for every EVAL
(store_id, product_id, dt) target before publisher eligibility masking.
Only public target keys are read from a byte-pinned private EVAL parquet file.
No evaluation answer fields, identifiers or predictions are emitted to output.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

EVAL_BYTES = 2_009_424
EVAL_SHA256 = "370ca7f995d2a059744e1659eb681e60db694bec2f80a84252426afdd2b6d626"
REVISION = "01c3bb306415e09d3ccd2fe762f33eb3aeb2affd"
EXPECTED_TARGETS = 70_000
DATES = {dt.date(2025, 7, 14) + dt.timedelta(days=i) for i in range(7)}
FIELDS = ["store_id", "product_id", "dt", "prediction"]


class CoverageError(ValueError):
    pass


def _id(value):
    if type(value) is int and value >= 0:
        return value
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise CoverageError("invalid target identifier")
    if len(value) > 18 or (len(value) > 1 and value[0] == "0"):
        raise CoverageError("noncanonical target identifier")
    return int(value)


def _date(value):
    if not isinstance(value, str):
        raise CoverageError("invalid target date")
    try:
        d = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise CoverageError("invalid target date") from exc
    if d.isoformat() != value or d not in DATES:
        raise CoverageError("date outside official forecasting horizon")
    return value


def key(row):
    try:
        return (_id(row["store_id"]), _id(row["product_id"]), _date(row["dt"]))
    except (KeyError, TypeError) as exc:
        raise CoverageError("missing target key field") from exc


def validate(target_rows, prediction_rows, *, expected=EXPECTED_TARGETS):
    """Exact set equality with strict duplicates; return aggregate-only result."""
    if not isinstance(expected, int) or expected < 1:
        raise CoverageError("invalid expected target count")
    targets = set()
    for row in target_rows:
        k = key(row)
        if k in targets:
            raise CoverageError("duplicate evaluation target")
        targets.add(k)
        if len(targets) > expected:
            raise CoverageError("too many evaluation targets")
    if len(targets) != expected:
        raise CoverageError("evaluation target count mismatch")
    seen = set()
    for row in prediction_rows:
        k = key(row)
        if k in seen:
            raise CoverageError("duplicate prediction key")
        if k not in targets:
            raise CoverageError("prediction key absent from evaluation targets")
        try:
            raw = row["prediction"]
            if isinstance(raw, bool) or raw is None:
                raise ValueError()
            value = float(raw)
        except (KeyError, ValueError, TypeError, OverflowError) as exc:
            raise CoverageError("invalid prediction") from exc
        if not math.isfinite(value) or value < 0:
            raise CoverageError("nonfinite or negative prediction")
        seen.add(k)
    if len(seen) != len(targets):
        raise CoverageError("missing prediction targets")
    return {"coverage": "PASS_FULL_TARGET_ONLY", "target_rows": len(targets),
            "prediction_rows": len(seen), "scored_rows": "TBD",
            "publisher_psd_and_stockout_mask_applied": False,
            "official_leaderboard_comparable": False,
            "publisher_review": "TBD", "maturity_change": "NONE"}


def _verify_eval(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            size += len(chunk)
            if size > EVAL_BYTES:
                raise CoverageError("EVAL size mismatch")
            digest.update(chunk)
    if size != EVAL_BYTES or digest.hexdigest() != EVAL_SHA256:
        raise CoverageError("EVAL byte pin mismatch")


def _targets(path):
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=8192, columns=FIELDS[:3]):
        yield from batch.to_pylist()


def _predictions(path):
    if path.stat().st_size > 12 * 1024 * 1024:
        raise CoverageError("prediction CSV exceeds publisher browser limit")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise CoverageError("prediction CSV header mismatch")
        for row in reader:
            if None in row:
                raise CoverageError("extra CSV fields")
            yield row


def run(eval_path, predictions_path):
    eval_path, predictions_path = Path(eval_path), Path(predictions_path)
    if eval_path.resolve() == predictions_path.resolve():
        raise CoverageError("evaluation and prediction files must differ")
    _verify_eval(eval_path)  # Never parse any EVAL fields before exact byte pin.
    report = validate(_targets(eval_path), _predictions(predictions_path))
    _verify_eval(eval_path)  # Detect ordinary file replacement during inspection.
    return {"experiment": "retail-lt-v27-full-target-coverage-preflight",
            "source": {"dataset": "Dingdong-Inc/FreshRetailNet-LT",
                       "revision": REVISION, "eval_sha256": EVAL_SHA256},
            "evidence": "COVERAGE_ONLY_NO_SCORING_OR_LABEL_INSPECTION",
            "result": report}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eval", type=Path, required=True)
    p.add_argument("--predictions", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or args.output.resolve() in (args.eval.resolve(), args.predictions.resolve()):
        raise SystemExit("refusing to overwrite input or existing evidence")
    report = run(args.eval, args.predictions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["result"], sort_keys=True))


if __name__ == "__main__":
    main()
