#!/usr/bin/env python3
"""Retail v2.4: apply v2.3 logical bounds to FROZEN 2025 paired public forecasts.

Post-hoc sensitivity, NOT a new holdout, confidence interval, demand recovery,
or evidence of inventory value. No publisher rows/series IDs leave this process.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import platform

import freshretail_lt_score_v21 as v21
import freshretail_lt_secondary_v22 as v22
import stockout_identification_bounds_v23 as bounds
from parquet_export import normalized_row
from retail_gate import parse_row

CANDIDATE = "weekday_median_last4"
COMPARATORS = ("last_observed", "causal_stockout_history")
EXPECTED = (512, 3584, 1766, 1818)
SCHEMA = "retail-lt-v24-observed-versus-latent-bounds"


class BoundsTransferError(ValueError):
    pass


def score_bounds(selected, predictions, evaluation_rows, original):
    """Build ephemeral paired rows; export ONLY aggregate logical intervals."""
    if (len(selected), original["expected_future_days"],
        original["observed_in_stock_days_scored"],
        original["censored_stockout_days_excluded"]) != (
            len(selected), len(selected) * 7,
            original["observed_in_stock_days_scored"],
            original["censored_stockout_days_excluded"]):
        raise BoundsTransferError("original denominator inconsistency")
    if not selected or len(set(selected)) != len(selected) or set(selected) != set(predictions):
        raise BoundsTransferError("cohort or prediction mismatch")
    by_key = defaultdict(dict)
    for index, raw in enumerate(evaluation_rows, 1):
        key = v21.v19.key_of(raw)
        if key not in predictions:
            raise BoundsTransferError("noncohort EVAL row")
        row = parse_row(normalized_row(raw, index), index)
        day = row["day"]
        if day not in v21.v20.FUTURE or day in by_key[key]:
            raise BoundsTransferError("duplicate or out-of-horizon EVAL day")
        by_key[key][day] = row
    inputs = {name: [] for name in COMPARATORS}
    n_obs = 0
    n_cens = 0
    for key in selected:
        if set(by_key[key]) != set(v21.v20.FUTURE):
            raise BoundsTransferError("incomplete seven-day EVAL horizon")
        if set(predictions[key]) != set(v21.METHODS):
            raise BoundsTransferError("changed frozen method set")
        for method in (CANDIDATE,) + COMPARATORS:
            ps = predictions[key][method]
            if len(ps) != 7 or any(type(p) not in (int, float) or
                                    not math.isfinite(p) or p < 0 for p in ps):
                raise BoundsTransferError("invalid frozen forecast")
        for i, day in enumerate(v21.v20.FUTURE):
            row = by_key[key][day]
            observed = not row["censored"]
            n_obs += observed
            n_cens += not observed
            for name in COMPARATORS:
                item = {"key": str(n_obs + n_cens),
                        "a": predictions[key][CANDIDATE][i],
                        "b": predictions[key][name][i],
                        "observed": observed}
                if observed:
                    item["y"] = row["y"]
                inputs[name].append(item)
    if (n_obs, n_cens) != (original["observed_in_stock_days_scored"],
                            original["censored_stockout_days_excluded"]):
        raise BoundsTransferError("observed/censored denominator drift")
    if n_obs + n_cens != original["expected_future_days"]:
        raise BoundsTransferError("total-day denominator drift")
    results = {}
    for name in COMPARATORS:
        result = bounds.evaluate({"schema": bounds.INPUT_SCHEMA, "cap": None,
                                  "rows": inputs[name]})
        if (result["observed_days"], result["censored_days"]) != (n_obs, n_cens):
            raise BoundsTransferError("bound engine denominator drift")
        expected = (original["models"][CANDIDATE]["day_weighted_mae"] -
                    original["models"][name]["day_weighted_mae"])
        actual = result["observed_only_paired_mae_delta_A_minus_B"]
        if actual is None or not math.isclose(actual, expected, abs_tol=1e-10, rel_tol=0):
            raise BoundsTransferError("observed delta does not reconcile to v2.1")
        results[name] = result
    return results


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if train.resolve() == evaluation.resolve():
        raise BoundsTransferError("TRAIN and EVAL cannot be identical")
    # Hard firewall: no evaluation file access until BOTH original TRAIN-only
    # prediction seals have been independently reconstructed.
    selected, predictions, seal = v21.reproduce_before_labels(train)
    v21.verify_file(evaluation, v21.EVAL_BYTES, v21.EVAL_SHA256)
    rows = list(v21.selected_eval_rows(evaluation, selected))
    original = v21.score_frozen(selected, predictions, rows)
    if ((len(selected), original["expected_future_days"],
         original["observed_in_stock_days_scored"],
         original["censored_stockout_days_excluded"]) != EXPECTED or
        original["decision"] != "PASSED_PREREGISTERED_MAE_GATE" or
        not math.isclose(original["primary_comparison"]["point_delta"],
                         -0.08064779161947905, abs_tol=1e-10, rel_tol=0)):
        raise BoundsTransferError("STOP: original v2.1 evidence did not reconcile")
    secondary = v22.secondary_from_rows(selected, predictions, rows, original)
    if (secondary["decision"] !=
            "EXPLORATORY_INCONCLUSIVE_INTERVAL_INCLUDES_ZERO"):
        raise BoundsTransferError("STOP: original v2.2 result did not reconcile")
    result = score_bounds(selected, predictions, rows, original)
    v21.verify_file(train, v21.TRAIN_BYTES, v21.TRAIN_SHA256)
    v21.verify_file(evaluation, v21.EVAL_BYTES, v21.EVAL_SHA256)
    return {
        "schema": SCHEMA,
        "analysis": "POST_HOC_PUBLIC_LABEL_PARTIAL_IDENTIFICATION_NOT_CONFIRMATORY",
        "source": {"dataset": "Dingdong-Inc/FreshRetailNet-LT",
                   "publisher_revision": v21.v19.REVISION if hasattr(v21.v19, "REVISION")
                   else "01c3bb306415e09d3ccd2fe762f33eb3aeb2affd",
                   "train_sha256": v21.TRAIN_SHA256, "eval_sha256": v21.EVAL_SHA256,
                   "independently_authenticated": False},
        "frozen_prediction_sha256": seal,
        "frozen_cohort_sha256": v21.PINNED_COHORT_SHA256,
        "observed_days": original["observed_in_stock_days_scored"],
        "censored_days": original["censored_stockout_days_excluded"],
        "historical_v21_primary": "PASSED_UNCHANGED",
        "historical_v22_strongest_comparator": "INCONCLUSIVE_UNCHANGED",
        "historical_v15_2024_primary": "FAILED_UNCHANGED",
        "paired_full_period_bounds": result,
        "no_censored_demand_imputed": True,
        "statistical_confidence": "TBD; logical bounds only",
        "latent_demand_truth": "UNAVAILABLE",
        "inventory_decision_value": "TBD",
        "independent_validation": "TBD",
        "maturity_change": "NONE",
        "provenance": {"python": platform.python_version(),
                       "os": platform.system(),
                       "git_checkout": os.environ.get("GITHUB_SHA", "TBD"),
                       "bound_engine_schema": bounds.SCHEMA}
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--train", type=Path, required=True)
    p.add_argument("--eval", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists() or a.output.resolve() in (a.train.resolve(), a.eval.resolve()):
        raise SystemExit("refusing to overwrite evidence or source")
    result = run(a.train, a.eval)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"schema": SCHEMA, "observed_days": result["observed_days"],
                      "censored_days": result["censored_days"],
                      "bounds": {k: {"lower": v["full_period_paired_mae_delta_lower"],
                                      "upper": v["full_period_paired_mae_delta_upper"],
                                      "decision": v["identification_decision"]}
                                 for k, v in result["paired_full_period_bounds"].items()}},
                     sort_keys=True))


if __name__ == "__main__":
    main()
