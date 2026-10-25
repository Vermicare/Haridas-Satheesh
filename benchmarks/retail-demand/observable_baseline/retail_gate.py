"""Fail-closed, leakage-tested FreshRetailNet hourly-status baseline (standard library only).

Public-data benchmark is NOT established by this package. Input must be acquired separately.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

BUSINESS_HOURS = range(6, 22)  # 06:00 through 21:59, matching stock_hour6_22_cnt
ORIGINS = (42, 56, 70)
HORIZON = 7


class EvidenceError(ValueError):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_row(obj, line):
    try:
        # Mirror parquet_export.normalized_row: never coerce IDs or truncate
        # timestamps into dates. Coercion can collapse distinct source rows.
        if not isinstance(obj, dict):
            raise EvidenceError('expected JSON object')
        for field in ('store_id', 'product_id'):
            if type(obj[field]) is not int or obj[field] < 0:
                raise EvidenceError(f'{field} must be a nonnegative integer')
        date_text = obj['dt']
        if type(date_text) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_text):
            raise EvidenceError('dt must be canonical YYYY-MM-DD')
        day = dt.date.fromisoformat(date_text)
        if day.isoformat() != date_text:
            raise EvidenceError('dt must be canonical YYYY-MM-DD')
        key = (str(obj['store_id']), str(obj['product_id']))
        sale = obj['hours_sale']
        status = obj['hours_stock_status']
        count = obj['stock_hour6_22_cnt']
        if len(sale) != 24 or len(status) != 24:
            raise EvidenceError('hourly arrays must have 24 elements')
        try:
            invalid_sale = any(type(x) not in (int, float) or x < 0 or not math.isfinite(x)
                               for x in sale)
        except OverflowError:
            invalid_sale = True  # Extremely large Python integers cannot become finite floats.
        if invalid_sale:
            raise EvidenceError('invalid hourly sale value')
        try:
            observed_sales = sum(sale[h] for h in BUSINESS_HOURS)
            if not math.isfinite(observed_sales):
                raise EvidenceError('nonfinite business-hour sales aggregate')
        except OverflowError as exc:
            raise EvidenceError('nonfinite business-hour sales aggregate') from exc
        if any(type(x) is not int or x not in (0, 1) for x in status):
            raise EvidenceError('stock status must be integer 0 or 1')
        if type(count) is not int or count != sum(status[h] for h in BUSINESS_HOURS):
            raise EvidenceError('stock_hour6_22_cnt does not equal status[6:22]')
        return {'key': key, 'day': day, 'y': observed_sales,
                'censored': count > 0, 'stockout_hours': count}
    except (KeyError, TypeError, IndexError, ValueError) as e:
        raise EvidenceError(f'line {line}: {e}') from e


def read_jsonl(path):
    groups = defaultdict(list)
    seen = set()
    with open(path, encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise EvidenceError(f'line {line_no}: malformed JSON') from e
            row = parse_row(obj, line_no)
            ident = (*row['key'], row['day'])
            if ident in seen:
                raise EvidenceError(f'line {line_no}: duplicate store/product/date')
            seen.add(ident)
            groups[row['key']].append(row)
    if not groups:
        raise EvidenceError('empty dataset')
    for group in groups.values():
        group.sort(key=lambda x: x['day'])
    return groups


def select_series(groups):
    """Choose cohort using ONLY the first 42 days; validate held-out coverage after selection."""
    for key in sorted(groups):
        rows = groups[key]
        train = rows[:ORIGINS[0]]
        if len(train) < ORIGINS[0]:
            continue
        if any((b['day'] - a['day']).days != 1 for a, b in zip(train, train[1:])):
            continue
        if not any(r['censored'] for r in train):
            continue
        if not any(not r['censored'] for r in train):
            continue
        # Do not skip a cohort after seeing its future: that would select on test availability.
        if len(rows) < max(ORIGINS) + HORIZON or any(
                (b['day'] - a['day']).days != 1 for a, b in zip(rows, rows[1:])):
            raise EvidenceError('preselected cohort has incomplete held-out horizon; do not select replacement using test data')
        return key, rows
    raise EvidenceError('no eligible first-42-day training cohort; do not relax selection')


def corrected_training_history(rows, origin):
    """Causal same-weekday replacement using only earlier uncensored observations."""
    out = []
    for i in range(origin):
        r = rows[i]
        if not r['censored']:
            out.append(r['y'])
            continue
        candidates = [rows[j]['y'] for j in range(i) if not rows[j]['censored']
                      and rows[j]['day'].weekday() == r['day'].weekday()]
        if not candidates:
            out.append(r['y'])  # conservative fallback, never pretend known latent demand
        else:
            recent = sorted(candidates[-4:])
            out.append(recent[len(recent) // 2] if len(recent) % 2 else
                       (recent[len(recent)//2-1] + recent[len(recent)//2]) / 2)
    return out


def mae(pairs):
    return sum(abs(a - b) for a, b in pairs) / len(pairs) if pairs else None


def forecast_at_origin(rows, origin):
    """Forecasts use strictly prior rows and never consume test labels or stock flags."""
    if origin < 7 or origin + HORIZON > len(rows):
        raise EvidenceError('invalid forecast origin')
    hist = corrected_training_history(rows, origin)
    return {'last_observed': [rows[origin-1]['y']] * HORIZON,
            'seasonal_naive': [rows[origin-7+k]['y'] for k in range(HORIZON)],
            'causal_stockout_history': [hist[origin-7+k] for k in range(HORIZON)]}


def evaluate(rows):
    result = []
    for origin in ORIGINS:
        preds = forecast_at_origin(rows, origin)
        valid = [k for k in range(HORIZON) if not rows[origin+k]['censored']]
        scored = {}
        for model, values in preds.items():
            scored[model] = {'mae_uncensored_only': mae([(values[k], rows[origin+k]['y']) for k in valid]),
                             'evaluated_days': len(valid)}
        result.append({'origin_date': rows[origin]['day'].isoformat(),
                       'train_last_date': rows[origin-1]['day'].isoformat(),
                       'horizon_days': HORIZON, 'test_days': HORIZON,
                       'uncensored_test_days': len(valid),
                       'censored_test_days_excluded_from_latent_truth_scoring': HORIZON-len(valid),
                       'models': scored})
    return result


def benchmark(path, expected_hash=None, source_uri=None, synthetic=False):
    if not synthetic and (not expected_hash or not source_uri):
        raise EvidenceError('external input requires source URI and pinned local SHA-256')
    actual = sha256_file(path)
    if expected_hash and actual.lower() != expected_hash.lower():
        raise EvidenceError('source checksum mismatch')
    key, rows = select_series(read_jsonl(path))
    if sha256_file(path) != actual:
        raise EvidenceError("source changed during benchmark ingestion; aborting")
    return {'schema_version': '1.0', 'data_kind': 'FICTIONAL_TEST_ONLY' if synthetic else
            'EXTERNAL_SNAPSHOT_ORIGIN_NOT_INDEPENDENTLY_ATTESTED',
            'source_uri': 'fictional fixture' if synthetic else source_uri,
            'input_sha256': actual, 'selected_store_id': key[0], 'selected_product_id': key[1],
            'selection_rule': 'lexicographically first consecutive 42-day training series with stockout and nonstockout; reject if its 77-day held-out coverage is incomplete',
            'business_hours': '06:00-21:59', 'folds': evaluate(rows),
            'latent_demand_ground_truth': 'UNAVAILABLE', 'ranking_intervention_outcome': 'TBD',
            'maturity': 'Research / Architecture — unchanged'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--source-sha256')
    p.add_argument('--source-uri')
    p.add_argument('--synthetic', action='store_true', help='only for explicitly fictional fixtures')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    report = benchmark(a.input, a.source_sha256, a.source_uri, a.synthetic)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"{report['data_kind']}: {len(report['folds'])} folds, report={a.output}")


if __name__ == '__main__':
    main()
