#!/usr/bin/env python3
"""Exploratory matched-budget diagnostic of unchanged WBI synthetic fixture.

Post-hoc fictional-data analysis only. Not EEG or an online authorization policy.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

FROZEN_BLOB = "2becec81a8002cc5ff2f445889b7617baf9937b9"
ALPHAS = (0.0, 0.05, 0.10, 0.20, 0.40, 0.80)
BUDGETS = (0.25, 0.50, 0.75)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def frozen_module(path: Path):
    raw = path.read_bytes()
    observed = git_blob(raw)
    if observed != FROZEN_BLOB:
        raise ValueError(f"Frozen evaluator blob mismatch: {observed}; expected {FROZEN_BLOB}")
    spec = importlib.util.spec_from_file_location("synthetic_evaluator", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load frozen evaluator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def select_indices(rows, k: int, alpha: float, pred_conf):
    """Select top-k using unlabeled confidence and drift; stable index ties."""
    if not (0 < k <= len(rows)):
        raise ValueError("k must be in [1,n]")
    if alpha < 0:
        raise ValueError("alpha must be nonnegative")
    return tuple(sorted(sorted(range(len(rows)),
                        key=lambda i: (-(pred_conf(rows[i])[1] - alpha * rows[i].drift), i))[:k]))


def wrong_acted(rows, chosen, pred_conf):
    return sum(pred_conf(rows[i])[0] != rows[i].y for i in chosen)


def score(rows, chosen, pred_conf):
    k = len(chosen)
    wrong = wrong_acted(rows, chosen, pred_conf)
    correct_total = sum(pred_conf(r)[0] == r.y for r in rows)
    return {"acted": k, "incorrect_acted": wrong,
            "incorrect_action_risk": wrong / k,
            "correct_action_retention": (k - wrong) / correct_total if correct_total else None}


def choose_alpha(cal, k, pred_conf):
    # Calibration labels only; smallest alpha wins a tie.
    return min(ALPHAS, key=lambda a: (wrong_acted(cal, select_indices(cal, k, a, pred_conf), pred_conf), a))


def experiment(frozen):
    cal = frozen.fixture(frozen.SEED_CAL)
    test = frozen.fixture(frozen.SEED_TEST)
    if len(cal) != 240 or len(test) != 240:
        raise ValueError("Unexpected frozen fixture row count")
    results = []
    for fraction in BUDGETS:
        k_cal = round(fraction * len(cal))
        k_test = round(fraction * len(test))
        alpha = choose_alpha(cal, k_cal, frozen.pred_conf)
        baseline = select_indices(test, k_test, 0.0, frozen.pred_conf)
        gate = select_indices(test, k_test, alpha, frozen.pred_conf)
        b = score(test, baseline, frozen.pred_conf)
        g = score(test, gate, frozen.pred_conf)
        results.append({"budget_fraction": fraction, "calibration_selected_alpha": alpha,
                        "baseline": b, "drift_aware": g,
                        "risk_delta_drift_minus_confidence": g["incorrect_action_risk"] - b["incorrect_action_risk"],
                        "test_label_count_used_for_selection": 0})
    return {"status": "exploratory_synthetic_only", "frozen_evaluator_git_blob": FROZEN_BLOB,
            "calibration_seed": frozen.SEED_CAL, "test_seed": frozen.SEED_TEST,
            "alpha_candidates": ALPHAS,
            "tie_rule": "prefer smallest alpha on equal calibration errors; stable index on score ties",
            "warning": "Post-hoc exploratory; top-k test feature ranks require whole test cohort; not online, EEG, or preregistered evidence.",
            "budgets": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", type=Path, default=Path(__file__).with_name("synthetic_evaluator.py"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    obj = experiment(frozen_module(args.frozen))
    data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
