#!/usr/bin/env python3
"""Exhaustive fictional carryover sensitivity for six-block cooling order designs.

This does not contain or authenticate any physical instrument measurements.
"""
from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from statistics import mean

from order_confounding_v1 import CONDITIONS, SEED, balanced_orders, simulate

VERSION = 'cooling-order-carryover-sensitivity-v2'


def analyze(carryover_c: float) -> dict:
    """Enumerate all 6! orderings of the six distinct three-condition blocks.

    Model assumes an additive one-slot carryover from the previous prototype,
    a global linear drift, 10-minute slots and zero actual treatment effect.
    Block boundaries do NOT reset the hypothetical carryover.
    """
    if type(carryover_c) not in (float, int) or not math.isfinite(carryover_c):
        raise ValueError('finite numeric carryover required')
    six_orders = list(itertools.permutations(CONDITIONS))
    comparisons = ('prototype_minus_ambient_c', 'prototype_minus_fan_only_c')
    values = {key: [] for key in comparisons}
    for order in itertools.permutations(six_orders):
        result = simulate(list(order), carryover_after_prototype_c=carryover_c)
        values['prototype_minus_ambient_c'].append(result['prototype_minus_ambient_c'])
        values['prototype_minus_fan_only_c'].append(
            result['means_c']['prototype'] - result['means_c']['fan_only'])
    seed_result = simulate(balanced_orders(SEED),
                           carryover_after_prototype_c=carryover_c)
    seeded = {
        'prototype_minus_ambient_c': seed_result['prototype_minus_ambient_c'],
        'prototype_minus_fan_only_c': (seed_result['means_c']['prototype'] -
                                       seed_result['means_c']['fan_only']),
    }
    def summary(numbers):
        # Round only for grouping to suppress floating-point subtraction noise;
        # exact unrounded min/max and seed result are also reported.
        frequencies = Counter(f'{x:+.6f}' for x in (round(v, 6) for v in numbers))
        return {'min_c': min(numbers), 'max_c': max(numbers),
                'mean_c': mean(numbers),
                'zero_bias_schedule_count': sum(abs(x) < 1e-9 for x in numbers),
                'rounded_bias_histogram': dict(sorted(frequencies.items()))}
    return {'schema_version': VERSION, 'assumed_carryover_c': carryover_c,
            'assumed_true_prototype_effect_c': 0.0,
            'assumed_linear_drift_c_per_min': -0.02,
            'assumed_slot_min': 10.0,
            'block_boundary_carryover_resets': False,
            'unique_balanced_block_orderings': math.factorial(6),
            'bias_by_comparator': {key: summary(values[key]) for key in comparisons},
            'seed': SEED, 'seeded_order_bias_c': seeded,
            'physical_measurements': 0, 'physical_origin_authenticated': False,
            'performance_claim_permitted': False}


def main():
    print(json.dumps({'scenarios': [analyze(-0.6), analyze(0.0), analyze(0.6)],
                      'interpretation': 'FICTIONAL one-slot carryover sensitivity only; do not select a favorable schedule post hoc; measure stabilization/washout before causal inference.'},
                     sort_keys=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
