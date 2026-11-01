"""TRAIN-only cohort preflight for preregistered FreshRetailNet-LT v1.8.

Never opens evaluation Parquet, never scores forecasts, never selects using
future coverage. This is a source/eligibility experiment, not performance.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
from pathlib import Path

from freshretail_lt_source_gate_v18 import TRAIN_BYTES, TRAIN_SHA256, verify_file

START = dt.date(2025, 4, 15)
END = dt.date(2025, 7, 13)
ORIGIN = dt.date(2025, 7, 14)
DAYS = 90
COHORT = 512
SALT = "retail-lt-v18-20261028"
FIELDS = ("store_id", "product_id", "dt", "hours_stock_status", "stock_hour6_22_cnt")
FULL_MASK = (1 << DAYS) - 1


class CohortGateError(ValueError):
    pass


def day(value):
    if type(value) is dt.datetime:
        raise CohortGateError("ambiguous datetime in daily records")
    if type(value) is dt.date:
        return value
    if type(value) is str:
        try:
            parsed = dt.date.fromisoformat(value)
        except ValueError as exc:
            raise CohortGateError("invalid daily date") from exc
        if parsed.isoformat() != value:
            raise CohortGateError("noncanonical daily date")
        return parsed
    raise CohortGateError("invalid date type")


def key_of(row):
    a, b = row["store_id"], row["product_id"]
    if type(a) is not int or type(b) is not int or a < 0 or b < 0:
        raise CohortGateError("invalid series key")
    return (a, b)


def valid_status(row):
    flags, count = row["hours_stock_status"], row["stock_hour6_22_cnt"]
    return (type(flags) is list and len(flags) == 24 and
            all(type(v) is int and v in (0, 1) for v in flags) and
            type(count) is int and 0 <= count <= 16 and
            sum(flags[6:22]) == count)


def rank(key):
    return (hashlib.sha256(f"{SALT}|{key[0]}|{key[1]}".encode("ascii")).digest(), key)


def audit_training_rows(rows, cohort_size=COHORT):
    """Fail closed for incomplete, duplicated or invalid TRAIN series."""
    if type(cohort_size) is not int or cohort_size < 1:
        raise CohortGateError("invalid cohort size")
    masks, bad = {}, set()
    in_window = duplicates = invalid_status = outside = 0
    for row in rows:
        k = key_of(row)
        d = day(row["dt"])
        if d >= ORIGIN:
            raise CohortGateError("TRAIN contains evaluation-origin or later date")
        if d < START:
            outside += 1
            continue
        if d > END:
            raise CohortGateError("unexpected pre-origin training date")
        in_window += 1
        bit = 1 << (d - START).days
        old = masks.get(k, 0)
        if old & bit:
            duplicates += 1
            bad.add(k)
        masks[k] = old | bit
        if not valid_status(row):
            invalid_status += 1
            bad.add(k)
    eligible = [k for k, mask in masks.items() if mask == FULL_MASK and k not in bad]
    selected = sorted(eligible, key=rank)[:cohort_size]
    digest = (hashlib.sha256(json.dumps(selected, separators=(",", ":")).encode("ascii")).hexdigest()
              if len(selected) == cohort_size else "TBD")
    return {
        "experiment": "retail-lt-train-only-cohort-v19",
        "analysis": "TRAIN_ONLY_NO_EVAL_LABEL_ACCESS",
        "status": ("TRAIN_COHORT_FROZEN_NO_EVAL_ACCESS" if len(selected) == cohort_size
                   else "STOP_INSUFFICIENT_ELIGIBLE_TRAIN_SERIES"),
        "training_window": [START.isoformat(), END.isoformat()],
        "forecast_origin": ORIGIN.isoformat(),
        "required_training_days_per_series": DAYS,
        "required_cohort": cohort_size,
        "training_rows_in_window": in_window,
        "earlier_training_rows_ignored": outside,
        "distinct_training_series": len(masks),
        "eligible_complete_valid_series": len(eligible),
        "duplicate_training_rows": duplicates,
        "invalid_stock_status_rows": invalid_status,
        "selected_series": len(selected) if len(selected) == cohort_size else 0,
        "selected_cohort_sha256": digest,
        "evaluation_file_opened": False,
        "evaluation_labels_read": False,
        "forecast_scores": "TBD",
        "latent_demand_accuracy": "TBD",
        "maturity_change": "NONE",
    }


def parquet_rows(path):
    import pyarrow.parquet as pq
    file = pq.ParquetFile(path)
    if not set(FIELDS).issubset(file.schema_arrow.names):
        raise CohortGateError("missing required TRAIN columns")
    for batch in file.iter_batches(batch_size=8192, columns=list(FIELDS)):
        yield from batch.to_pylist()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--train", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite an evidence artifact")
    source = verify_file(args.train, TRAIN_BYTES, TRAIN_SHA256)
    result = audit_training_rows(parquet_rows(args.train))
    import pyarrow
    result["provenance"] = {
        "dataset": "Dingdong-Inc/FreshRetailNet-LT",
        "publisher_revision": "01c3bb306415e09d3ccd2fe762f33eb3aeb2affd",
        "train_bytes_verified": source["bytes"],
        "train_sha256_verified": source["sha256"],
        "source_authenticity_beyond_publisher": "TBD",
        "python": platform.python_version(),
        "pyarrow": pyarrow.__version__,
        "runner_os": platform.system(),
        "git_checkout": os.environ.get("GITHUB_SHA", "TBD"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in
                      ("status", "eligible_complete_valid_series", "selected_cohort_sha256",
                       "evaluation_labels_read")}, sort_keys=True))


if __name__ == "__main__":
    main()
