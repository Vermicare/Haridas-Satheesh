#!/usr/bin/env python3
"""WBI v1.4: repeated fictional drift-permutation sensitivity.

Exploratory, post-hoc, fixed-cohort top-k only. No EEG, online safety or
inferential permutation test. Frozen original evaluator is never edited.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from statistics import median
from wbi_matched_coverage_v11 import frozen_module, choose_alpha, select_indices, wrong_acted
from wbi_v12_multiseed import PAIRS, N, SEED_START
from wbi_v13_drift_negative_controls import permute_drift

FROZEN_BLOB = '2becec81a8002cc5ff2f445889b7617baf9937b9'
PERMUTATION_START = 1_400_000
PERMUTATION_STRIDE = 20_000


def evaluate(frozen, pairs=PAIRS, repeats=8):
    if type(pairs) is not int or not 1 <= pairs <= 1000:
        raise ValueError('pairs must be integer 1..1000')
    if type(repeats) is not int or not 2 <= repeats <= 100:
        raise ValueError('repeats must be integer 2..100')
    if pairs * repeats > 4000:
        raise ValueError('work budget exceeded')
    k = N // 2
    per_repeat = [dict(repeat=j, baseline_wrong=0, both_wrong=0,
                       test_only_wrong=0, both_better=0, both_tied=0,
                       both_worse=0, test_only_better=0, test_only_tied=0,
                       test_only_worse=0, both_alpha_zero=0) for j in range(repeats)]
    baseline_total = original_total = original_better = original_tied = original_worse = 0
    for i in range(pairs):
        cal = frozen.fixture(SEED_START + 2*i, N)
        test = frozen.fixture(SEED_START + 2*i + 1, N)
        if len(cal) != N or len(test) != N:
            raise ValueError('unexpected fixture length')
        base = wrong_acted(test, select_indices(test, k, 0.0, frozen.pred_conf), frozen.pred_conf)
        alpha_original = choose_alpha(cal, k, frozen.pred_conf)
        original = wrong_acted(test, select_indices(test, k, alpha_original, frozen.pred_conf), frozen.pred_conf)
        baseline_total += base
        original_total += original
        original_better += original < base
        original_tied += original == base
        original_worse += original > base
        for j, r in enumerate(per_repeat):
            seed = PERMUTATION_START + PERMUTATION_STRIDE*j + 2*i
            cal_perm = permute_drift(cal, seed)
            test_perm = permute_drift(test, seed + 1)
            alpha_both = choose_alpha(cal_perm, k, frozen.pred_conf)
            both = wrong_acted(test_perm, select_indices(test_perm, k, alpha_both, frozen.pred_conf), frozen.pred_conf)
            test_only = wrong_acted(test_perm, select_indices(test_perm, k, alpha_original, frozen.pred_conf), frozen.pred_conf)
            r['baseline_wrong'] += base
            r['both_wrong'] += both
            r['test_only_wrong'] += test_only
            r['both_better'] += both < base
            r['both_tied'] += both == base
            r['both_worse'] += both > base
            r['test_only_better'] += test_only < base
            r['test_only_tied'] += test_only == base
            r['test_only_worse'] += test_only > base
            r['both_alpha_zero'] += alpha_both == 0
    for r in per_repeat:
        r['both_delta_wrong'] = r['both_wrong'] - r['baseline_wrong']
        r['test_only_delta_wrong'] = r['test_only_wrong'] - r['baseline_wrong']
    both = [r['both_delta_wrong'] for r in per_repeat]
    test_only = [r['test_only_delta_wrong'] for r in per_repeat]
    return {
        'evidence_class': 'FICTIONAL_SYNTHETIC_ONLY',
        'stage': 'Research / Simulation',
        'design': 'Post-hoc repeated deterministic drift permutations, fixed synthetic rows and 50% cohort top-k budget; descriptive sensitivity only, not a statistical permutation test',
        'source_evaluator_git_blob': FROZEN_BLOB,
        'pairs': pairs, 'repeats': repeats, 'test_rows_per_pair': N,
        'actions_per_pair': k, 'labels_or_confidence_changed': False,
        'permutation_seed_formula': '1400000 + 20000*repeat + 2*pair (+1 for test)',
        'original': {'baseline_wrong': baseline_total, 'candidate_wrong': original_total,
                     'delta_wrong': original_total - baseline_total,
                     'better': original_better, 'tied': original_tied, 'worse': original_worse},
        'summary': {
            'permuted_both_delta_min': min(both), 'permuted_both_delta_median': median(both),
            'permuted_both_delta_max': max(both),
            'permuted_both_nonnegative_repeats': sum(x >= 0 for x in both),
            'permuted_test_only_delta_min': min(test_only),
            'permuted_test_only_delta_median': median(test_only),
            'permuted_test_only_delta_max': max(test_only),
            'permuted_test_only_nonnegative_repeats': sum(x >= 0 for x in test_only)},
        'replicates': per_repeat,
        'unknowns': {'real_eeg': 'TBD', 'online_action_policy': 'TBD',
                     'independent_source_authenticity': 'TBD',
                     'clinical_or_safety_benefit': 'TBD'},
        'maturity_advanced': False
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frozen', type=Path, default=Path(__file__).with_name('synthetic_evaluator.py'))
    p.add_argument('--pairs', type=int, default=PAIRS)
    p.add_argument('--repeats', type=int, default=8)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = evaluate(frozen_module(args.frozen), args.pairs, args.repeats)
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.output:
        if args.output.exists():
            raise FileExistsError('Refusing to overwrite existing result')
        args.output.write_text(payload, encoding='utf-8', newline='\n')
    else:
        print(payload, end='')

if __name__ == '__main__':
    main()
