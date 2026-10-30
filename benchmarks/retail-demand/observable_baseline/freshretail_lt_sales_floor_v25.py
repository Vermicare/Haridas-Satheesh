#!/usr/bin/env python3
"""Retail v2.5: post-hoc conditional observed-sales-floor bounds on FROZEN 2025 data.

Reproduces v2.4 first; separately re-seals TRAIN before EVAL access. Assumes
recorded business-hour sales <= same-target latent demand on stockout days.
This is a conditional logical sensitivity, not measured lost demand or a
new confirmatory benchmark. Only aggregate statistics leave the process.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import platform

import freshretail_lt_stockout_bounds_v24 as v24
import retail_sales_floor_bounds_v25 as floor
from parquet_export import normalized_row
from retail_gate import parse_row

SCHEMA = "retail-lt-v25-conditional-sales-floor-transfer"


class TransferError(ValueError):
    pass


def score_floor(selected, predictions, evaluation_rows, original_bounds):
    by_key = defaultdict(dict)
    for i, raw in enumerate(evaluation_rows, 1):
        key = v24.v21.v19.key_of(raw)
        if key not in predictions:
            raise TransferError("noncohort EVAL row")
        row = parse_row(normalized_row(raw, i), i)
        if row["day"] not in v24.v21.v20.FUTURE or row["day"] in by_key[key]:
            raise TransferError("duplicate or out-of-horizon EVAL day")
        by_key[key][row["day"]] = row
    if not selected or set(selected) != set(predictions):
        raise TransferError("invalid selected cohort")
    inputs = {name: [] for name in v24.COMPARATORS}
    ordinal = 0
    for key in selected:
        if set(by_key[key]) != set(v24.v21.v20.FUTURE):
            raise TransferError("incomplete selected EVAL horizon")
        if set(predictions[key]) != set(v24.v21.METHODS):
            raise TransferError("changed prediction methods")
        for i, day in enumerate(v24.v21.v20.FUTURE):
            ordinal += 1
            row = by_key[key][day]
            for name in v24.COMPARATORS:
                entry = {"key": str(ordinal),
                         "a": predictions[key][v24.CANDIDATE][i],
                         "b": predictions[key][name][i],
                         "observed": not row["censored"]}
                if row["censored"]:
                    # Actual recorded sales are a FLOOR, never a latent-demand label.
                    entry["sales_floor"] = row["y"]
                else:
                    entry["y"] = row["y"]
                inputs[name].append(entry)
    result = {}
    for name in v24.COMPARATORS:
        r = floor.evaluate({"schema": floor.INPUT_SCHEMA, "rows": inputs[name]})
        old = original_bounds[name]
        if (r["observed_days"], r["censored_days"]) != (
                old["observed_days"], old["censored_days"]):
            raise TransferError("denominator mismatch")
        for a, b in (("nonnegative_only_lower", "full_period_paired_mae_delta_lower"),
                     ("nonnegative_only_upper", "full_period_paired_mae_delta_upper"),
                     ("observed_only_paired_mae_delta_A_minus_B",
                      "observed_only_paired_mae_delta_A_minus_B")):
            if not math.isclose(r[a], old[b], abs_tol=1e-10, rel_tol=0):
                raise TransferError("original v2.4 logical bounds mismatch")
        result[name] = r
    return result


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if train.resolve() == evaluation.resolve():
        raise TransferError("TRAIN and EVAL cannot be identical")
    # Reproduce the original v2.4 pinned source, forecast, labels and outcomes.
    old = v24.run(train, evaluation)
    # Independently reconstruct the frozen TRAIN-only seal before another EVAL read.
    selected, predictions, seal = v24.v21.reproduce_before_labels(train)
    if seal != old["frozen_prediction_sha256"]:
        raise TransferError("original forecast seal mismatch")
    v24.v21.verify_file(evaluation, v24.v21.EVAL_BYTES, v24.v21.EVAL_SHA256)
    rows = list(v24.v21.selected_eval_rows(evaluation, selected))
    new = score_floor(selected, predictions, rows, old["paired_full_period_bounds"])
    v24.v21.verify_file(train, v24.v21.TRAIN_BYTES, v24.v21.TRAIN_SHA256)
    v24.v21.verify_file(evaluation, v24.v21.EVAL_BYTES, v24.v21.EVAL_SHA256)
    return {
        "schema": SCHEMA,
        "analysis": "POST_HOC_CONDITIONAL_SALES_FLOOR_PUBLIC_2025_LABELS",
        "source": old["source"],
        "frozen_prediction_sha256": seal,
        "frozen_cohort_sha256": old["frozen_cohort_sha256"],
        "observed_days": old["observed_days"],
        "censored_days": old["censored_days"],
        "historical_v21_primary": old["historical_v21_primary"],
        "historical_v22_strongest_comparator": old["historical_v22_strongest_comparator"],
        "historical_v15_2024_primary": old["historical_v15_2024_primary"],
        "conditional_sales_floor_bounds": new,
        "original_v24_preserved": True,
        "source_sales_are_same_target_lower_bound": "ASSUMED_NOT_INDEPENDENTLY_VERIFIED",
        "no_censored_latent_demand_imputed": True,
        "external_validation": "TBD",
        "inventory_decision_value": "TBD",
        "maturity_change": "NONE",
        "provenance": {"python": platform.python_version(), "os": platform.system(),
                       "git_checkout": os.environ.get("GITHUB_SHA", "TBD")}
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--train", type=Path, required=True)
    p.add_argument("--eval", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or args.output.resolve() in (args.train.resolve(), args.eval.resolve()):
        raise SystemExit("refusing to overwrite source or existing evidence")
    result = run(args.train, args.eval)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"schema": SCHEMA,
                      "counts": [result["observed_days"], result["censored_days"]],
                      "bounds": {k: {"lower": v["sales_floor_lower"],
                                     "upper": v["sales_floor_upper"],
                                     "decision": v["identification_decision"],
                                     "positive_floor_days": v["censored_days_with_positive_sales_floor"]}
                                 for k, v in result["conditional_sales_floor_bounds"].items()}},
                     sort_keys=True))


if __name__ == "__main__":
    main()
