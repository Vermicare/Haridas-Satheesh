"""Prospective store-disjoint *series* transfer check on the already-known 2024-06-26..07-02 publisher window.

This is NOT a new temporal holdout: the weekday-median comparator was chosen after
results on other stores for these same dates were inspected. This test can assess
cross-store generality, not independently confirm temporal forecasting uplift.
No latent demand or inventory/revenue impact is observed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import official_holdout_v12 as frozen
import weekday_median_v14 as v14
from retail_gate import EvidenceError

EXPERIMENT_ID = "retail-store-disjoint-transfer-v15"
SELECTION_SEED = "retail-store-disjoint-v15-20261027"
SAMPLE_SIZE = 512
ORIGINAL_COHORT_SHA256 = v14.FROZEN_COHORT_SHA256


def digest_cohort(keys):
    return hashlib.sha256(json.dumps(tuple(keys), separators=(",", ":")).encode("utf-8")).hexdigest()


def select_disjoint_training_cohort(train_ids, count=SAMPLE_SIZE):
    """Selection uses TRAIN identifiers only; all original-cohort stores are excluded.

    Never replace a selected series based on EVAL availability or outcomes.
    """
    if type(count) is not int or count < 1:
        raise EvidenceError("invalid predeclared cohort size")
    unique = set(frozen._key(*pair) for pair in train_ids)
    original = frozen.select_train_only(unique)
    if digest_cohort(original) != ORIGINAL_COHORT_SHA256:
        raise EvidenceError("original v1.2 cohort identity changed")
    excluded_stores = {store for store, _ in original}
    eligible = (key for key in unique if key[0] not in excluded_stores)

    def rank(key):
        material = f"{SELECTION_SEED}|{key[0]}|{key[1]}".encode("ascii")
        return hashlib.sha256(material).digest(), key

    new = tuple(sorted(eligible, key=rank)[:count])
    if len(new) != count or {store for store, _ in new} & excluded_stores:
        raise EvidenceError("insufficient store-disjoint training series; do not relax selection")
    return original, new


def interpret_primary_gate(metrics):
    """Predeclared primary comparator: weekday median vs last-observed, store cluster CI."""
    import math

    def finite_number(value):
        # bool is a subclass of int; huge ints may overflow float conversion.
        if type(value) not in (int, float):
            return False
        try:
            return math.isfinite(value)
        except (OverflowError, ValueError):
            return False

    try:
        interval = metrics["weekday_median_minus_last_observed_store_cluster_ci95"]
        weekday = metrics["weekday_median_last4_day_weighted_mae"]
        last = metrics["original_v12_metrics"]["day_weighted_mae"]["last_observed"]
    except (KeyError, TypeError) as exc:
        raise EvidenceError("missing primary-gate evidence") from exc
    if (not isinstance(interval, list) or len(interval) != 2 or
            not all(finite_number(x) for x in interval) or interval[0] > interval[1]):
        raise EvidenceError("invalid primary store-cluster interval")
    if not finite_number(weekday) or not finite_number(last) or weekday < 0 or last < 0:
        raise EvidenceError("invalid primary-gate MAE")
    point_better = weekday < last
    return {
        "predeclared_primary_comparator": "weekday-median minus last-observed per-series MAE, paired store-cluster 95% interval",
        "point_mae_better": bool(point_better),
        "cluster_interval_excludes_zero_in_favorable_direction": bool(interval[1] < 0),
        "conditional_store_transfer_gate_passed": bool(point_better and interval[1] < 0),
        "interpretation_limit": "same previously inspected publisher evaluation dates; not an independent temporal confirmation",
    }


def run(train_path, eval_path):
    train_path, eval_path = Path(train_path), Path(eval_path)
    if frozen.sha256_file(train_path) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256:
        raise EvidenceError("publisher TRAIN hash mismatch")
    if frozen.sha256_file(eval_path) != frozen.EVAL_SHA256:
        raise EvidenceError("publisher EVAL hash mismatch")
    original, new = select_disjoint_training_cohort(frozen.parquet_ids(train_path))
    selected_set = set(new)
    # The evaluation source is not used to choose or replace the new cohort.
    metrics = v14.evaluate_v14(new, frozen.parquet_selected(train_path, selected_set),
                               frozen.parquet_selected(eval_path, selected_set))
    if metrics["original_v12_metrics"]["frozen_train_selected_series"] != SAMPLE_SIZE:
        raise EvidenceError("new cohort scoring denominator changed")
    if metrics["scored_series"] < 2:
        raise EvidenceError("insufficient scored series for cluster uncertainty")
    gate = interpret_primary_gate(metrics)
    if (frozen.sha256_file(train_path) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256 or
            frozen.sha256_file(eval_path) != frozen.EVAL_SHA256):
        raise EvidenceError("publisher source bytes changed during run")
    return {
        "experiment_id": EXPERIMENT_ID,
        "analysis_type": "PROSPECTIVE_STORE_DISJOINT_SERIES_TRANSFER_ON_SEEN_TEMPORAL_HOLDOUT",
        "method_selection": "weekday-median was chosen post-hoc on other stores, same eval dates",
        "publisher_dataset": "Dingdong-Inc/FreshRetailNet-50K",
        "publisher_train_sha256": frozen.PUBLISHER_REPORTED_TRAIN_SHA256,
        "publisher_eval_sha256": frozen.EVAL_SHA256,
        "original_cohort_sha256": digest_cohort(original),
        "new_cohort_sha256": digest_cohort(new),
        "original_cohort_stores": len({s for s, _ in original}),
        "new_cohort_stores": len({s for s, _ in new}),
        "overlapping_stores": 0,
        "train_only_selection_seed": SELECTION_SEED,
        "frozen_comparators": ["weekday_median_last4", *frozen.MODELS],
        "primary_gate": gate,
        "metrics": metrics,
        "latent_demand_ground_truth": "UNAVAILABLE",
        "decision_value_or_revenue_uplift": "TBD",
        "independent_temporal_holdout": "TBD",
        "independent_external_review": "TBD",
        "maturity": "Research / Architecture; unchanged",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--eval", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite existing evidence")
    report = run(args.train, args.eval)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "new_stores": report["new_cohort_stores"],
        "scored_days": report["metrics"]["scored_days"],
        "mae": {
            "weekday_median": report["metrics"]["weekday_median_last4_day_weighted_mae"],
            **report["metrics"]["original_v12_metrics"]["day_weighted_mae"],
        },
        "primary_gate": report["primary_gate"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
