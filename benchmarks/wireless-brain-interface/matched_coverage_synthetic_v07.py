#!/usr/bin/env python3
"""WBI v0.7: held-out, exact-coverage synthetic drift-feature falsification.

No EEG is loaded. Original frozen synthetic evaluator is imported, never changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random

import synthetic_evaluator as frozen

ORIGINAL_BLOB = "2becec81a8002cc5ff2f445889b7617baf9937b9"
WEIGHTS = (0.0, 0.1, 0.25, 0.5, 1.0)
N = 240
ACT = 120
REPS = 12
INCREMENT = 1009


class GateError(ValueError):
    pass


def frozen_identity():
    raw = Path(frozen.__file__).read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw).hexdigest()
    if git_blob != ORIGINAL_BLOB:
        raise GateError("original frozen evaluator source changed; abort")
    return {"git_blob": git_blob, "sha256": hashlib.sha256(raw).hexdigest()}


def rank_actions(rows, weight, count=ACT):
    """Choose actions using only confidence, drift and stable row index; NO labels."""
    if not 0 <= count <= len(rows) or not math.isfinite(weight) or weight < 0:
        raise GateError("invalid action count or weight")
    scores = []
    for i, row in enumerate(rows):
        _, confidence = frozen.pred_conf(row)
        if not (math.isfinite(confidence) and math.isfinite(row.drift)
                and 0 <= row.drift <= 1):
            raise GateError("nonfinite or invalid decision feature")
        scores.append((-(confidence - weight * row.drift), i))
    return frozenset(i for _, i in sorted(scores)[:count])


def wrong_count(rows, selected):
    if any(i < 0 or i >= len(rows) for i in selected):
        raise GateError("invalid selected index")
    return sum(frozen.pred_conf(rows[i])[0] != rows[i].y for i in selected)


def choose_weight(calibration):
    """Calibration-only labels; test rows are never passed to this function."""
    if len(calibration) != N:
        raise GateError("invalid calibration fixture size")
    candidates = [(wrong_count(calibration, rank_actions(calibration, w)), w)
                  for w in WEIGHTS]
    return min(candidates)[1]


def permute_test_drift(test, seed):
    """Break drift/label association; preserve test labels, confidence and drift multiset."""
    drift = [row.drift for row in test]
    random.Random(seed).shuffle(drift)
    return [frozen.Row(row.y, row.p1, d, row.segment)
            for row, d in zip(test, drift)]


def evaluate_pair(test, weight):
    baseline = rank_actions(test, 0.0)
    candidate = rank_actions(test, weight)
    if len(baseline) != ACT or len(candidate) != ACT:
        raise GateError("coverage mismatch")
    b, c = wrong_count(test, baseline), wrong_count(test, candidate)
    return {"baseline_incorrect": b, "candidate_incorrect": c,
            "candidate_minus_baseline_incorrect": c - b,
            "baseline_risk": b / ACT, "candidate_risk": c / ACT,
            "acted_each": ACT, "total": len(test),
            "coverage_each": ACT / len(test),
            "different_action_decisions": len(baseline ^ candidate)}


def run():
    source = frozen_identity()
    records = []
    for i in range(REPS):
        cal_seed = frozen.SEED_CAL + i * INCREMENT
        test_seed = frozen.SEED_TEST + i * INCREMENT
        cal = frozen.fixture(cal_seed, N)
        test = frozen.fixture(test_seed, N)
        weight = choose_weight(cal)
        normal = evaluate_pair(test, weight)
        stress = evaluate_pair(permute_test_drift(test, test_seed + 777), weight)
        records.append({"replicate": i, "calibration_seed": cal_seed,
                        "test_seed": test_seed, "calibration_selected_weight": weight,
                        "held_out": normal, "permuted_test_drift": stress})
    deltas = [r["held_out"]["candidate_minus_baseline_incorrect"] for r in records]
    stressed = [r["permuted_test_drift"]["candidate_minus_baseline_incorrect"]
                for r in records]
    return {
        "experiment": "wbi-v07-exact-coverage-synthetic-drift-falsification",
        "evidence_class": "FICTIONAL_SYNTHETIC_ONLY_NOT_EEG",
        "stage": "Research / Simulation (unchanged)",
        "source": source,
        "protocol": {"replicates": REPS, "fixture_rows_per_split": N,
                     "actions_per_policy": ACT, "coverage": ACT / N,
                     "candidate_weights": list(WEIGHTS), "seed_increment": INCREMENT,
                     "weight_selection": "minimum calibration incorrect count; smallest weight on ties",
                     "test_label_used_for_selection": False,
                     "stress": "fixed test-only drift permutation; no recalibration"},
        "replicates": records,
        "aggregate": {
            "held_out_candidate_minus_baseline_total_incorrect": sum(deltas),
            "held_out_candidate_wins_ties_losses": [sum(d < 0 for d in deltas),
                                                     sum(d == 0 for d in deltas),
                                                     sum(d > 0 for d in deltas)],
            "permuted_drift_candidate_minus_baseline_total_incorrect": sum(stressed),
            "permuted_drift_candidate_wins_ties_losses": [sum(d < 0 for d in stressed),
                                                         sum(d == 0 for d in stressed),
                                                         sum(d > 0 for d in stressed)],
            "denominator_actions_each": ACT * REPS,
        },
        "limitations": {"real_eeg": "TBD", "matched_coverage_real_eeg": "TBD",
                        "clinical_safety": "TBD", "independent_external_review": "TBD",
                        "causal_drift_benefit": "NOT_ESTABLISHED",
                        "statistical_significance": "NOT_TESTED",
                        "maturity_advanced": False},
        "provenance": {"python": platform.python_version(), "os": platform.system(),
                       "git_checkout": os.environ.get("GITHUB_SHA", "TBD"),
                       "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite evidence")
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                     allow_nan=False) + "\\n", encoding="utf-8", newline="\\n")
    print(json.dumps({"experiment": result["experiment"],
                      "aggregate": result["aggregate"],
                      "evidence_class": result["evidence_class"]}, sort_keys=True))


if __name__ == "__main__":
    main()
