#!/usr/bin/env python3
"""Synthetic-only, calibration-selected WBI coverage-target diagnostic.

The original frozen evaluator is imported but never changed. Coverage-target
thresholds are chosen using calibration p1/drift only, without reading labels.
This is NOT a capacity-matched or EEG validation and does not establish benefit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from synthetic_evaluator import (
    CONF_THRESHOLDS, DRIFT_THRESHOLDS, SEED_CAL, SEED_TEST,
    confidence_policy, fixture, gate_policy, pred_conf,
)

TARGETS = (0.30, 0.50, 0.70)
TEST_COVERAGE_TOLERANCE = 0.05
FROZEN_EVALUATOR_GIT_BLOB = "2becec81a8002cc5ff2f445889b7617baf9937b9"


def coverage(actions: list[bool]) -> float:
    if not actions:
        raise ValueError("empty calibration or evaluation rows")
    return sum(actions) / len(actions)


def choose_thresholds(cal, target: float, policy: str):
    """Coverage-only calibration. No y label, segment, or test data is inspected."""
    if not 0 < target <= 1:
        raise ValueError("target coverage must be in (0, 1]")
    if not cal:
        raise ValueError("calibration rows required")
    if policy == "confidence":
        candidates = [((c, None), confidence_policy(cal, c)) for c in CONF_THRESHOLDS]
    elif policy == "gate":
        candidates = [((c, d), gate_policy(cal, c, d))
                      for c in CONF_THRESHOLDS for d in DRIFT_THRESHOLDS]
    else:
        raise ValueError("unknown policy")
    # Deterministic tie-breaker: favor higher drift allowance, then higher
    # confidence threshold. This is a declared engineering convention, not an
    # empirical optimization of safety or correctness.
    (c, d), acted = min(candidates, key=lambda item: (
        abs(coverage(item[1]) - target),
        -(item[0][1] if item[0][1] is not None else 1.0),
        -item[0][0],
    ))
    return {"confidence_threshold": c, "drift_threshold": d,
            "calibration_coverage": coverage(acted)}


def evaluate(rows, acted):
    if len(rows) != len(acted) or not rows:
        raise ValueError("row/action mismatch or empty evaluation")
    n = sum(acted)
    wrong = sum(a and pred_conf(r)[0] != r.y for r, a in zip(rows, acted))
    correct = sum(a and pred_conf(r)[0] == r.y for r, a in zip(rows, acted))
    return {"n": len(rows), "acted": n, "incorrect": wrong, "correct": correct,
            "coverage": n / len(rows), "incorrect_action_risk": wrong / n if n else None}


def run(cal, test, targets=TARGETS):
    if not cal or not test:
        raise ValueError("nonempty calibration and test required")
    results = []
    for target in targets:
        configs = {p: choose_thresholds(cal, target, p) for p in ("confidence", "gate")}
        policies = {}
        for p, conf in configs.items():
            actions = (confidence_policy(test, conf["confidence_threshold"])
                       if p == "confidence" else gate_policy(
                           test, conf["confidence_threshold"], conf["drift_threshold"]))
            policies[p] = {
                "selection": conf,
                "test": evaluate(test, actions),
                "nominal": evaluate([r for r in test if r.segment == "nominal"],
                                    [a for r, a in zip(test, actions) if r.segment == "nominal"]),
                "drift": evaluate([r for r in test if r.segment == "drift"],
                                  [a for r, a in zip(test, actions) if r.segment == "drift"]),
            }
        a = policies["confidence"]["test"]
        b = policies["gate"]["test"]
        gap = abs(a["coverage"] - b["coverage"])
        comparable = gap <= TEST_COVERAGE_TOLERANCE and a["acted"] > 0 and b["acted"] > 0
        results.append({
            "target_calibration_coverage": target,
            "test_coverage_gap": gap,
            "within_test_coverage_tolerance": comparable,
            "gate_minus_confidence_risk":
                b["incorrect_action_risk"] - a["incorrect_action_risk"] if comparable else None,
            "policies": policies,
        })
    return {
        "scope": "FICTIONAL SYNTHETIC DATA ONLY; NOT EEG, CLINICAL, DEVICE OR SAFETY VALIDATION",
        "frozen_evaluator_git_blob": FROZEN_EVALUATOR_GIT_BLOB,
        "calibration_seed": SEED_CAL, "test_seed": SEED_TEST,
        "calibration_rows": len(cal), "test_rows": len(test),
        "selection": "coverage-only, calibration p1/drift; no labels or test inputs",
        "test_coverage_tolerance_absolute": TEST_COVERAGE_TOLERANCE,
        "limitation": "Coarse threshold grids; matched test coverage is not guaranteed. "
                      "No paired statistical uncertainty or model-capacity matching. "
                      "The synthetic drift score is artificial; no public EEG tested.",
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("coverage_target_results.json"))
    args = parser.parse_args()
    data = run(fixture(SEED_CAL), fixture(SEED_TEST))
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    for item in data["results"]:
        c = item["policies"]["confidence"]["test"]
        g = item["policies"]["gate"]["test"]
        print(f"synthetic target={item['target_calibration_coverage']:.2f} "
              f"confidence={c['coverage']:.3f}/{c['incorrect_action_risk']:.3f} "
              f"gate={g['coverage']:.3f}/{g['incorrect_action_risk']:.3f} "
              f"coverage_comparable={item['within_test_coverage_tolerance']}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
