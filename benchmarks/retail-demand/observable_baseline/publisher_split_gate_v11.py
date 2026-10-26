"""Official 90/7 FreshRetailNet series split preflight; metadata-only, no real data.

This does not read publisher Parquet, authenticate provenance, fit models, or
measure forecasting accuracy. It checks date-series and fit-cutoff contracts.
"""
from __future__ import annotations
import datetime as dt
import json
import re

TRAIN_DAYS = 90
EVAL_DAYS = 7


class SplitError(ValueError):
    """An official train/eval chronology contract was violated."""


def _days(values, name, expected):
    if type(values) not in (tuple, list) or len(values) != expected:
        raise SplitError(f'{name} must contain exactly {expected} dates')
    out = []
    for value in values:
        if type(value) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            raise SplitError(f'{name} has noncanonical date')
        try:
            day = dt.date.fromisoformat(value)
        except ValueError as exc:
            raise SplitError(f'{name} has impossible date') from exc
        if day.isoformat() != value:
            raise SplitError(f'{name} has noncanonical date')
        out.append(day)
    if any((right - left).days != 1 for left, right in zip(out, out[1:])):
        raise SplitError(f'{name} must be strictly chronological and consecutive')
    return out


def validate_publisher_split(train_dates, eval_dates, *, fitted_dates=None):
    """Validate per-series 90 training + next 7 evaluation days.

    fitted_dates=None means no fit-provenance evidence; a caller must NOT
    infer a leakage-free model from the split check alone.
    """
    train = _days(train_dates, 'train', TRAIN_DAYS)
    evaluation = _days(eval_dates, 'eval', EVAL_DAYS)
    if (evaluation[0] - train[-1]).days != 1:
        raise SplitError('eval must begin immediately after train, without overlap or gap')
    fit_checked = fitted_dates is not None
    if fit_checked:
        if type(fitted_dates) not in (tuple, list):
            raise SplitError('fitted_dates must be a sequence')
        # A fit log can be empty (unfitted baseline), but cannot name held-out dates.
        for value in fitted_dates:
            if type(value) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise SplitError('fit provenance has noncanonical date')
            try:
                fitted = dt.date.fromisoformat(value)
            except ValueError as exc:
                raise SplitError('fit provenance has impossible date') from exc
            if fitted not in train:
                raise SplitError('fit provenance contains date outside official training window')
    return {
        'evidence_class': 'DATE_ONLY_SPLIT_CONTRACT_NO_PUBLISHER_BYTES',
        'train_days': len(train), 'eval_days': len(evaluation),
        'train_start': train[0].isoformat(), 'train_end': train[-1].isoformat(),
        'eval_start': evaluation[0].isoformat(), 'eval_end': evaluation[-1].isoformat(),
        'fit_date_boundary_checked': fit_checked,
        'fit_feature_leakage_excluded': False,
        'publisher_parquet_verified': False,
        'public_data_scores': 'TBD',
    }


def demo():
    start = dt.date(2025, 1, 1)
    dates = [(start + dt.timedelta(days=i)).isoformat() for i in range(97)]
    return json.dumps(validate_publisher_split(dates[:90], dates[90:], fitted_dates=dates[:90]),
                      indent=2, sort_keys=True, allow_nan=False) + '\n'


if __name__ == '__main__':
    print(demo(), end='')
