"""Read-only, TRAIN-only daily/hourly numeric identity audit for FreshRetailNet-LT.

Checks one narrowly defined field consistency property. It cannot establish
latent demand, returns semantics, forecast accuracy, or inventory benefits.
No EVAL file is accepted or opened, and no source rows are emitted.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import platform
from pathlib import Path

from freshretail_lt_source_gate_v18 import TRAIN_BYTES, TRAIN_SHA256, REVISION, verify_file

ABS_TOL = 1e-8
REL_TOL = 1e-6
EXPECTED_ROWS = 7869549

class IdentityAuditError(ValueError):
    pass


def empty_summary():
    return {"rows": 0, "rows_matching_tolerance": 0, "rows_exceeding_tolerance": 0,
            "rows_abs_difference_over_0_001": 0, "rows_abs_difference_over_0_1": 0,
            "rows_negative_daily": 0, "hourly_negative_values": 0,
            "max_abs_difference": 0.0, "sum_abs_difference": 0.0}


def ingest_block(summary, daily, hourly_sum, lengths, negative_hourly_values=0):
    """Pure numeric core: numpy arrays, fictional unit tests and Arrow runner share it."""
    import numpy as np
    d = np.asarray(daily, dtype=np.float64)
    h = np.asarray(hourly_sum, dtype=np.float64)
    n = np.asarray(lengths)
    if d.ndim != 1 or h.shape != d.shape or n.shape != d.shape:
        raise IdentityAuditError("mismatched one-dimensional columns")
    if np.any(n != 24):
        raise IdentityAuditError("hourly vector length is not 24")
    if not np.all(np.isfinite(d)) or not np.all(np.isfinite(h)):
        raise IdentityAuditError("null or non-finite daily/hourly quantity")
    if type(negative_hourly_values) is not int or negative_hourly_values < 0:
        raise IdentityAuditError("invalid negative hourly count")
    delta = np.abs(d - h)
    tolerance = ABS_TOL + REL_TOL * np.maximum(np.abs(d), np.abs(h))
    bad = delta > tolerance
    summary["rows"] += int(d.size)
    summary["rows_matching_tolerance"] += int(np.count_nonzero(~bad))
    summary["rows_exceeding_tolerance"] += int(np.count_nonzero(bad))
    summary["rows_abs_difference_over_0_001"] += int(np.count_nonzero(delta > 0.001))
    summary["rows_abs_difference_over_0_1"] += int(np.count_nonzero(delta > 0.1))
    summary["rows_negative_daily"] += int(np.count_nonzero(d < 0))
    summary["hourly_negative_values"] += negative_hourly_values
    if d.size:
        summary["max_abs_difference"] = max(summary["max_abs_difference"], float(delta.max()))
        summary["sum_abs_difference"] += float(delta.sum(dtype=np.float64))
    return summary


def audit_parquet(path):
    import numpy as np
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    if not {"sale_amount", "hours_sale"}.issubset(parquet.schema_arrow.names):
        raise IdentityAuditError("required TRAIN columns absent")
    summary = empty_summary()
    for batch in parquet.iter_batches(batch_size=16384, columns=["sale_amount", "hours_sale"]):
        daily, hourly = batch.column(0), batch.column(1)
        if daily.null_count or hourly.null_count:
            raise IdentityAuditError("null daily or hourly vector")
        lengths = np.asarray(pc.list_value_length(hourly).to_numpy(zero_copy_only=False))
        if np.any(lengths != 24):
            raise IdentityAuditError("hourly vector length is not 24")
        flat = pc.list_flatten(hourly)
        if flat.null_count:
            raise IdentityAuditError("null hourly element")
        values = np.asarray(flat.to_numpy(zero_copy_only=False), dtype=np.float64)
        if not np.all(np.isfinite(values)):
            raise IdentityAuditError("non-finite hourly element")
        sums = values.reshape((-1, 24)).sum(axis=1, dtype=np.float64)
        ingest_block(summary, daily.to_numpy(zero_copy_only=False), sums, lengths,
                     negative_hourly_values=int(np.count_nonzero(values < 0)))
    if summary["rows"] != parquet.metadata.num_rows or summary["rows"] != EXPECTED_ROWS:
        raise IdentityAuditError("TRAIN row count differs from pinned publisher metadata")
    summary["numeric_identity_status"] = (
        "CONSISTENT_WITHIN_PREDECLARED_TOLERANCE" if summary["rows_exceeding_tolerance"] == 0
        else "REVIEW_REQUIRED_NUMERIC_MISMATCH")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.train.resolve():
        raise SystemExit("refusing to overwrite output or TRAIN source")
    source = verify_file(args.train, TRAIN_BYTES, TRAIN_SHA256)
    summary = audit_parquet(args.train)
    import pyarrow
    result = {
        "experiment": "retail-lt-train-only-daily-hourly-identity-v26",
        "provenance": {"dataset": "Dingdong-Inc/FreshRetailNet-LT", "revision": REVISION,
                       "train_bytes": source["bytes"], "train_sha256": source["sha256"],
                       "source_authenticity_beyond_publisher": "TBD", "python": platform.python_version(),
                       "pyarrow": pyarrow.__version__, "runner_os": platform.system(),
                       "git_checkout": os.environ.get("GITHUB_SHA", "TBD")},
        "tolerances": {"absolute": ABS_TOL, "relative": REL_TOL},
        "training_only": True, "evaluation_file_opened": False, "evaluation_labels_read": False,
        "forecast_accuracy": "TBD", "same_target_latent_demand_floor": "TBD",
        "returns_substitutions_cancellations": "TBD", "maturity_change": "NONE",
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"rows": summary["rows"], "status": summary["numeric_identity_status"],
                      "mismatches": summary["rows_exceeding_tolerance"],
                      "evaluation_labels_read": False}, sort_keys=True))

if __name__ == "__main__":
    main()
