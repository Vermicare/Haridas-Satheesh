#!/usr/bin/env python3
"""Synthetic-only stress diagnostic for WBI; no EEG or safety validation.

The existing frozen evaluator and coverage diagnostic are imported unchanged.
Every threshold is calibrated independently within its regime and seed pair;
held-out labels, risk, and coverage never enter selection.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import random

from synthetic_evaluator import fixture
from coverage_target_diagnostic import run, TARGETS, TEST_COVERAGE_TOLERANCE

# Fixed before interpreting any outcomes; no adaptive seed search.
SEED_PAIRS = ((1103, 2103), (1117, 2117), (1129, 2129), (1143, 2143), (1151, 2151))
REGIMES = ("original", "permuted", "inverted", "constant")
ROWS_PER_SPLIT = 240
FROZEN_EVALUATOR_BLOB = "2becec81a8002cc5ff2f445889b7617baf9937b9"


def transform(rows, regime: str, seed: int):
    """Alter only fictional drift score, never label, probability, or segment."""
    if regime not in REGIMES:
        raise ValueError(f"unknown regime: {regime}")
    if regime == "original":
        return list(rows)
    if regime == "permuted":
        scores = [r.drift for r in rows]
        random.Random(seed).shuffle(scores)
    elif regime == "inverted":
        scores = [1.0 - r.drift for r in rows]
    else:
        scores = [0.5] * len(rows)
    return [replace(r, drift=s) for r, s in zip(rows, scores)]


def summarize(cases):
    """Aggregate ONLY declared comparable synthetic test points."""
    out = {}
    for regime in REGIMES:
        subset = [x for x in cases if x["regime"] == regime]
        compared = [x for x in subset if x["comparable"]]
        deltas = [x["gate_minus_confidence_risk"] for x in compared]
        if any(x is None for x in deltas):
            raise ValueError("comparable case without a risk delta")
        if any(x["gate_minus_confidence_risk"] is not None for x in subset if not x["comparable"]):
            raise ValueError("unmatched coverage was assigned a risk delta")
        out[regime] = {
            "cases": len(subset),
            "comparable": len(compared),
            "excluded_coverage_mismatch_or_zero_actions": len(subset) - len(compared),
            "gate_worse": sum(d > 0 for d in deltas),
            "gate_better": sum(d < 0 for d in deltas),
            "ties": sum(d == 0 for d in deltas),
            "mean_gate_minus_confidence_risk": round(sum(deltas) / len(deltas), 6) if deltas else None,
        }
    return out


def experiment():
    cases = []
    for cal_seed, test_seed in SEED_PAIRS:
        cal_base = fixture(cal_seed, ROWS_PER_SPLIT)
        test_base = fixture(test_seed, ROWS_PER_SPLIT)
        for regime in REGIMES:
            cal = transform(cal_base, regime, cal_seed + 9000)
            test = transform(test_base, regime, test_seed + 9000)
            result = run(cal, test, targets=TARGETS)
            for point in result["results"]:
                cases.append({
                    "calibration_seed": cal_seed,
                    "test_seed": test_seed,
                    "regime": regime,
                    "target": point["target_calibration_coverage"],
                    "comparable": point["within_test_coverage_tolerance"],
                    "held_out_coverage_gap": round(point["test_coverage_gap"], 6),
                    "gate_minus_confidence_risk": (
                        round(point["gate_minus_confidence_risk"], 6)
                        if point["gate_minus_confidence_risk"] is not None else None
                    ),
                    "confidence": point["policies"]["confidence"]["test"],
                    "gate": point["policies"]["gate"]["test"],
                    "calibration_selection": {
                        policy: point["policies"][policy]["selection"]
                        for policy in ("confidence", "gate")
                    },
                })
    return {
        "scope": "FICTIONAL SYNTHETIC DATA ONLY; NOT EEG, CLINICAL OR DEVICE VALIDATION",
        "frozen_evaluator_git_blob": FROZEN_EVALUATOR_BLOB,
        "method": "original coverage-target diagnostic, no edits to frozen evaluator",
        "seed_pairs": [list(x) for x in SEED_PAIRS],
        "regimes": list(REGIMES),
        "regime_definitions": {
            "original": "original seeded synthetic drift scores",
            "permuted": "shuffle scores within split without using labels; preserve score multiset",
            "inverted": "replace drift score with 1-score",
            "constant": "set every drift score to 0.5",
        },
        "rows_per_split": ROWS_PER_SPLIT,
        "targets": list(TARGETS),
        "absolute_test_coverage_tolerance": TEST_COVERAGE_TOLERANCE,
        "selection_boundary": "per-case thresholds use calibration probabilities/drift only; test labels are held out",
        "limitations": "Fixed small fictional seed set; regimes reuse base rows and are correlated; "
                       "no confidence intervals, statistical superiority, capacity matching, or public EEG evidence; "
                       "coverage mismatches excluded, not imputed.",
        "summary": summarize(cases),
        "cases": cases,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("synthetic_regime_stress.json"))
    args = p.parse_args()
    report = experiment()
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "
", encoding="utf-8")
    for regime, result in report["summary"].items():
        print(f"FICTIONAL {regime}: {result['comparable']}/{result['cases']} comparable; "
              f"gate better/worse/tie={result['gate_better']}/{result['gate_worse']}/{result['ties']}; "
              f"mean risk delta={result['mean_gate_minus_confidence_risk']}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
