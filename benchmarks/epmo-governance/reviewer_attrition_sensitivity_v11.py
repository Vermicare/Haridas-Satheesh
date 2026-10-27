#!/usr/bin/env python3
"""FICTIONAL sensitivity of reviewer-level permutation inference to selective attrition.

No participants, actual reviews, employer information, or external actions.
All numbers are explicitly hypothetical, not efficacy or sample-size evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import random

SEED = 20261027
CASES = 13
REVIEWERS_PER_ARM = 48
REPLICATIONS = 1000
PERMUTATIONS = 199
ALPHA = 0.05
ICC = 0.10
SCENARIOS = (
    "null_complete",
    "null_random_25pct",
    "null_selective_treatment_dropout",
    "hypothetical_effect_complete",
)


def reviewer_rate(rng: random.Random, probability: float, icc: float = ICC) -> float:
    if not (math.isfinite(probability) and 0 < probability < 1 and
            math.isfinite(icc) and 0 <= icc < 1):
        raise ValueError("probability and ICC must be finite and in bounds")
    if icc:
        concentration = (1 / icc) - 1
        probability = rng.betavariate(probability * concentration,
                                     (1 - probability) * concentration)
    return sum(rng.random() < probability for _ in range(CASES)) / CASES


def retained(rng: random.Random, scenario: str, arm: str, rate: float) -> bool:
    """Explicit toy missingness rules; high-risk dropout is outcome-dependent."""
    if scenario in ("null_complete", "hypothetical_effect_complete"):
        return True
    if scenario == "null_random_25pct":
        return rng.random() >= 0.25
    if scenario == "null_selective_treatment_dropout":
        # Selection on potential error rate AFTER fictional decisions.
        dropout = 0.80 if arm == "treatment" and rate >= (4 / CASES) else 0.05
        return rng.random() >= dropout
    raise ValueError("unknown scenario")


def permutation_pvalue(control: list[float], treatment: list[float],
                       rng: random.Random, permutations: int = PERMUTATIONS) -> float:
    if (not control or not treatment or type(permutations) is not int or
            permutations < 19 or any(not math.isfinite(x) or not 0 <= x <= 1
                                     for x in control + treatment)):
        raise ValueError("invalid complete-case data or permutation count")
    n = len(control)
    m = len(treatment)
    combined = list(control) + list(treatment)
    observed = abs(sum(control) / n - sum(treatment) / m)
    extreme = 0
    for _ in range(permutations):
        rng.shuffle(combined)
        delta = abs(sum(combined[:n]) / n - sum(combined[n:]) / m)
        extreme += delta + 1e-12 >= observed
    return (extreme + 1) / (permutations + 1)


def run(seed: int = SEED, replications: int = REPLICATIONS,
        permutations: int = PERMUTATIONS,
        reviewers_per_arm: int = REVIEWERS_PER_ARM) -> dict:
    if (type(seed) is not int or type(replications) is not int or
            replications < 20 or type(permutations) is not int or
            permutations < 19 or type(reviewers_per_arm) is not int or
            reviewers_per_arm < 12):
        raise ValueError("invalid simulation parameters")
    rng = random.Random(seed)
    results = []
    for scenario in SCENARIOS:
        rejected = 0
        total_control_retained = total_treatment_retained = 0
        summed_observed_difference = 0.0
        for _ in range(replications):
            treatment_probability = 0.10 if scenario == "hypothetical_effect_complete" else 0.20
            control = [reviewer_rate(rng, 0.20) for _ in range(reviewers_per_arm)]
            treatment = [reviewer_rate(rng, treatment_probability) for _ in range(reviewers_per_arm)]
            observed_control = [x for x in control if retained(rng, scenario, "control", x)]
            observed_treatment = [x for x in treatment if retained(rng, scenario, "treatment", x)]
            # No imputation: this is deliberately the potentially biased complete-case analysis.
            if not observed_control or not observed_treatment:
                raise ValueError("all reviewers missing in an arm")
            total_control_retained += len(observed_control)
            total_treatment_retained += len(observed_treatment)
            summed_observed_difference += (sum(observed_treatment) / len(observed_treatment)
                                           - sum(observed_control) / len(observed_control))
            rejected += permutation_pvalue(observed_control, observed_treatment,
                                           rng, permutations) <= ALPHA
        p = rejected / replications
        results.append({
            "scenario": scenario,
            "null_true": scenario != "hypothetical_effect_complete",
            "rejections": rejected,
            "estimated_rejection_probability": round(p, 4),
            "monte_carlo_standard_error": round(math.sqrt(p * (1 - p) / replications), 4),
            "mean_observed_treatment_minus_control": round(summed_observed_difference / replications, 4),
            "mean_control_retained": round(total_control_retained / replications, 2),
            "mean_treatment_retained": round(total_treatment_retained / replications, 2),
        })
    return {
        "origin": "FICTIONAL_ASSUMPTION_BASED_SIMULATION",
        "version": "1.1",
        "seed": seed,
        "cases_per_reviewer": CASES,
        "reviewers_assigned_per_arm": reviewers_per_arm,
        "within_reviewer_icc_assumed": ICC,
        "replications": replications,
        "permutations": permutations,
        "alpha_two_sided": ALPHA,
        "missingness_rules": {
            "null_complete": "none",
            "null_random_25pct": "25% independent dropout in each arm",
            "null_selective_treatment_dropout": "treatment: 80% dropout if >=4/13 fictional false approvals, else 5%; control: 5% dropout",
            "hypothetical_effect_complete": "none; assumed treatment probability 0.10 versus control 0.20",
        },
        "results": results,
        "observed_human_participants": 0,
        "observed_effect": "TBD",
        "external_actions": 0,
        "decision": "Illustrates complete-case selection bias under hypothetical missing-not-at-random; not observed human evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--replications", type=int, default=REPLICATIONS)
    parser.add_argument("--permutations", type=int, default=PERMUTATIONS)
    parser.add_argument("--reviewers-per-arm", type=int, default=REVIEWERS_PER_ARM)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.replications, args.permutations,
                         args.reviewers_per_arm), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
