#!/usr/bin/env python3
"""Fictional-only order-confounding demonstration for cooling comparisons.

No physical observations, cooling efficacy, safety, or instrument authentication.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import defaultdict

CONDITIONS = ('ambient', 'fan_only', 'prototype')
VERSION = 'cooling-order-confounding-v1'
SEED = 20261027


def balanced_orders(seed: int = SEED) -> list[tuple[str, ...]]:
    """One of each of the six 3-condition orders, shuffled reproducibly."""
    orders = list(itertools.permutations(CONDITIONS))
    random.Random(seed).shuffle(orders)
    return orders


def fixed_orders() -> list[tuple[str, ...]]:
    return [CONDITIONS] * 6


def simulate(orders: list[tuple[str, ...]], *, baseline_c: float = 30.0,
             drift_c_per_min: float = -0.02, slot_min: float = 10.0,
             prototype_effect_c: float = 0.0,
             carryover_after_prototype_c: float = 0.0) -> dict:
    """Exact deterministic illustrative temperatures at trial midpoints.

    A treatment's fictional effect is added to a global linear temperature trend.
    Carryover (if requested) affects the immediately subsequent slot.
    """
    if len(orders) != 6 or any(sorted(o) != sorted(CONDITIONS) for o in orders):
        raise ValueError('six complete 3-condition blocks required')
    if slot_min <= 0:
        raise ValueError('slot_min must be positive')
    rows = []
    previous = None
    for block, order in enumerate(orders, start=1):
        for slot, condition in enumerate(order, start=1):
            index = (block - 1) * 3 + slot - 1
            midpoint_min = (index + 0.5) * slot_min
            carry = carryover_after_prototype_c if previous == 'prototype' else 0.0
            temp = (baseline_c + drift_c_per_min * midpoint_min
                    + (prototype_effect_c if condition == 'prototype' else 0.0)
                    + carry)
            rows.append({'block': block, 'slot': slot, 'condition': condition,
                         'midpoint_min': midpoint_min, 'fictional_temp_c': temp})
            previous = condition
    by_condition = defaultdict(list)
    for row in rows:
        by_condition[row['condition']].append(row['fictional_temp_c'])
    means = {condition: sum(by_condition[condition]) / len(by_condition[condition])
             for condition in CONDITIONS}
    return {'schema_version': VERSION, 'rows': rows, 'means_c': means,
            'prototype_minus_ambient_c': means['prototype'] - means['ambient'],
            'physical_measurements': 0, 'performance_claim_permitted': False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=SEED)
    args = parser.parse_args()
    fixed = simulate(fixed_orders())
    balanced = simulate(balanced_orders(args.seed))
    print(json.dumps({'schema_version': VERSION, 'seed': args.seed,
                      'assumptions': {'baseline_c': 30.0, 'linear_drift_c_per_min': -0.02,
                                      'slot_min': 10.0, 'true_treatment_effect_c': 0.0,
                                      'carryover_c': 0.0},
                      'fixed': fixed, 'balanced': balanced,
                      'physical_measurements': 0, 'performance_claim_permitted': False},
                     sort_keys=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
