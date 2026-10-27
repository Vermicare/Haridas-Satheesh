#!/usr/bin/env python3
"""Fictional reviewer-level power sensitivity, not human-study evidence.

No participant records, real outcomes, public identities, or external actions.
The model is beta-binomial: 13 negative cases/reviewer, assumed baseline
false-approval probability and within-reviewer intraclass correlation.
"""
from __future__ import annotations
import argparse
import json
import math
import random

SEED = 20261027
NEGATIVE_CASES = 13
ARM_SIZES = (12, 24, 48, 96)
REPLICATIONS = 400
PERMUTATIONS = 199
ALPHA = 0.05
SCENARIOS = (("null", 0.20, 0.20), ("ten_point_reduction", 0.20, 0.10))
RHO = 0.10


def reviewer_rate(rng, probability, rho=RHO):
    if not (0 < probability < 1 and 0 <= rho < 1):
        raise ValueError("invalid model parameters")
    if rho:
        concentration = 1.0 / rho - 1.0
        probability = rng.betavariate(probability * concentration,
                                     (1.0 - probability) * concentration)
    return sum(rng.random() < probability for _ in range(NEGATIVE_CASES)) / NEGATIVE_CASES


def permutation_pvalue(control, treatment, rng, permutations=PERMUTATIONS):
    """Two-sided Monte Carlo randomization test at the reviewer level."""
    if not control or not treatment or type(permutations) is not int or permutations < 19:
        raise ValueError("need nonempty arms and >=19 permutations")
    n = len(control)
    combined = list(control) + list(treatment)
    observed = abs(sum(control) / n - sum(treatment) / len(treatment))
    exceed = 0
    for _ in range(permutations):
        rng.shuffle(combined)
        difference = abs(sum(combined[:n]) / n - sum(combined[n:]) / len(treatment))
        if difference + 1e-12 >= observed:
            exceed += 1
    return (1 + exceed) / (1 + permutations)


def run(seed=SEED, replications=REPLICATIONS, permutations=PERMUTATIONS):
    if type(seed) is not int or type(replications) is not int or replications < 20:
        raise ValueError("invalid seed/replications")
    rng = random.Random(seed)
    results = []
    for scenario, baseline, treatment in SCENARIOS:
        for n in ARM_SIZES:
            discoveries = 0
            for _ in range(replications):
                control_rates = [reviewer_rate(rng, baseline) for _ in range(n)]
                treatment_rates = [reviewer_rate(rng, treatment) for _ in range(n)]
                discoveries += permutation_pvalue(control_rates, treatment_rates, rng, permutations) <= ALPHA
            proportion = discoveries / replications
            results.append({"scenario": scenario, "reviewers_per_arm": n,
                            "rejections": discoveries, "replications": replications,
                            "estimated_rejection_probability": round(proportion, 4),
                            "monte_carlo_se": round(math.sqrt(proportion * (1 - proportion) / replications), 4)})
    return {"origin": "FICTIONAL_ASSUMPTION_BASED_SIMULATION", "version": "1.0",
            "seed": seed, "negative_cases_per_reviewer": NEGATIVE_CASES,
            "within_reviewer_icc_assumed": RHO, "alpha_two_sided": ALPHA,
            "replications": replications, "permutations_per_replication": permutations,
            "test": "reviewer-level two-sided Monte Carlo permutation; (1+extreme)/(1+permutations)",
            "scenarios": [{"name": name, "control_probability": a,
                           "worksheet_probability": b} for name, a, b in SCENARIOS],
            "results": results, "observed_human_participants": 0,
            "observed_effect": "TBD", "external_actions": 0,
            "decision": "Planning sensitivity only; no efficacy or study-power guarantee"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--replications", type=int, default=REPLICATIONS)
    parser.add_argument("--permutations", type=int, default=PERMUTATIONS)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.replications, args.permutations), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
