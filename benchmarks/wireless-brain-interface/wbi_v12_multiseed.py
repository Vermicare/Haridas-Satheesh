#!/usr/bin/env python3
"""Exploratory synthetic-only multi-seed stress test of WBI v1.1 top-k.

No EEG, no online authorization, no prospective validation. Imports the
unchanged evaluator only after its Git blob is checked by the v1.1 loader.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median
from wbi_matched_coverage_v11 import (
    frozen_module, choose_alpha, select_indices, wrong_acted, ALPHAS
)

SEED_START = 100000
PAIRS = 200
N = 240
BUDGET = 0.50


def run(frozen, pairs=PAIRS):
    if pairs <= 0:
        raise ValueError("pairs must be positive")
    records = []
    for i in range(pairs):
        cal_seed, test_seed = SEED_START + 2*i, SEED_START + 2*i + 1
        cal, test = frozen.fixture(cal_seed, N), frozen.fixture(test_seed, N)
        k = round(BUDGET * N)
        alpha = choose_alpha(cal, k, frozen.pred_conf)
        baseline = wrong_acted(
            test, select_indices(test, k, 0.0, frozen.pred_conf), frozen.pred_conf
        )
        drift = wrong_acted(
            test, select_indices(test, k, alpha, frozen.pred_conf), frozen.pred_conf
        )
        records.append({
            "pair": i, "cal_seed": cal_seed, "test_seed": test_seed,
            "alpha": alpha, "baseline_wrong": baseline, "drift_wrong": drift,
            "delta_wrong": drift-baseline
        })
    ds = [r["delta_wrong"] for r in records]
    return {
        "status": "EXPLORATORY_SYNTHETIC_ONLY",
        "protocol": {
            "pairs": pairs, "seed_start": SEED_START,
            "cal_seed_formula": "100000+2*i",
            "test_seed_formula": "100001+2*i",
            "n_per_split": N, "budget_fraction": BUDGET,
            "k": round(BUDGET*N), "alpha_grid": list(ALPHAS),
            "alpha_calibration_only": True, "post_hoc_design": True,
            "real_eeg": "NOT_TESTED", "online_policy": "NOT_TESTED"
        },
        "aggregate": {
            "mean_delta_wrong": mean(ds), "median_delta_wrong": median(ds),
            "total_baseline_wrong": sum(r["baseline_wrong"] for r in records),
            "total_drift_wrong": sum(r["drift_wrong"] for r in records),
            "drift_better_pairs": sum(d < 0 for d in ds),
            "tie_pairs": sum(d == 0 for d in ds),
            "drift_worse_pairs": sum(d > 0 for d in ds),
            "selected_alphas": dict(sorted(Counter(str(r["alpha"]) for r in records).items())),
            "min_delta_wrong": min(ds), "max_delta_wrong": max(ds)
        },
        "records": records
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frozen", type=Path,
        default=Path(__file__).with_name("synthetic_evaluator.py")
    )
    parser.add_argument("--pairs", type=int, default=PAIRS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    obj = run(frozen_module(args.frozen), args.pairs)
    payload = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError("Refusing to overwrite results")
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
