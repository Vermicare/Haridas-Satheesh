#!/usr/bin/env python3
"""Synthetic-only WBI v1.3 drift-feature permutation controls.

Preserves frozen evaluator and v1.1/v1.2 implementations. This is a
post-hoc cohort top-k diagnostic, NOT EEG or online authorization evidence.
"""
from __future__ import annotations
import argparse
import json
import random
from dataclasses import replace
from pathlib import Path
from statistics import median
from wbi_matched_coverage_v11 import frozen_module, choose_alpha, select_indices, wrong_acted
from wbi_v12_multiseed import PAIRS, N, SEED_START


def permute_drift(rows, seed):
    values = [r.drift for r in rows]
    random.Random(seed).shuffle(values)
    return [replace(r, drift=v) for r, v in zip(rows, values)]


def evaluate(frozen, pairs=PAIRS):
    if not 1 <= pairs <= 10000:
        raise ValueError("pairs must be in 1..10000")
    cases = {"informative_original": [], "permuted_both": [], "permuted_test_only": []}
    for i in range(pairs):
        cal = frozen.fixture(SEED_START + 2*i, N)
        test = frozen.fixture(SEED_START + 2*i + 1, N)
        k = N // 2
        base = wrong_acted(test, select_indices(test, k, 0.0, frozen.pred_conf), frozen.pred_conf)
        cal_perm = permute_drift(cal, 700000 + 2*i)
        test_perm = permute_drift(test, 700000 + 2*i + 1)
        for key, c, t in (
            ("informative_original", cal, test),
            ("permuted_both", cal_perm, test_perm),
            ("permuted_test_only", cal, test_perm),
        ):
            alpha = choose_alpha(c, k, frozen.pred_conf)
            wrong = wrong_acted(t, select_indices(t, k, alpha, frozen.pred_conf), frozen.pred_conf)
            cases[key].append({"pair": i, "alpha": alpha, "baseline_wrong": base,
                               "candidate_wrong": wrong, "delta_wrong": wrong-base})
    out = {}
    for name, rows in cases.items():
        ds = [r["delta_wrong"] for r in rows]
        out[name] = {"total_baseline_wrong": sum(r["baseline_wrong"] for r in rows),
                     "total_candidate_wrong": sum(r["candidate_wrong"] for r in rows),
                     "delta_wrong": sum(ds), "median_paired_delta_wrong": median(ds),
                     "better": sum(d<0 for d in ds), "tied": sum(d==0 for d in ds),
                     "worse": sum(d>0 for d in ds),
                     "alpha_zero_pairs": sum(r["alpha"]==0 for r in rows),
                     "records": rows}
    return {"evidence_class": "FICTIONAL_SYNTHETIC_ONLY",
            "design": "Post-hoc fixed-seed permutation sensitivity; not prospective or inferential EEG evidence",
            "seed_start": SEED_START, "pairs": pairs, "n_test_per_pair": N,
            "acted_per_pair": N//2, "permutation_seed_start": 700000,
            "labels_changed": False, "confidence_changed": False,
            "source_evaluator_git_blob": "2becec81a8002cc5ff2f445889b7617baf9937b9",
            "cases": out}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frozen", type=Path, default=Path(__file__).with_name("synthetic_evaluator.py"))
    p.add_argument("--pairs", type=int, default=PAIRS)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = evaluate(frozen_module(args.frozen), args.pairs)
    payload = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError("Refusing to overwrite existing output")
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
