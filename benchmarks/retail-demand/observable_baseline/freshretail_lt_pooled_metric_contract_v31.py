"""Fictional-only FreshRetailNet-LT pooled metric arithmetic preflight.

Independent of the v3.0 coverage/mask gate. Never run on publisher EVAL
before reference provenance and scorer equivalence are independently frozen.
No forecasting, leaderboard submission, or official metric parity is claimed.
"""
from __future__ import annotations

import datetime as dt
import math
from collections import defaultdict

FIELDS = frozenset({"dt", "prediction", "sale_amount", "psd", "stock_hour6_22_cnt"})
FORECAST_START = dt.date(2025, 7, 14)
FORECAST_END = dt.date(2025, 7, 20)


class MetricContractError(ValueError):
    pass


def _number(value, field):
    if isinstance(value, bool) or value is None:
        raise MetricContractError("invalid " + field)
    if isinstance(value, str) and (not value or value != value.strip()):
        raise MetricContractError("invalid " + field)
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MetricContractError("invalid " + field) from exc
    if not math.isfinite(number):
        raise MetricContractError("nonfinite " + field)
    return number


def _stock(value):
    if type(value) is int:
        result = value
    elif isinstance(value, str) and value.isascii() and value.isdecimal() and (
            len(value) == 1 or not value.startswith("0")):
        result = int(value)
    else:
        raise MetricContractError("invalid stockout count")
    if not 0 <= result <= 24:
        raise MetricContractError("out-of-range stockout count")
    return result


def _date(value):
    if not isinstance(value, str) or len(value) != 10:
        raise MetricContractError("invalid forecast date")
    try:
        day = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise MetricContractError("invalid forecast date") from exc
    if not FORECAST_START <= day <= FORECAST_END or day.isoformat() != value:
        raise MetricContractError("forecast date outside publisher horizon")
    return value


def _metrics(pairs):
    if not pairs:
        return None
    actual_total = math.fsum(y for y, _ in pairs)
    if actual_total <= 0:
        return None
    count = len(pairs)
    absolute_errors = [abs(pred - actual) for actual, pred in pairs]
    signed_errors = [pred - actual for actual, pred in pairs]
    return {
        "scored_rows": count,
        "wape_ratio": math.fsum(absolute_errors) / actual_total,
        "wpe_ratio": math.fsum(signed_errors) / actual_total,
        "mae": math.fsum(absolute_errors) / count,
        "mse": math.fsum(e * e for e in signed_errors) / count,
    }


def score_fictional(rows):
    """Aggregate explicitly fictional labels; no keys or predictions in output.

    This does not check full 70k target coverage or independently supplied psd.
    Call v3.0 separately before any eventual real-data scoring experiment.
    """
    by_day = defaultdict(list)
    counts = defaultdict(int)
    seen = False
    for row in rows:
        seen = True
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise MetricContractError("exact fictional scorer fields required")
        day = _date(row["dt"])
        actual = _number(row["sale_amount"], "sale_amount")
        pred = _number(row["prediction"], "prediction")
        psd = _number(row["psd"], "psd")
        stock = _stock(row["stock_hour6_22_cnt"])
        if actual < 0 or pred < 0:
            raise MetricContractError("negative sales or prediction")
        counts["total"] += 1
        if psd < 0 or stock != 0:
            counts["excluded"] += 1
            continue
        by_day[day].append((actual, pred))
        counts["eligible"] += 1
    if not seen or not counts["eligible"]:
        raise MetricContractError("no eligible fictional rows")
    pairs = [pair for day in sorted(by_day) for pair in by_day[day]]
    pooled = _metrics(pairs)
    if pooled is None:
        raise MetricContractError("pooled actual-sales denominator is zero")
    return {
        "schema": "freshretail-lt-pooled-metric-contract-v3.1",
        "source": "Dingdong-Inc/frn-baseline TFT/predictTFT.py cal_metrics (all_days)",
        "aggregation": "pooled eligible rows; ratio of sums, not mean of daily ratios",
        "total_fictional_rows": counts["total"],
        "eligible_fictional_rows": counts["eligible"],
        "excluded_fictional_rows": counts["excluded"],
        "pooled": pooled,
        "per_day_diagnostics": {day: _metrics(by_day[day]) for day in sorted(by_day)},
        "official_browser_equivalence": "TBD",
        "psd_reference_equivalence": "TBD",
        "full_target_coverage_verified": False,
        "publisher_eval_labels_used": False,
        "maturity_change": "NONE",
    }
