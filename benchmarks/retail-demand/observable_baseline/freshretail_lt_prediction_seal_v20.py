"""FreshRetailNet-LT v2.0: seal TRAIN-only forecasts before EVAL label access.

No EVAL path is accepted. This is prediction provenance, NOT forecast accuracy.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform

import freshretail_lt_train_cohort_v19 as v19
from freshretail_lt_source_gate_v18 import TRAIN_BYTES, TRAIN_SHA256, verify_file
from parquet_export import normalized_row
from retail_gate import forecast_at_origin, parse_row
from weekday_median_v14 import weekday_median_forecast

EXPECTED_COHORT_SHA256 = 'dc128d3bed90035214c80529bf58e685ad7d49c717d95bd10c30c2b9407ca016'
MODELS = ('last_observed', 'seasonal_naive', 'causal_stockout_history', 'weekday_median_last4')
PREDICTION_FIELDS = ('store_id', 'product_id', 'dt', 'hours_sale', 'hours_stock_status', 'stock_hour6_22_cnt')
FUTURE = tuple(v19.ORIGIN + dt.timedelta(days=i) for i in range(7))


class SealError(ValueError):
    pass


def cohort_digest(keys):
    return hashlib.sha256(json.dumps(keys, separators=(',', ':')).encode('ascii')).hexdigest()


def training_cohort(rows, size=v19.COHORT, expected_digest=EXPECTED_COHORT_SHA256):
    """Independently reproduce v1.9 TRAIN-only selection and pin its observed hash."""
    if type(size) is not int or size < 1:
        raise SealError('invalid cohort size')
    masks, bad = {}, set()
    window_rows = duplicates = invalid = 0
    for row in rows:
        key, day = v19.key_of(row), v19.day(row['dt'])
        if day >= v19.ORIGIN:
            raise SealError('TRAIN includes EVAL-origin or future date')
        if day < v19.START:
            continue
        if day > v19.END:
            raise SealError('TRAIN has unexpected date')
        window_rows += 1
        bit = 1 << (day - v19.START).days
        old = masks.get(key, 0)
        if old & bit:
            duplicates += 1
            bad.add(key)
        masks[key] = old | bit
        if not v19.valid_status(row):
            invalid += 1
            bad.add(key)
    eligible = [key for key, mask in masks.items() if mask == v19.FULL_MASK and key not in bad]
    selected = tuple(sorted(eligible, key=v19.rank)[:size])
    if len(selected) != size:
        raise SealError('insufficient complete TRAIN series; do not replace using EVAL')
    digest = cohort_digest(selected)
    if digest != expected_digest:
        raise SealError('v1.9 frozen TRAIN-only cohort fingerprint mismatch')
    return selected, {'training_rows_in_window': window_rows,
                      'distinct_training_series': len(masks),
                      'eligible_complete_valid_series': len(eligible),
                      'duplicate_training_rows': duplicates,
                      'invalid_stock_status_rows': invalid,
                      'selected_series': len(selected),
                      'selected_cohort_sha256': digest}


def in_frozen_training_window(raw):
    """Discard earlier TRAIN years, never tolerate future TRAIN dates."""
    day = v19.day(raw['dt'])
    if day >= v19.ORIGIN:
        raise SealError('TRAIN contains EVAL-origin or future row')
    return v19.START <= day <= v19.END


def parquet_selected_training(path, selected):
    """Stream only frozen 90-day TRAIN rows; no EVAL or future covariates."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    if not set(PREDICTION_FIELDS).issubset(parquet.schema_arrow.names):
        raise SealError('TRAIN lacks required hourly sales/status columns')
    for batch in parquet.iter_batches(batch_size=8192, columns=list(PREDICTION_FIELDS)):
        stores, products = batch.column(0).to_pylist(), batch.column(1).to_pylist()
        indices = [i for i, key in enumerate(zip(stores, products)) if key in selected]
        if indices:
            for raw in batch.take(pa.array(indices, type=pa.int32())).to_pylist():
                if in_frozen_training_window(raw):
                    yield raw


def sealed_predictions(selected, selected_training_rows):
    """Commit canonical predictions without emitting raw series or forecast rows.

    Future placeholders have only dates: a future label read would raise.
    """
    if not selected or len(set(selected)) != len(selected):
        raise SealError('invalid frozen cohort')
    groups = defaultdict(list)
    selected_set = set(selected)
    for index, raw in enumerate(selected_training_rows, 1):
        key = v19.key_of(raw)
        if key not in selected_set:
            raise SealError('noncohort TRAIN row')
        parsed = parse_row(normalized_row(raw, index), index)
        if parsed['day'] < v19.START or parsed['day'] > v19.END:
            raise SealError('selected TRAIN row outside frozen history')
        groups[key].append(parsed)
    digest = hashlib.sha256()
    fallbacks = {'weekday': 0, 'recent14': 0, 'zero': 0}
    total = 0
    for key in selected:
        training = sorted(groups.get(key, []), key=lambda r: r['day'])
        if len(training) != v19.DAYS or len({r['day'] for r in training}) != v19.DAYS:
            raise SealError('missing or duplicate selected TRAIN day')
        if any(r['day'] != v19.START + dt.timedelta(days=i)
               for i, r in enumerate(training)):
            raise SealError('selected TRAIN history has date gap')
        placeholders = [{'day': day} for day in FUTURE]
        original = forecast_at_origin(training + placeholders, v19.DAYS)
        weekday, counts = weekday_median_forecast(training, list(FUTURE))
        forecasts = {**original, 'weekday_median_last4': weekday}
        if set(forecasts) != set(MODELS):
            raise SealError('frozen four-model contract changed')
        for name in MODELS:
            values = forecasts[name]
            if (len(values) != 7 or any(type(x) not in (int, float)
                                        or not math.isfinite(x) or x < 0 for x in values)):
                raise SealError('invalid TRAIN-only forecast')
        for name in fallbacks:
            fallbacks[name] += counts[name]
        payload = {'series': list(key), 'future_dates': [d.isoformat() for d in FUTURE],
                   'predictions': {name: forecasts[name] for name in MODELS}}
        digest.update(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                 allow_nan=False).encode('ascii') + b'\n')
        total += 7
    return {'status': 'TRAIN_ONLY_PREDICTIONS_SEALED_NO_EVAL_ACCESS',
            'prediction_schema': 'retail-lt-v20-per-series-seven-day-canonical-jsonl-v1',
            'prediction_sha256': digest.hexdigest(),
            'predicted_series': len(selected), 'forecast_dates': [d.isoformat() for d in FUTURE],
            'predicted_days': total, 'models': list(MODELS),
            'training_only_weekday_fallback_counts': fallbacks,
            'evaluation_file_opened': False, 'evaluation_labels_read': False,
            'forecast_accuracy': 'TBD', 'latent_demand_accuracy': 'TBD',
            'inventory_or_revenue_uplift': 'TBD', 'maturity_change': 'NONE'}


def run(train):
    train = Path(train)
    source = verify_file(train, TRAIN_BYTES, TRAIN_SHA256)
    selected, cohort = training_cohort(v19.parquet_rows(train))
    forecast = sealed_predictions(selected, parquet_selected_training(train, set(selected)))
    if verify_file(train, TRAIN_BYTES, TRAIN_SHA256) != source:
        raise SealError('TRAIN source changed during prediction sealing')
    import pyarrow
    return {**forecast, 'experiment': 'retail-lt-train-only-prediction-seal-v20',
            'cohort': cohort,
            'provenance': {'dataset': 'Dingdong-Inc/FreshRetailNet-LT',
                           'publisher_revision': '01c3bb306415e09d3ccd2fe762f33eb3aeb2affd',
                           'train_sha256_verified': source['sha256'],
                           'train_bytes_verified': source['bytes'],
                           'python': platform.python_version(),
                           'pyarrow': pyarrow.__version__,
                           'runner_os': platform.system(),
                           'git_checkout': os.environ.get('GITHUB_SHA', 'TBD'),
                           'publisher_authenticity_independently_attested': False}}


def main():
    parser = argparse.ArgumentParser(description='TRAIN-only frozen predictions; no EVAL argument')
    parser.add_argument('--train', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    report = run(args.train)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n',
                           encoding='utf-8', newline='\n')
    print(json.dumps({'status': report['status'],
                      'cohort_sha256': report['cohort']['selected_cohort_sha256'],
                      'prediction_sha256': report['prediction_sha256'],
                      'evaluation_labels_read': False}, sort_keys=True))


if __name__ == '__main__':
    main()
