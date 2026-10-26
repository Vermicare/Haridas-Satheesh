"""Exploratory v1.4 weekday-median baseline on the *unchanged* publisher holdout.

This comparator was selected AFTER v1.2 results were visible: it is post-hoc,
not a preregistered or independent held-out experiment. Only observed in-stock
sales are scored; no latent demand or commercial outcome is measured.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import official_holdout_v12 as frozen
from parquet_export import normalized_row
from retail_gate import EvidenceError, forecast_at_origin, parse_row

FROZEN_COHORT_SHA256 = "7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710"
FROZEN_DAYS = 2183
FROZEN_MAE = {
    "last_observed": 0.4785616124599175,
    "seasonal_naive": 0.48518048557031696,
    "causal_stockout_history": 0.4799061814017406,
}
SEED = 20261027
REPS = 2000


def finite_median(values):
    if not values or any(type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in values):
        raise EvidenceError("median requires nonempty finite nonnegative values")
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return float(ordered[n // 2])
    value = ordered[n // 2 - 1] / 2 + ordered[n // 2] / 2
    if not math.isfinite(value):
        raise EvidenceError("nonfinite median")
    return value


def weekday_median_forecast(training, future_days):
    """Frozen 4 most recent uncensored same-weekday sales; no evaluation rows read.

    Fallback: median of uncensored last 14 TRAIN days; then zero if none.
    These choices are exploratory and must not be tuned on the seen holdout.
    """
    if len(training) != 90 or not future_days:
        raise EvidenceError("expected 90 train days and nonempty future date list")
    frozen._strict_series(training, 90, "train")
    if any(type(day) is not dt.date or day <= training[-1]["day"] for day in future_days):
        raise EvidenceError("future dates must follow training")
    if len(set(future_days)) != len(future_days):
        raise EvidenceError("duplicate future day")
    values, fallback_counts = [], {"weekday": 0, "recent14": 0, "zero": 0}
    for day in future_days:
        matching = [r["y"] for r in training if not r["censored"] and r["day"].weekday() == day.weekday()]
        if matching:
            values.append(finite_median(matching[-4:]))
            fallback_counts["weekday"] += 1
            continue
        recent = [r["y"] for r in training[-14:] if not r["censored"]]
        if recent:
            values.append(finite_median(recent))
            fallback_counts["recent14"] += 1
        else:
            values.append(0.0)
            fallback_counts["zero"] += 1
    return values, fallback_counts


def _group(items, selected_set):
    groups = defaultdict(list)
    for i, obj in enumerate(items, 1):
        row = parse_row(normalized_row(obj, i), i)
        key = (int(row["key"][0]), int(row["key"][1]))
        if key not in selected_set:
            raise EvidenceError("noncohort input")
        groups[key].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: r["day"])
    return groups


def store_cluster_ci(pairs, reps=REPS, seed=SEED):
    """Paired series-macro deltas, resampled by store; descriptive, not causal."""
    if type(reps) is not int or reps < 1 or type(seed) is not int:
        raise EvidenceError("invalid bootstrap configuration")
    by_store = defaultdict(list)
    for store, delta in pairs:
        if type(store) is not int or store < 0 or type(delta) not in (int, float) or not math.isfinite(delta):
            raise EvidenceError("invalid store/delta")
        by_store[store].append(delta)
    if len(by_store) < 2:
        return None
    clusters = [(store, len(values), math.fsum(values)) for store, values in sorted(by_store.items())]
    rng = random.Random(seed)
    n = len(clusters)
    estimates = []
    for _ in range(reps):
        chosen = [clusters[rng.randrange(n)] for _ in range(n)]
        estimates.append(math.fsum(s for _, _, s in chosen) / sum(c for _, c, _ in chosen))
    estimates.sort()
    return [frozen.percentile(estimates, 0.025), frozen.percentile(estimates, 0.975)]


def evaluate_v14(selected, train_rows, eval_rows):
    """Fail closed if the original v1.2 cohort/metrics do not reproduce."""
    selected = tuple(selected)
    if not selected or len(set(selected)) != len(selected):
        raise EvidenceError("invalid frozen cohort")
    train_rows, eval_rows = list(train_rows), list(eval_rows)
    original = frozen.evaluate_cohort(selected, train_rows, eval_rows)
    if original["uncensored_eval_days_scored"] != FROZEN_DAYS:
        # Small fictional unit fixtures may use a different count: gate real
        # evidence in run(), not this reusable evaluator.
        pass
    training, evaluation = _group(train_rows, set(selected)), _group(eval_rows, set(selected))
    new_errors, new_macro = [], []
    delta_last, delta_correction = [], []
    fallbacks = {"weekday": 0, "recent14": 0, "zero": 0}
    for key in selected:
        tr, ev = training.get(key, []), evaluation.get(key, [])
        frozen._strict_series(tr, 90, "train")
        frozen._strict_series(ev, 7, "eval")
        frozen.validate_publisher_split([r["day"].isoformat() for r in tr],
                                        [r["day"].isoformat() for r in ev],
                                        fitted_dates=[r["day"].isoformat() for r in tr])
        if tr[0]["day"] != dt.date(2024, 3, 28) or ev[0]["day"] != dt.date(2024, 6, 26):
            raise EvidenceError("unexpected official calendar")
        candidate, counts = weekday_median_forecast(tr, [r["day"] for r in ev])
        for name, count in counts.items():
            fallbacks[name] += count
        prior = forecast_at_origin(tr + ev, 90)
        observable = [i for i, r in enumerate(ev) if not r["censored"]]
        if not observable:
            continue
        err = [abs(candidate[i] - ev[i]["y"]) for i in observable]
        last_err = [abs(prior["last_observed"][i] - ev[i]["y"]) for i in observable]
        correction_err = [abs(prior["causal_stockout_history"][i] - ev[i]["y"]) for i in observable]
        if any(not math.isfinite(x) for x in err + last_err + correction_err):
            raise EvidenceError("nonfinite held-out error")
        new_errors.extend(err)
        new_macro.append(math.fsum(err) / len(err))
        delta_last.append((key[0], math.fsum(err) / len(err) - math.fsum(last_err) / len(last_err)))
        delta_correction.append((key[0], math.fsum(err) / len(err) - math.fsum(correction_err) / len(correction_err)))
    if not new_errors or len(new_errors) != original["uncensored_eval_days_scored"]:
        raise EvidenceError("changed scoring denominator")
    return {
        "original_v12_metrics": original,
        "weekday_median_last4_day_weighted_mae": math.fsum(new_errors) / len(new_errors),
        "weekday_median_last4_series_macro_mae": math.fsum(new_macro) / len(new_macro),
        "weekday_median_minus_last_observed_series_macro_delta": math.fsum(d for _, d in delta_last) / len(delta_last),
        "weekday_median_minus_correction_series_macro_delta": math.fsum(d for _, d in delta_correction) / len(delta_correction),
        "weekday_median_minus_last_observed_store_cluster_ci95": store_cluster_ci(delta_last),
        "weekday_median_minus_correction_store_cluster_ci95": store_cluster_ci(delta_correction),
        "training_only_fallback_counts_all_7day_predictions": fallbacks,
        "scored_series": len(new_macro),
        "scored_days": len(new_errors),
    }


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if frozen.sha256_file(train) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256:
        raise EvidenceError("pinned train hash mismatch")
    if frozen.sha256_file(evaluation) != frozen.EVAL_SHA256:
        raise EvidenceError("pinned eval hash mismatch")
    selected = frozen.select_train_only(frozen.parquet_ids(train))
    cohort_sha = hashlib.sha256(json.dumps(selected, separators=(",", ":")).encode()).hexdigest()
    if cohort_sha != FROZEN_COHORT_SHA256:
        raise EvidenceError("frozen cohort hash mismatch")
    result = evaluate_v14(selected, frozen.parquet_selected(train, set(selected)),
                          frozen.parquet_selected(evaluation, set(selected)))
    original = result["original_v12_metrics"]
    if original["uncensored_eval_days_scored"] != FROZEN_DAYS:
        raise EvidenceError("original v1.2 scored-day mismatch")
    for name, expected in FROZEN_MAE.items():
        if not math.isclose(original["day_weighted_mae"][name], expected, abs_tol=1e-10, rel_tol=0):
            raise EvidenceError("original v1.2 MAE changed")
    if frozen.sha256_file(train) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256 or frozen.sha256_file(evaluation) != frozen.EVAL_SHA256:
        raise EvidenceError("source changed during evaluation")
    return {
        "experiment_id": "retail-exploratory-weekday-median-v14",
        "analysis_type": "POST_HOC_BASELINE_ADDED_AFTER_V12_HOLDOUT_RESULTS_KNOWN",
        "dataset": "Dingdong-Inc/FreshRetailNet-50K",
        "cohort_sha256": cohort_sha,
        "publisher_train_sha256_verified": frozen.PUBLISHER_REPORTED_TRAIN_SHA256,
        "publisher_eval_sha256_verified": frozen.EVAL_SHA256,
        "method": "last four uncensored training observations on matching weekday; fallback last14 uncensored then zero",
        "metrics": result,
        "latent_demand_ground_truth": "UNAVAILABLE",
        "inventory_or_revenue_impact": "TBD",
        "independent_external_validation": "TBD",
        "maturity": "Research / Architecture — unchanged",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--eval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite evidence")
    report = run(args.train, args.eval)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    m = report["metrics"]
    print(json.dumps({"experiment_id": report["experiment_id"], "scored_days": m["scored_days"],
                      "weekday_median_mae": m["weekday_median_last4_day_weighted_mae"],
                      "original_mae": m["original_v12_metrics"]["day_weighted_mae"],
                      "store_cluster_ci95_vs_last": m["weekday_median_minus_last_observed_store_cluster_ci95"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
