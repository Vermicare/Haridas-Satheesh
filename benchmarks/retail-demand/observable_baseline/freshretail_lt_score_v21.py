"""FreshRetailNet-LT v2.1: independent prediction re-seal BEFORE EVAL-label parsing.

Public publisher data; no employer data. No raw rows, series IDs or predictions
are written. An unchanged TRAIN-only SHA commitment is a hard precondition.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform

import freshretail_lt_prediction_seal_v20 as v20
import freshretail_lt_train_cohort_v19 as v19
from freshretail_lt_source_gate_v18 import (
    EVAL_BYTES, EVAL_SHA256, TRAIN_BYTES, TRAIN_SHA256, verify_file,
)
from parquet_export import normalized_row
from retail_gate import EvidenceError, forecast_at_origin, parse_row
from store_cluster_day_weighted_v17 import paired_store_cluster_day_ci
from weekday_median_v14 import _group, weekday_median_forecast

PINNED_PREDICTION_SHA256 = "5c21bce8c9a436ecc0d3173128b0812e4408cc025558faedc2ed0e3497a54e20"
PINNED_COHORT_SHA256 = "dc128d3bed90035214c80529bf58e685ad7d49c717d95bd10c30c2b9407ca016"
EVAL_FIELDS = v20.PREDICTION_FIELDS
METHODS = v20.MODELS


class ScoreError(ValueError):
    pass


def reproduce_before_labels(train):
    """Rebuild the v2.0 seal; independently reassemble per-series predictions.

    Does not accept or open any evaluation file. Abort on any drift.
    """
    sealed = v20.run(train)
    if (sealed["prediction_sha256"] != PINNED_PREDICTION_SHA256 or
            sealed["cohort"]["selected_cohort_sha256"] != PINNED_COHORT_SHA256 or
            sealed["evaluation_labels_read"] is not False):
        raise ScoreError("STOP: original TRAIN-only prediction seal mismatch")
    selected, cohort = v20.training_cohort(v19.parquet_rows(train))
    if cohort["selected_cohort_sha256"] != PINNED_COHORT_SHA256:
        raise ScoreError("STOP: independently regenerated cohort differs")
    grouped = _group(v20.parquet_selected_training(train, set(selected)), set(selected))
    predictions = {}
    digest = hashlib.sha256()
    for key in selected:
        history = grouped.get(key, [])
        if (len(history) != v19.DAYS or
                [r["day"] for r in history] !=
                [v19.START + dt.timedelta(days=i) for i in range(v19.DAYS)]):
            raise ScoreError("STOP: selected TRAIN history changed")
        original = forecast_at_origin(history + [{"day": d} for d in v20.FUTURE], v19.DAYS)
        weekday, _ = weekday_median_forecast(history, list(v20.FUTURE))
        forecasts = {**original, "weekday_median_last4": weekday}
        if set(forecasts) != set(METHODS):
            raise ScoreError("STOP: frozen method names changed")
        payload = {"series": list(key),
                   "future_dates": [d.isoformat() for d in v20.FUTURE],
                   "predictions": {name: forecasts[name] for name in METHODS}}
        digest.update(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                 allow_nan=False).encode("ascii") + b"\n")
        predictions[key] = forecasts
    if digest.hexdigest() != PINNED_PREDICTION_SHA256:
        raise ScoreError("STOP: independent prediction reconstruction differs")
    verify_file(Path(train), TRAIN_BYTES, TRAIN_SHA256)
    return selected, predictions, digest.hexdigest()


def selected_eval_rows(evaluation, selected):
    """Read only selected public EVAL series, after the caller verifies the seal."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    pqfile = pq.ParquetFile(evaluation)
    if not set(EVAL_FIELDS).issubset(pqfile.schema_arrow.names):
        raise ScoreError("EVAL lacks frozen hourly fields")
    chosen = set(selected)
    for batch in pqfile.iter_batches(batch_size=8192, columns=list(EVAL_FIELDS)):
        keys = zip(batch.column(0).to_pylist(), batch.column(1).to_pylist())
        indices = [i for i, key in enumerate(keys) if key in chosen]
        if indices:
            yield from batch.take(pa.array(indices, type=pa.int32())).to_pylist()


def score_frozen(selected, predictions, eval_rows):
    """Fail closed on missing/duplicate future dates; never replace TRAIN cohort."""
    if not selected or len(selected) != len(set(selected)) or set(selected) != set(predictions):
        raise ScoreError("invalid frozen selected cohort or predictions")
    by_key = defaultdict(dict)
    for i, raw in enumerate(eval_rows, 1):
        key = v19.key_of(raw)
        if key not in predictions:
            raise ScoreError("noncohort row supplied to scorer")
        row = parse_row(normalized_row(raw, i), i)
        day = row["day"]
        if day not in v20.FUTURE:
            raise ScoreError("selected EVAL date outside frozen seven-day horizon")
        if day in by_key[key]:
            raise ScoreError("duplicate selected EVAL day")
        by_key[key][day] = row
    total_days = 0
    censored = 0
    observed = 0
    error_sums = {name: [] for name in METHODS}
    signed_sums = {name: [] for name in METHODS}
    macro = {name: [] for name in METHODS}
    records = []
    scored_stores = set()
    total_stores = set()
    products = set()
    for key in selected:
        total_stores.add(key[0])
        products.add(key[1])
        rows = by_key.get(key, {})
        if set(rows) != set(v20.FUTURE):
            raise ScoreError("STOP: selected EVAL missing future days; no replacement")
        if set(predictions[key]) != set(METHODS):
            raise ScoreError("changed forecast methods")
        for name in METHODS:
            vals = predictions[key][name]
            if (len(vals) != 7 or any(type(v) not in (int, float)
                                     or not math.isfinite(v) or v < 0 for v in vals)):
                raise ScoreError("nonfinite or invalid sealed prediction")
        valid = [i for i, day in enumerate(v20.FUTURE) if not rows[day]["censored"]]
        total_days += 7
        censored += 7 - len(valid)
        observed += len(valid)
        if not valid:
            continue
        scored_stores.add(key[0])
        series_abs = {}
        for name in METHODS:
            errs = [abs(predictions[key][name][i] - rows[v20.FUTURE[i]]["y"])
                    for i in valid]
            signed = [predictions[key][name][i] - rows[v20.FUTURE[i]]["y"]
                      for i in valid]
            if any(not math.isfinite(x) for x in errs + signed):
                raise ScoreError("nonfinite forecast error")
            total = math.fsum(errs)
            series_abs[name] = total
            error_sums[name].append(total)
            signed_sums[name].append(math.fsum(signed))
            macro[name].append(total / len(valid))
        records.append((key[0], key[1], len(valid),
                        series_abs["weekday_median_last4"],
                        series_abs["last_observed"]))
    if total_days != len(selected) * 7 or observed + censored != total_days:
        raise ScoreError("EVAL denominator mismatch")
    denominator = math.fsum(
        by_key[key][day]["y"] for key in selected for day in v20.FUTURE
        if not by_key[key][day]["censored"]
    )
    metrics = {}
    for name in METHODS:
        metrics[name] = {
            "day_weighted_mae": math.fsum(error_sums[name]) / observed if observed else "TBD",
            "series_macro_mae": math.fsum(macro[name]) / len(macro[name]) if macro[name] else "TBD",
            "wape": math.fsum(error_sums[name]) / denominator if denominator > 0 else "TBD",
            "wpe_forecast_minus_observed": math.fsum(signed_sums[name]) / denominator if denominator > 0 else "TBD",
        }
    ci = None
    decision = "INCONCLUSIVE_NO_IN_STOCK_DAYS"
    if observed and len(scored_stores) >= 2:
        ci = paired_store_cluster_day_ci(records, reps=2000, seed=20261028)
        expected = (metrics["weekday_median_last4"]["day_weighted_mae"]
                    - metrics["last_observed"]["day_weighted_mae"])
        if not math.isclose(ci["point_delta"], expected, rel_tol=0, abs_tol=1e-10):
            raise ScoreError("point estimate and cluster interval estimands differ")
        decision = ("PASSED_PREREGISTERED_MAE_GATE" if
                    expected < 0 and ci["store_cluster_ci95"][1] < 0
                    else "FAILED_PREREGISTERED_MAE_SUPERIORITY_GATE")
    elif observed:
        decision = "INCONCLUSIVE_TOO_FEW_SCORED_STORES"
    if ci is not None:
        ci["statistical_limit"] = ("public-label 2025 temporal transfer from same publisher; "
                                   "not blinded, independent-publisher or causal validation")
    return {
        "decision": decision,
        "primary_comparison": ci,
        "models": metrics,
        "selected_series": len(selected),
        "selected_store_count": len(total_stores),
        "selected_product_count": len(products),
        "scored_series": len(records),
        "scored_store_count": len(scored_stores),
        "expected_future_days": total_days,
        "observed_in_stock_days_scored": observed,
        "censored_stockout_days_excluded": censored,
        "missing_future_days": 0,
        "opportunity_ranking_ground_truth": "TBD",
        "latent_demand_truth": "UNAVAILABLE",
        "inventory_or_revenue_uplift": "TBD",
        "maturity_change": "NONE",
    }


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if train.resolve() == evaluation.resolve():
        raise ScoreError("TRAIN and EVAL must be distinct files")
    selected, predictions, commitment = reproduce_before_labels(train)
    # This is the first EVAL file access: hash bytes, then parse labels.
    source = verify_file(evaluation, EVAL_BYTES, EVAL_SHA256)
    result = score_frozen(selected, predictions, selected_eval_rows(evaluation, selected))
    verify_file(train, TRAIN_BYTES, TRAIN_SHA256)
    verify_file(evaluation, EVAL_BYTES, EVAL_SHA256)
    import pyarrow
    return {
        "experiment": "retail-lt-v21-presealed-2025-temporal-transfer",
        "analysis": "PREREGISTERED_PUBLIC_LABEL_TEMPORAL_TRANSFER_SAME_PUBLISHER",
        "train_only_prediction_seal_regenerated_before_eval_labels": True,
        "original_and_independent_prediction_sha256": commitment,
        "cohort_sha256": PINNED_COHORT_SHA256,
        "source": {"dataset": "Dingdong-Inc/FreshRetailNet-LT",
                   "publisher_revision": "01c3bb306415e09d3ccd2fe762f33eb3aeb2affd",
                   "train_sha256": TRAIN_SHA256, "eval_sha256": source["sha256"],
                   "publisher_authenticity_independently_attested": False},
        "result": result,
        "prior_2024_v15_superiority_gate": "FAILED_UNCHANGED",
        "provenance": {"python": platform.python_version(),
                       "pyarrow": pyarrow.__version__,
                       "runner_os": platform.system(),
                       "git_checkout": os.environ.get("GITHUB_SHA", "TBD")},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--eval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() in (args.train.resolve(), args.eval.resolve()):
        raise SystemExit("refusing to overwrite source or existing evidence")
    report = run(args.train, args.eval)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8", newline="\n")
    r = report["result"]
    print(json.dumps({"decision": r["decision"], "observed_in_stock_days": r["observed_in_stock_days_scored"],
                      "selected_series": r["selected_series"],
                      "prediction_seal": report["original_and_independent_prediction_sha256"],
                      "primary_comparison": r["primary_comparison"]}, sort_keys=True))


if __name__ == "__main__":
    main()
