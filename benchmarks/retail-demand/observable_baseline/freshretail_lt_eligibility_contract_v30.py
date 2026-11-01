"""FreshRetailNet-LT v3.0: fictional-only eligibility-mask contract, NOT a scorer.

The publisher's pre-evaluator scores only (psd >= 0) AND
(stock_hour6_22_cnt == 0), after full 70,000-target coverage.
This module requires an independently supplied per-series psd reference;
it does NOT calculate psd, inspect EVAL labels, or claim reference equivalence.
Only exact allowed input fields are accepted; aggregate counts are returned.
"""
from __future__ import annotations

import datetime as dt
import math
from collections import Counter

from freshretail_lt_full_target_gate_v27 import (
    EXPECTED_TARGETS, CoverageError, key, validate as coverage_validate, _id,
)

TARGET_FIELDS = frozenset({"store_id", "product_id", "dt", "stock_hour6_22_cnt"})
PSD_FIELDS = frozenset({"store_id", "product_id", "psd"})


class MaskContractError(ValueError):
    pass


def _exact(row, fields, context):
    if not isinstance(row, dict) or set(row) != fields:
        raise MaskContractError(f"{context} fields must be exact; no answer columns")


def _finite_number(value, context):
    if value is None or isinstance(value, bool):
        raise MaskContractError(f"invalid {context}")
    if isinstance(value, str) and (value != value.strip() or not value):
        raise MaskContractError(f"invalid {context}")
    try:
        x = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise MaskContractError(f"invalid {context}") from exc
    if not math.isfinite(x):
        raise MaskContractError(f"invalid {context}")
    return x


def _stock(value):
    if isinstance(value, bool) or value is None:
        raise MaskContractError("invalid stockout-hour count")
    if type(value) is int:
        n = value
    elif isinstance(value, str) and value.isascii() and value.isdecimal():
        if len(value) > 1 and value[0] == "0":
            raise MaskContractError("noncanonical stockout-hour count")
        n = int(value)
    else:
        raise MaskContractError("invalid stockout-hour count")
    if not 0 <= n <= 24:
        raise MaskContractError("stockout-hour count outside daily bounds")
    return n


def audit(target_rows, prediction_rows, psd_reference_rows, *, expected=EXPECTED_TARGETS):
    """Fail closed on coverage/reference mismatch; return no identifiers/labels."""
    targets = list(target_rows)
    for row in targets:
        _exact(row, TARGET_FIELDS, "target")
    try:
        coverage = coverage_validate(targets, prediction_rows, expected=expected)
    except CoverageError as exc:
        raise MaskContractError(f"coverage prerequisite failed: {exc}") from exc

    psd_by_series = {}
    for row in psd_reference_rows:
        _exact(row, PSD_FIELDS, "psd reference")
        try:
            series = (_id(row["store_id"]), _id(row["product_id"]))
        except CoverageError as exc:
            raise MaskContractError("invalid psd reference key") from exc
        if series in psd_by_series:
            raise MaskContractError("duplicate psd reference series")
        psd_by_series[series] = _finite_number(row["psd"], "psd")

    target_series = {key(row)[:2] for row in targets}
    if set(psd_by_series) != target_series:
        raise MaskContractError("psd reference series mismatch")

    counts = Counter()
    daily = {}
    for row in targets:
        k = key(row)
        stock = _stock(row["stock_hour6_22_cnt"])
        psd_ok = psd_by_series[k[:2]] >= 0
        stock_ok = stock == 0
        date = k[2]
        day = daily.setdefault(date, Counter())
        counts["total"] += 1
        day["total"] += 1
        if psd_ok and stock_ok:
            counts["eligible"] += 1
            day["eligible"] += 1
        else:
            category = ("excluded_both" if not psd_ok and not stock_ok else
                        "excluded_psd" if not psd_ok else "excluded_stockout")
            counts[category] += 1
            day[category] += 1

    return {
        "schema": "freshretail-lt-eligibility-contract-v3.0",
        "coverage": coverage["coverage"],
        "target_rows": counts["total"],
        "eligible_rows": counts["eligible"],
        "excluded_psd": counts["excluded_psd"],
        "excluded_stockout": counts["excluded_stockout"],
        "excluded_both": counts["excluded_both"],
        "per_day": {d: {name: daily[d][name] for name in
                       ("total", "eligible", "excluded_psd", "excluded_stockout",
                        "excluded_both")} for d in sorted(daily)},
        "mask_rule": "psd >= 0 and stock_hour6_22_cnt == 0",
        "psd_reference_provenance": "CALLER_SUPPLIED_UNVERIFIED",
        "publisher_reference_equivalence": "TBD",
        "metrics": "TBD",
        "eval_labels_read": False,
        "official_leaderboard_comparable": False,
        "maturity_change": "NONE",
    }
