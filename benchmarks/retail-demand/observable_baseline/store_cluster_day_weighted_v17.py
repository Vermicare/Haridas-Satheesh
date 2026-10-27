"""Post-hoc, descriptive v1.5 day-weighted paired store-cluster sensitivity.

DO NOT treat this as a new holdout or change the preregistered v1.5 FAILED gate.
Uses only the publisher's already-inspected 2024-06-26..07-02 evaluation window.
No raw store/product rows, identifiers, sales or predictions are written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import official_holdout_v12 as frozen
import store_disjoint_v15 as v15
import weekday_median_v14 as v14
from retail_gate import EvidenceError, forecast_at_origin

SEED = 20261028
REPS = 2000


def _valid_float(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def _percentile(values, q):
    return frozen.percentile(values, q)


def paired_store_cluster_day_ci(records, *, reps=REPS, seed=SEED):
    """Store bootstrap of ratio of PAIRED error sums to observed-day counts.

    Each (store, product, days, candidate_abs_error_sum, baseline_abs_error_sum)
    represents one fictional or real series. Resampling draws whole stores and
    retains every series within each store. This is a descriptive percentile CI.
    """
    if type(reps) is not int or not 100 <= reps <= 100000 or type(seed) is not int:
        raise EvidenceError('invalid bootstrap configuration')
    grouped = defaultdict(list)
    seen = set()
    for row in records:
        if not isinstance(row, (tuple, list)) or len(row) != 5:
            raise EvidenceError('invalid series record shape')
        store, product, days, candidate_sum, baseline_sum = row
        if (type(store) is not int or store < 0 or type(product) is not int or product < 0 or
                type(days) is not int or not 1 <= days <= 7 or
                not _valid_float(candidate_sum) or not _valid_float(baseline_sum) or
                candidate_sum < 0 or baseline_sum < 0):
            raise EvidenceError('invalid series sufficient statistics')
        if (store, product) in seen:
            raise EvidenceError('duplicate store-product series')
        seen.add((store, product))
        delta = candidate_sum - baseline_sum
        if not math.isfinite(delta):
            raise EvidenceError('nonfinite paired error difference')
        grouped[store].append((days, delta))
    if len(grouped) < 2:
        raise EvidenceError('at least two independent store clusters required')
    clusters = []
    for store in sorted(grouped):
        days = sum(x[0] for x in grouped[store])
        delta = math.fsum(x[1] for x in grouped[store])
        if not math.isfinite(delta):
            raise EvidenceError('nonfinite store error sum')
        clusters.append((days, delta, len(grouped[store])))
    total_days = sum(x[0] for x in clusters)
    total_delta = math.fsum(x[1] for x in clusters)
    point = total_delta / total_days
    if not math.isfinite(point):
        raise EvidenceError('nonfinite pooled estimate')
    rng = random.Random(seed)
    n = len(clusters)
    samples = []
    for _ in range(reps):
        drawn = [clusters[rng.randrange(n)] for _ in range(n)]
        estimate = math.fsum(x[1] for x in drawn) / sum(x[0] for x in drawn)
        if not math.isfinite(estimate):
            raise EvidenceError('nonfinite bootstrap estimate')
        samples.append(estimate)
    samples.sort()
    leave_one_store_out = [
        (total_delta - delta) / (total_days - days)
        for days, delta, _ in clusters
    ]
    return {
        'estimand': 'day-weighted weekday-median minus last-observed MAE, on in-stock days',
        'uncertainty': 'paired whole-store percentile bootstrap, resampling store clusters with replacement',
        'point_delta': point,
        'store_cluster_ci95': [_percentile(samples, .025), _percentile(samples, .975)],
        'store_count': n,
        'series_count': len(seen),
        'scored_days': total_days,
        'min_series_per_store': min(x[2] for x in clusters),
        'max_series_per_store': max(x[2] for x in clusters),
        'leave_one_store_out_delta_range': [min(leave_one_store_out), max(leave_one_store_out)],
        'bootstrap_seed': seed,
        'bootstrap_replicates': reps,
        'statistical_limit': 'descriptive post-hoc interval; same previously inspected temporal holdout; no independent temporal confirmation',
    }


def sufficient_statistics(selected, train_rows, eval_rows):
    """Calculate paired sums with frozen v1.4 predictions; no cohort substitution."""
    selected = tuple(selected)
    if not selected or len(set(selected)) != len(selected):
        raise EvidenceError('invalid selected cohort')
    training = v14._group(train_rows, set(selected))
    evaluation = v14._group(eval_rows, set(selected))
    records = []
    for store, product in selected:
        tr, ev = training.get((store, product), []), evaluation.get((store, product), [])
        frozen._strict_series(tr, 90, 'train')
        frozen._strict_series(ev, 7, 'eval')
        frozen.validate_publisher_split(
            [r['day'].isoformat() for r in tr],
            [r['day'].isoformat() for r in ev],
            fitted_dates=[r['day'].isoformat() for r in tr],
        )
        if tr[0]['day'] != dt.date(2024, 3, 28) or ev[0]['day'] != dt.date(2024, 6, 26):
            raise EvidenceError('unexpected publisher calendar')
        candidate, _ = v14.weekday_median_forecast(tr, [r['day'] for r in ev])
        prior = forecast_at_origin(tr + ev, 90)['last_observed']
        indices = [i for i, row in enumerate(ev) if not row['censored']]
        if not indices:
            continue
        candidate_sum = math.fsum(abs(candidate[i] - ev[i]['y']) for i in indices)
        baseline_sum = math.fsum(abs(prior[i] - ev[i]['y']) for i in indices)
        records.append((store, product, len(indices), candidate_sum, baseline_sum))
    return records


def run(train_path, eval_path, frozen_result_path):
    train_path, eval_path = Path(train_path), Path(eval_path)
    if (frozen.sha256_file(train_path) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256 or
            frozen.sha256_file(eval_path) != frozen.EVAL_SHA256):
        raise EvidenceError('pinned publisher source mismatch')
    preserved = json.loads(Path(frozen_result_path).read_text(encoding='utf-8'))
    if preserved.get('experiment_id') != v15.EXPERIMENT_ID or preserved.get('primary_gate', {}).get('conditional_store_transfer_gate_passed') is not False:
        raise EvidenceError('original negative decision changed')
    _, selected = v15.select_disjoint_training_cohort(frozen.parquet_ids(train_path))
    if v15.digest_cohort(selected) != preserved['new_cohort_sha256']:
        raise EvidenceError('frozen v1.5 cohort mismatch')
    chosen = set(selected)
    train_rows = list(frozen.parquet_selected(train_path, chosen))
    eval_rows = list(frozen.parquet_selected(eval_path, chosen))
    # Preserve a second independent computation path for the original point values.
    original = v14.evaluate_v14(selected, train_rows, eval_rows)
    m = preserved['metrics']
    for got, expected in (
        (original['weekday_median_last4_day_weighted_mae'], m['weekday_median_last4_day_weighted_mae']),
        (original['original_v12_metrics']['day_weighted_mae']['last_observed'], m['original_v12_metrics']['day_weighted_mae']['last_observed']),
        (original['weekday_median_minus_last_observed_series_macro_delta'], m['weekday_median_minus_last_observed_series_macro_delta']),
    ):
        if not math.isclose(got, expected, rel_tol=0, abs_tol=1e-10):
            raise EvidenceError('frozen v1.5 metrics not reproduced')
    records = sufficient_statistics(selected, train_rows, eval_rows)
    result = paired_store_cluster_day_ci(records)
    expected_delta = m['weekday_median_last4_day_weighted_mae'] - m['original_v12_metrics']['day_weighted_mae']['last_observed']
    if (result['scored_days'] != m['scored_days'] or result['series_count'] != m['scored_series'] or
            result['store_count'] != preserved['new_cohort_stores'] or
            not math.isclose(result['point_delta'], expected_delta, rel_tol=0, abs_tol=1e-10)):
        raise EvidenceError('independent sufficient-statistics reconciliation failed')
    if (frozen.sha256_file(train_path) != frozen.PUBLISHER_REPORTED_TRAIN_SHA256 or
            frozen.sha256_file(eval_path) != frozen.EVAL_SHA256):
        raise EvidenceError('source changed during evaluation')
    return {
        'experiment_id': 'retail-v17-posthoc-dayweighted-cluster-sensitivity',
        'analysis_type': 'POST_HOC_REANALYSIS_SAME_SEEN_TEMPORAL_WINDOW_NOT_CONFIRMATORY',
        'source_experiment': v15.EXPERIMENT_ID,
        'source_cohort_sha256': preserved['new_cohort_sha256'],
        'publisher_train_sha256': frozen.PUBLISHER_REPORTED_TRAIN_SHA256,
        'publisher_eval_sha256': frozen.EVAL_SHA256,
        'original_predeclared_v15_gate': 'FAILED_UNCHANGED',
        'paired_store_dayweighted': result,
        'independent_temporal_holdout': 'TBD',
        'latent_demand_ground_truth': 'UNAVAILABLE',
        'decision_value': 'TBD',
        'maturity': 'Research / Architecture — unchanged',
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--train', required=True, type=Path)
    p.add_argument('--eval', required=True, type=Path)
    p.add_argument('--preserved', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    report = run(args.train, args.eval, args.preserved)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'experiment_id': report['experiment_id'], 'paired_store_dayweighted': report['paired_store_dayweighted'], 'original_gate': report['original_predeclared_v15_gate']}, sort_keys=True))


if __name__ == '__main__':
    main()
