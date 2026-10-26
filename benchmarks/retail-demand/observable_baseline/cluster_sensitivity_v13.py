"""Post-hoc store-clustered uncertainty sensitivity for frozen retail v1.2.

Reuses the original v1.2 forecast evaluator and the identical train-only cohort.
This is not a new holdout, latent-demand ground truth, or commercial uplift.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import official_holdout_v12 as frozen
from parquet_export import normalized_row
from retail_gate import EvidenceError, parse_row

COHORT_SHA256 = '7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710'
FROZEN_MACRO_DELTA = -0.014454543340773807
FROZEN_SCORED_DAYS = 2183
SEED = 20261027
REPS = 2000


def store_cluster_bootstrap(store_stats, reps=REPS, seed=SEED):
    """Paired cluster resampling; series-weighted macro-delta estimand.

    Each item is (store_id, scored_series_count, store_mean_delta).
    Stores, not individual store-product series, are resampled. No store IDs
    appear in the returned summary. Interval is descriptive, not causal.
    """
    if type(reps) is not int or reps < 1 or type(seed) is not int:
        raise EvidenceError('invalid bootstrap configuration')
    stats = sorted(store_stats, key=lambda item: item[0])
    ids = []
    for store, count, mean in stats:
        if type(store) is not int or store < 0 or type(count) is not int or count < 1:
            raise EvidenceError('invalid store cluster')
        if type(mean) not in (float, int) or not math.isfinite(mean):
            raise EvidenceError('nonfinite store mean')
        ids.append(store)
    if len(stats) < 2 or len(set(ids)) != len(ids):
        raise EvidenceError('at least two distinct scored stores required')
    n = len(stats)
    point = math.fsum(count * mean for _, count, mean in stats) / sum(count for _, count, _ in stats)
    rng = random.Random(seed)
    samples = []
    for _ in range(reps):
        picks = [stats[rng.randrange(n)] for _ in range(n)]
        samples.append(math.fsum(count * mean for _, count, mean in picks) /
                       sum(count for _, count, _ in picks))
    samples.sort()
    return {'scored_store_clusters': n, 'scored_series': sum(count for _, count, _ in stats),
            'series_weighted_macro_delta': point,
            'store_cluster_bootstrap_95pct_ci': [frozen.percentile(samples, 0.025),
                                                  frozen.percentile(samples, 0.975)],
            'bootstrap_replicates': reps, 'bootstrap_seed': seed,
            'resampling_unit': 'store (all scored product series resampled together)',
            'estimand': 'series-weighted mean of paired stockout-correction minus seasonal-naive per-series MAE'}


def evaluate_cluster_sensitivity(selected, train_rows, eval_rows):
    """Re-evaluate frozen model per store; fail on disagreement with v1.2."""
    selected = tuple(selected)
    selected_set = set(selected)
    training, evaluation = list(train_rows), list(eval_rows)
    original = frozen.evaluate_cohort(selected, training, evaluation)
    selected_by_store = defaultdict(list)
    for store, product in selected:
        selected_by_store[store].append((store, product))
    train_by_store, eval_by_store = defaultdict(list), defaultdict(list)
    for rows, target in ((training, train_by_store), (evaluation, eval_by_store)):
        for row in rows:
            store, product = frozen._key(row['store_id'], row['product_id'])
            if (store, product) not in selected_set:
                raise EvidenceError('noncohort row')
            target[store].append(row)
    stats = []
    unscored_stores = 0
    for store in sorted(selected_by_store):
        # v1.2 has already validated every row, calendar and split. A store
        # with zero observable eval days contributes no estimable score.
        observable = any(not parse_row(normalized_row(row, i), i)['censored']
                         for i, row in enumerate(eval_by_store[store], 1))
        if not observable:
            unscored_stores += 1
            continue
        part = frozen.evaluate_cohort(selected_by_store[store],
                                      train_by_store[store], eval_by_store[store])
        stats.append((store, part['series_with_at_least_one_uncensored_eval_day'],
                      part['causal_minus_seasonal_macro_mae_delta']))
    result = store_cluster_bootstrap(stats)
    if result['scored_series'] != original['series_with_at_least_one_uncensored_eval_day']:
        raise EvidenceError('cluster scoring changed frozen cohort denominator')
    if not math.isclose(result['series_weighted_macro_delta'],
                        original['causal_minus_seasonal_macro_mae_delta'],
                        rel_tol=0, abs_tol=1e-12):
        raise EvidenceError('cluster recomputation disagrees with frozen macro delta')
    result['unscored_store_clusters'] = unscored_stores
    result['frozen_v12_series_macro_delta'] = original['causal_minus_seasonal_macro_mae_delta']
    result['frozen_v12_scored_days'] = original['uncensored_eval_days_scored']
    return result


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if frozen.sha256_file(train) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256:
        raise EvidenceError('pinned train hash mismatch')
    if frozen.sha256_file(evaluation) != frozen.EVAL_SHA256:
        raise EvidenceError('pinned eval hash mismatch')
    selected = frozen.select_train_only(frozen.parquet_ids(train))
    digest = hashlib.sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest()
    if digest != COHORT_SHA256:
        raise EvidenceError('original frozen cohort identity mismatch')
    result = evaluate_cluster_sensitivity(selected,
                 frozen.parquet_selected(train, set(selected)),
                 frozen.parquet_selected(evaluation, set(selected)))
    if not math.isclose(result['frozen_v12_series_macro_delta'], FROZEN_MACRO_DELTA,
                        rel_tol=0, abs_tol=1e-12) or result['frozen_v12_scored_days'] != FROZEN_SCORED_DAYS:
        raise EvidenceError('original v1.2 aggregate reproduction mismatch')
    if frozen.sha256_file(train) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256 or frozen.sha256_file(evaluation) != frozen.EVAL_SHA256:
        raise EvidenceError('publisher source changed during run')
    return {'experiment_id': 'retail-store-cluster-sensitivity-v13',
            'analysis_type': 'POST_HOC_UNCERTAINTY_SENSITIVITY_NOT_NEW_HOLDOUT',
            'original_experiment_id': 'retail-official-90-7-holdout-v12',
            'cohort_sha256': digest,
            'publisher_train_sha256_verified': frozen.PUBLISHER_REPORTED_TRAIN_SHA256,
            'publisher_eval_sha256_verified': frozen.EVAL_SHA256,
            'method': 'store-clustered paired bootstrap; original v1.2 forecast code unchanged',
            'metrics': result,
            'latent_demand_ground_truth': 'UNAVAILABLE',
            'revenue_or_inventory_impact': 'TBD',
            'external_independent_validation': 'TBD',
            'maturity': 'Research / Architecture — unchanged'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--train', type=Path, required=True)
    p.add_argument('--eval', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    report = run(args.train, args.eval)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'experiment_id': report['experiment_id'],
                      'scored_store_clusters': report['metrics']['scored_store_clusters'],
                      'store_cluster_bootstrap_95pct_ci': report['metrics']['store_cluster_bootstrap_95pct_ci']},
                     sort_keys=True))


if __name__ == '__main__':
    main()
