#!/usr/bin/env python3
"""Fictional EPMO reviewer attrition: sharp no-assumption missing-outcome bounds.

No participants, employers, outreach, private keys, external actions or real review outcomes.
Reviewer is the unit; each *completed* fictional reviewer decides 13 oracle-negative cases.
"""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction

from reviewer_attrition_sensitivity_v11 import CASES, retained, reviewer_rate

SEED = 20261028
ASSIGNED_PER_ARM = 48
SCENARIOS = ("null_random_25pct", "null_selective_treatment_dropout")


def rational(value: Fraction) -> dict[str, str]:
    return {"exact": f"{value.numerator}/{value.denominator}",
            "decimal": f"{float(value):.6f}"}


def arm_bounds(assigned: int, observed_false_counts: list[int]) -> dict:
    """Sharp finite-sample bounds, assuming every unobserved review rate is in [0,1]."""
    if type(assigned) is not int or assigned <= 0 or type(observed_false_counts) is not list:
        raise ValueError("assigned must be positive int; counts must be a list")
    if len(observed_false_counts) > assigned:
        raise ValueError("more completed reviewers than assigned")
    if any(type(x) is not int or x < 0 or x > CASES for x in observed_false_counts):
        raise ValueError("each completed reviewer must have 0..13 false approvals")
    completed = len(observed_false_counts)
    missing = assigned - completed
    total = sum(observed_false_counts)
    # Each completed reviewer's outcome is a rate in [0,1]. Missing outcomes can
    # be zero or one. No missing-at-random assumption and no imputed values.
    lower = Fraction(total, CASES * assigned)
    upper = Fraction(total + CASES * missing, CASES * assigned)
    observed = Fraction(total, CASES * completed) if completed else None
    return {
        "assigned": assigned, "completed": completed, "missing": missing,
        "observed_false_approvals": total,
        "complete_case_rate": rational(observed) if observed is not None else None,
        "assigned_mean_lower": rational(lower),
        "assigned_mean_upper": rational(upper),
    }


def contrast_bounds(control: dict, treatment: dict) -> dict:
    def exact(item: dict, field: str) -> Fraction:
        n, d = item[field]["exact"].split("/")
        return Fraction(int(n), int(d))
    lo = exact(treatment, "assigned_mean_lower") - exact(control, "assigned_mean_upper")
    hi = exact(treatment, "assigned_mean_upper") - exact(control, "assigned_mean_lower")
    observed = None
    if control["complete_case_rate"] is not None and treatment["complete_case_rate"] is not None:
        observed = exact(treatment, "complete_case_rate") - exact(control, "complete_case_rate")
    return {
        "direction": "worksheet_minus_manual; negative means fewer false approvals",
        "complete_case_difference": rational(observed) if observed is not None else None,
        "assigned_difference_lower": rational(lo),
        "assigned_difference_upper": rational(hi),
        "zero_in_identification_interval": lo <= 0 <= hi,
        "interval_type": "sharp no-assumption finite-sample identification bounds; NOT a confidence interval",
    }


def fictional_scenario(seed: int, scenario: str, assigned: int = ASSIGNED_PER_ARM) -> dict:
    if type(seed) is not int or type(assigned) is not int or assigned <= 0 or scenario not in SCENARIOS:
        raise ValueError("invalid seed, scenario, or assigned count")
    rng = random.Random(seed)
    # Both arms share the same fictional true-null outcome distribution (p=.20).
    # The missingness mechanism is intentionally outcome-dependent in one arm.
    full_control = [round(CASES * reviewer_rate(rng, 0.20)) for _ in range(assigned)]
    full_treatment = [round(CASES * reviewer_rate(rng, 0.20)) for _ in range(assigned)]
    observed_control = [x for x in full_control if retained(rng, scenario, "control", x / CASES)]
    observed_treatment = [x for x in full_treatment if retained(rng, scenario, "treatment", x / CASES)]
    control = arm_bounds(assigned, observed_control)
    treatment = arm_bounds(assigned, observed_treatment)
    # Reproducibility fingerprint of *fictional* observed counts, without exposing
    # reviewer-level records in the public result. No private identifiers exist.
    fixture = {"manual": observed_control, "worksheet": observed_treatment}
    digest = hashlib.sha256(json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"scenario": scenario, "observed_fixture_sha256": digest,
            "manual": control, "worksheet": treatment,
            "contrast": contrast_bounds(control, treatment)}


def run(seed: int = SEED, assigned: int = ASSIGNED_PER_ARM) -> dict:
    return {
        "origin": "FICTIONAL_ASSUMPTION_BASED_MISSINGNESS_PREFLIGHT",
        "version": "1.2", "seed": seed, "assigned_per_arm": assigned,
        "cases_per_completed_reviewer": CASES,
        "assumed_true_null_false_approval_probability": "0.20 in both arms",
        "generator": "reviewer_attrition_sensitivity_v11.reviewer_rate and retained",
        "assumed_reviewer_icc": "0.10 (from v1.1)",
        "scenarios": [fictional_scenario(seed + i, name, assigned) for i, name in enumerate(SCENARIOS)],
        "observed_human_reviewers": 0, "human_treatment_effect": "TBD",
        "actual_completion_rates": "TBD", "external_actions": 0,
        "decision": "Do not claim an assigned-reviewer benefit from complete cases when worst-case bounds include zero; predefine missingness before any private pilot.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
