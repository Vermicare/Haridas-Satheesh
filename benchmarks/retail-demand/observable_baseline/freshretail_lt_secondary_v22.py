"""Exploratory v2.2 strongest-simple-comparator sensitivity on SEEN public 2025 labels.

NOT a new holdout, preregistration, independent validation or promotion of a model.
Never export raw publisher rows, series identifiers, forecasts or residuals.
The original v2.1 primary decision is immutable and must reconcile exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
from collections import defaultdict
from pathlib import Path

import freshretail_lt_score_v21 as v21
from parquet_export import normalized_row
from retail_gate import parse_row
from store_cluster_day_weighted_v17 import paired_store_cluster_day_ci

REPS = 2000
SEED = 20261029
CANDIDATE = "weekday_median_last4"
COMPARATOR = "causal_stockout_history"


class SecondaryError(ValueError):
    pass


def secondary_from_rows(selected, predictions, evaluation_rows, original):
    """Use identical in-stock day-weighted estimand and whole-store resampling."""
    if original["selected_series"] != len(selected) or original["missing_future_days"] != 0:
        raise SecondaryError("original scorer/cohort mismatch")
    by_key = defaultdict(dict)
    for index, raw in enumerate(evaluation_rows, 1):
        key = v21.v19.key_of(raw)
        if key not in predictions:
            raise SecondaryError("noncohort evaluation row")
        row = parse_row(normalized_row(raw, index), index)
        if row["day"] not in v21.v20.FUTURE or row["day"] in by_key[key]:
            raise SecondaryError("duplicate or out-of-horizon evaluation date")
        by_key[key][row["day"]] = row
    records = []
    days = 0
    for key in selected:
        rows = by_key.get(key, {})
        if set(rows) != set(v21.v20.FUTURE):
            raise SecondaryError("incomplete evaluation horizon")
        if set(predictions[key]) != set(v21.METHODS):
            raise SecondaryError("changed model set")
        indices = [i for i, day in enumerate(v21.v20.FUTURE) if not rows[day]["censored"]]
        if not indices:
            continue
        errors = {}
        for method in (CANDIDATE, COMPARATOR):
            forecast = predictions[key][method]
            if len(forecast) != 7 or any(
                type(p) not in (int, float) or not math.isfinite(p) or p < 0
                for p in forecast
            ):
                raise SecondaryError("invalid frozen forecast")
            errors[method] = math.fsum(
                abs(forecast[i] - rows[v21.v20.FUTURE[i]]["y"]) for i in indices
            )
        days += len(indices)
        records.append((key[0], key[1], len(indices),
                        errors[CANDIDATE], errors[COMPARATOR]))
    if days != original["observed_in_stock_days_scored"]:
        raise SecondaryError("observed-day denominator drift")
    if len(records) != original["scored_series"]:
        raise SecondaryError("scored-series denominator drift")
    if len({r[0] for r in records}) != original["scored_store_count"]:
        raise SecondaryError("scored-store denominator drift")
    if len({r[0] for r in records}) < 2:
        return {"decision": "INCONCLUSIVE_TOO_FEW_STORES", "comparison": None}
    ci = paired_store_cluster_day_ci(records, reps=REPS, seed=SEED)
    expected = (original["models"][CANDIDATE]["day_weighted_mae"] -
                original["models"][COMPARATOR]["day_weighted_mae"])
    if not math.isclose(ci["point_delta"], expected, rel_tol=0, abs_tol=1e-10):
        raise SecondaryError("secondary point estimate disagrees with frozen v2.1 metrics")
    ci["estimand"] = "EXPLORATORY 2025 in-stock day-weighted weekday minus causal-stockout-history MAE"
    ci["statistical_limit"] = (
        "Post-hoc secondary comparison on ALREADY OPENED public 2025 labels; "
        "same publisher; 50%+ days stockout-censored; no multiplicity correction, "
        "independent-publisher evidence, lost-demand truth or decision value."
    )
    decision = ("EXPLORATORY_INTERVAL_EXCLUDES_ZERO_FAVORS_WEEKDAY" if ci["store_cluster_ci95"][1] < 0
                else "EXPLORATORY_INTERVAL_EXCLUDES_ZERO_FAVORS_CAUSAL" if ci["store_cluster_ci95"][0] > 0
                else "EXPLORATORY_INCONCLUSIVE_INTERVAL_INCLUDES_ZERO")
    return {"decision": decision, "comparison": ci}


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if train.resolve() == evaluation.resolve():
        raise SecondaryError("TRAIN and EVAL cannot be the same file")
    selected, predictions, seal = v21.reproduce_before_labels(train)
    # Only after the original TRAIN-only prediction SHA-256 is independently matched.
    v21.verify_file(evaluation, v21.EVAL_BYTES, v21.EVAL_SHA256)
    rows = list(v21.selected_eval_rows(evaluation, selected))
    original = v21.score_frozen(selected, predictions, rows)
    if (original["selected_series"] != 512 or original["expected_future_days"] != 3584 or
            original["observed_in_stock_days_scored"] != 1766 or
            original["censored_stockout_days_excluded"] != 1818 or
            original["decision"] != "PASSED_PREREGISTERED_MAE_GATE" or
            not math.isclose(original["primary_comparison"]["point_delta"],
                             -0.08064779161947905, abs_tol=1e-10, rel_tol=0)):
        raise SecondaryError("STOP: original v2.1 primary evidence does not reconcile")
    secondary = secondary_from_rows(selected, predictions, rows, original)
    v21.verify_file(train, v21.TRAIN_BYTES, v21.TRAIN_SHA256)
    v21.verify_file(evaluation, v21.EVAL_BYTES, v21.EVAL_SHA256)
    return {
        "experiment": "retail-lt-v22-exploratory-strongest-simple-comparator",
        "analysis": "POST_HOC_ALREADY_SEEN_PUBLIC_2025_LABELS_NOT_CONFIRMATORY",
        "frozen_prediction_sha256": seal,
        "frozen_cohort_sha256": v21.PINNED_COHORT_SHA256,
        "source_train_sha256": v21.TRAIN_SHA256,
        "source_eval_sha256": v21.EVAL_SHA256,
        "original_v21_primary_gate": "PASSED_UNCHANGED",
        "original_v15_2024_primary_gate": "FAILED_UNCHANGED",
        "scored_in_stock_days": original["observed_in_stock_days_scored"],
        "stockout_censored_days": original["censored_stockout_days_excluded"],
        "exploratory_secondary": secondary,
        "latent_demand_truth": "UNAVAILABLE",
        "inventory_decision_value": "TBD",
        "independent_validation": "TBD",
        "maturity_change": "NONE",
        "provenance": {"python": platform.python_version(), "os": platform.system(),
                       "git_checkout": os.environ.get("GITHUB_SHA", "TBD"),
                       "bootstrap_reps": REPS, "bootstrap_seed": SEED}
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--eval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() in (args.train.resolve(), args.eval.resolve()):
        raise SystemExit("refusing to overwrite existing evidence or input")
    result = run(args.train, args.eval)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps({"experiment": result["experiment"],
                      "secondary": result["exploratory_secondary"],
                      "original_primary": result["original_v21_primary_gate"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
