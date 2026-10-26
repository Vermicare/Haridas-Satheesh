"""Publisher 90+7 held-out, 512 train-selected series; no raw data is published.

Observational in-stock sales are not latent-demand ground truth. This script
neither proves stockout correction nor estimates inventory/revenue uplift.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from parquet_export import REQUIRED, normalized_row, sha256_file, PINNED_REVISION, PUBLISHER_REPORTED_TRAIN_SHA256
from publisher_split_gate_v11 import validate_publisher_split
from retail_gate import EvidenceError, forecast_at_origin, parse_row

EVAL_SHA256 = '1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e'
SAMPLE_SEED = 'retail-official-holdout-v12-20261026'
SAMPLE_SIZE = 512
BOOTSTRAP_SEED = 20261026
BOOTSTRAP_REPS = 2000
MODELS = ('last_observed', 'seasonal_naive', 'causal_stockout_history')


def _key(store, product):
    if type(store) is not int or type(product) is not int or store < 0 or product < 0:
        raise EvidenceError('invalid train-only series identifier')
    return store, product


def select_train_only(keys, count=SAMPLE_SIZE):
    """Freeze sample before eval is read; never replace based on eval coverage."""
    if type(count) is not int or count < 1:
        raise EvidenceError('invalid predeclared sample size')
    unique = set(_key(*pair) for pair in keys)
    if len(unique) < count:
        raise EvidenceError('fewer training series than predeclared cohort')
    def rank(key):
        material = f'{SAMPLE_SEED}|{key[0]}|{key[1]}'.encode('ascii')
        return hashlib.sha256(material).digest(), key
    return tuple(sorted(unique, key=rank)[:count])


def parquet_ids(path):
    import pyarrow.parquet as pq
    for batch in pq.ParquetFile(path).iter_batches(batch_size=65536, columns=['store_id', 'product_id']):
        for store, product in zip(batch.column(0).to_pylist(), batch.column(1).to_pylist()):
            yield _key(store, product)


def parquet_selected(path, selected):
    import pyarrow as pa
    import pyarrow.parquet as pq
    for batch in pq.ParquetFile(path).iter_batches(batch_size=16384, columns=list(REQUIRED)):
        stores, products = batch.column(0).to_pylist(), batch.column(1).to_pylist()
        positions = [i for i, pair in enumerate(zip(stores, products)) if pair in selected]
        if positions:
            for obj in batch.take(pa.array(positions, type=pa.int32())).to_pylist():
                yield obj


def _strict_series(rows, expected, label):
    if len(rows) != expected:
        raise EvidenceError(f'{label}: expected {expected} distinct daily rows')
    days = [r['day'] for r in rows]
    if len(days) != len(set(days)):
        raise EvidenceError(f'{label}: duplicate day')
    if any((b-a).days != 1 for a, b in zip(days, days[1:])):
        raise EvidenceError(f'{label}: date gap or out-of-order row')


def percentile(sorted_values, q):
    position = (len(sorted_values)-1) * q
    lo = int(position)
    frac = position - lo
    return sorted_values[lo] * (1-frac) + sorted_values[min(lo+1, len(sorted_values)-1)] * frac


def bootstrap_macro_delta(deltas, reps=BOOTSTRAP_REPS, seed=BOOTSTRAP_SEED):
    if not deltas or any(not math.isfinite(x) for x in deltas):
        return None
    rng = random.Random(seed)
    n = len(deltas)
    means = sorted(math.fsum(deltas[rng.randrange(n)] for _ in range(n))/n for _ in range(reps))
    return [percentile(means, 0.025), percentile(means, 0.975)]


def evaluate_cohort(selected, train_rows, eval_rows):
    """Only TRAIN selects cohort. No selected series may be replaced on eval failure."""
    selected = tuple(selected)
    if not selected or len(set(selected)) != len(selected):
        raise EvidenceError('invalid frozen cohort')
    selected_set = set(selected)
    def group(items, name):
        groups = defaultdict(list)
        for index, obj in enumerate(items, 1):
            normalized = normalized_row(obj, index)
            row = parse_row(normalized, index)
            key = (int(row['key'][0]), int(row['key'][1]))
            if key not in selected_set:
                raise EvidenceError(f'{name}: noncohort row')
            groups[key].append(row)
        for values in groups.values():
            values.sort(key=lambda r: r['day'])
        return groups
    training, evaluation = group(train_rows, 'train'), group(eval_rows, 'eval')
    errors = {name: [] for name in MODELS}
    per_series = {name: [] for name in MODELS}
    deltas = []
    scored_series = censored_days = scored_days = 0
    for key in selected:
        tr, ev = training.get(key, []), evaluation.get(key, [])
        _strict_series(tr, 90, 'train')
        _strict_series(ev, 7, 'eval')
        validate_publisher_split([r['day'].isoformat() for r in tr],
                                 [r['day'].isoformat() for r in ev],
                                 fitted_dates=[r['day'].isoformat() for r in tr])
        if tr[0]['day'] != dt.date(2024, 3, 28) or ev[0]['day'] != dt.date(2024, 6, 26):
            raise EvidenceError('not the publisher official calendar window')
        # The model's seven predictions use only the 90 training days.
        predictions = forecast_at_origin(tr + ev, 90)
        observed = [i for i, r in enumerate(ev) if not r['censored']]
        scored_days += len(observed)
        censored_days += 7-len(observed)
        if not observed:
            continue
        scored_series += 1
        current = {}
        for model in MODELS:
            values = [abs(predictions[model][i] - ev[i]['y']) for i in observed]
            if any(not math.isfinite(v) for v in values):
                raise EvidenceError('nonfinite holdout error')
            errors[model].extend(values)
            current[model] = math.fsum(values) / len(values)
            per_series[model].append(current[model])
        deltas.append(current['causal_stockout_history'] - current['seasonal_naive'])
    if scored_days == 0:
        raise EvidenceError('no uncensored evaluation labels; cannot score')
    return {
        'frozen_train_selected_series': len(selected),
        'series_with_at_least_one_uncensored_eval_day': scored_series,
        'series_with_no_uncensored_eval_day': len(selected)-scored_series,
        'uncensored_eval_days_scored': scored_days,
        'censored_eval_days_excluded': censored_days,
        'day_weighted_mae': {m: math.fsum(errors[m])/len(errors[m]) for m in MODELS},
        'series_macro_mae': {m: math.fsum(per_series[m])/len(per_series[m]) for m in MODELS},
        'causal_minus_seasonal_macro_mae_delta': math.fsum(deltas)/len(deltas),
        'paired_series_bootstrap_95pct_ci_for_macro_delta': bootstrap_macro_delta(deltas),
        'bootstrap_unit': 'store-product series, paired resampling, not causal inference',
    }


def run(train, evaluation):
    train, evaluation = Path(train), Path(evaluation)
    if sha256_file(train) != PUBLISHER_REPORTED_TRAIN_SHA256:
        raise EvidenceError('publisher-pinned TRAIN SHA256 mismatch')
    if sha256_file(evaluation) != EVAL_SHA256:
        raise EvidenceError('publisher-pinned EVAL SHA256 mismatch')
    selected = select_train_only(parquet_ids(train))
    cohort_digest = hashlib.sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest()
    metrics = evaluate_cohort(selected, parquet_selected(train, set(selected)),
                              parquet_selected(evaluation, set(selected)))
    if sha256_file(train) != PUBLISHER_REPORTED_TRAIN_SHA256 or sha256_file(evaluation) != EVAL_SHA256:
        raise EvidenceError('source bytes changed during held-out evaluation')
    return {
        'experiment_id': 'retail-official-90-7-holdout-v12',
        'evidence_class': 'PINNED_PUBLISHER_90_7_OBSERVATIONAL_IN_STOCK_SALES_ONLY',
        'dataset': 'Dingdong-Inc/FreshRetailNet-50K',
        'publisher_revision': PINNED_REVISION,
        'publisher_train_sha256_locally_verified': PUBLISHER_REPORTED_TRAIN_SHA256,
        'publisher_eval_sha256_locally_verified': EVAL_SHA256,
        'source_origin_independently_attested': False,
        'cohort_rule': 'smallest 512 SHA256(seed|store_id|product_id) ranks from TRAIN IDs only',
        'cohort_seed': SAMPLE_SEED, 'cohort_sha256': cohort_digest,
        'eval_dates': ['2024-06-26', '2024-07-02'],
        'target': 'observed business-hour (06:00-21:59) sales on in-stock eval days',
        'models': list(MODELS),
        'bootstrap_seed': BOOTSTRAP_SEED, 'bootstrap_replicates': BOOTSTRAP_REPS,
        'metrics': metrics,
        'latent_demand_ground_truth': 'UNAVAILABLE',
        'inventory_or_revenue_uplift': 'TBD',
        'independent_external_replication': 'TBD',
        'maturity': 'Research / Architecture — unchanged',
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--train', type=Path, required=True)
    p.add_argument('--eval', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    report = run(a.train, a.eval)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'evidence_class': report['evidence_class'],
                      'series': report['metrics']['frozen_train_selected_series'],
                      'scored_days': report['metrics']['uncensored_eval_days_scored'],
                      'mae': report['metrics']['day_weighted_mae']}, sort_keys=True))


if __name__ == '__main__':
    main()
