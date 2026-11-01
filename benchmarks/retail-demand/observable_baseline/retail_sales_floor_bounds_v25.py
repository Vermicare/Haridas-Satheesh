#!/usr/bin/env python3
"""Retail v2.5: conditional sharp paired-MAE bounds using observed stockout sales.

FICTIONAL contract engine. A censored day's observed sales are a LOWER bound
on latent demand only if source semantics support sales <= demand for the
same business-hour target. This does not infer lost demand or claim accuracy.
"""
from __future__ import annotations
import json
import math
import stockout_identification_bounds_v23 as v23

SCHEMA = "retail-stockout-sales-floor-bounds-v2.5"
INPUT_SCHEMA = "retail-stockout-sales-floor-input-v1"


class FloorError(ValueError):
    pass


def row_bounds(a, b, floor):
    """Sharp range of |a-y|-|b-y| for y >= floor, with no upper demand cap."""
    a, b, floor = (v23._number(x) for x in (a, b, floor))
    points = [floor] + [x for x in (a, b) if x >= floor]
    values = [v23._delta(a, b, y) for y in points]
    return min(values), max(values)


def evaluate(doc):
    if not isinstance(doc, dict) or set(doc) != {"schema", "rows"} or doc["schema"] != INPUT_SCHEMA:
        raise FloorError("invalid_top_level_schema")
    rows = doc["rows"]
    if not isinstance(rows, list) or not 0 < len(rows) <= v23.MAX_ROWS:
        raise FloorError("invalid_row_count")
    legacy_rows = []
    floors = []
    positive = 0
    for row in rows:
        if not isinstance(row, dict):
            raise FloorError("invalid_row")
        if type(row.get("observed")) is not bool:
            raise FloorError("invalid_observation_flag")
        keys = {"key", "a", "b", "observed", "y" if row["observed"] else "sales_floor"}
        if set(row) != keys:
            raise FloorError("invalid_row_schema")
        a, b = v23._number(row["a"]), v23._number(row["b"])
        key = row["key"]
        item = {"key": key, "a": a, "b": b, "observed": row["observed"]}
        if row["observed"]:
            y = v23._number(row["y"])
            item["y"] = y
            floors.append((v23._delta(a, b, y), v23._delta(a, b, y)))
        else:
            floor = v23._number(row["sales_floor"])
            positive += floor > 0
            floors.append(row_bounds(a, b, floor))
        legacy_rows.append(item)
    # Reuse the frozen v2.3 schema and duplicate-key checks; never expose IDs.
    baseline = v23.evaluate({"schema": v23.INPUT_SCHEMA, "cap": None, "rows": legacy_rows})
    n = len(rows)
    lo = math.fsum(x[0] for x in floors) / n
    hi = math.fsum(x[1] for x in floors) / n
    old_lo, old_hi = baseline["full_period_paired_mae_delta_lower"], baseline["full_period_paired_mae_delta_upper"]
    if lo < old_lo - 1e-10 or hi > old_hi + 1e-10 or lo > hi + 1e-10:
        raise FloorError("floor_bounds_not_nested_in_nonnegative_bounds")
    decision = ("A_lower_MAE_for_all_admissible_outcomes" if hi < 0 else
                "B_lower_MAE_for_all_admissible_outcomes" if lo > 0 else
                "undetermined_including_ties")
    return {
        "schema": SCHEMA,
        "analysis": "CONDITIONAL_SALES_LOWER_BOUND_NOT_LOST_DEMAND_IMPUTATION",
        "assumption": "same-target latent demand >= recorded business-hour sales on censored days",
        "total_days": n,
        "observed_days": baseline["observed_days"],
        "censored_days": baseline["censored_days"],
        "censored_days_with_positive_sales_floor": positive,
        "observed_only_paired_mae_delta_A_minus_B": baseline["observed_only_paired_mae_delta_A_minus_B"],
        "nonnegative_only_lower": old_lo,
        "nonnegative_only_upper": old_hi,
        "sales_floor_lower": lo,
        "sales_floor_upper": hi,
        "identification_decision": decision,
        "no_censored_latent_demand_imputed": True,
        "uncertainty_type": "conditional sharp logical bounds, NOT statistical confidence intervals",
        "physical_sales_demand_semantics_independently_verified": False,
        "latent_demand_truth": "UNAVAILABLE",
        "inventory_value": "TBD",
        "independent_validation": "TBD",
        "maturity_change": "NONE",
    }


def main():
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists() or args.output.resolve() == args.input.resolve():
        raise SystemExit("refusing to overwrite evidence or source")
    raw = args.input.read_bytes()
    if len(raw) > v23.MAX_BYTES:
        raise FloorError("oversized_input")
    result = evaluate(v23._strict_load(raw.decode("utf-8")))
    with args.output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
