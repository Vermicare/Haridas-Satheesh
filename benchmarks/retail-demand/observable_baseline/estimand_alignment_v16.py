"""Post-hoc, aggregate-only estimand audit of retail v1.5; no new publisher evidence."""
from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path

class AuditError(ValueError):
    pass

def finite(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False

def audit_v15(report):
    """Audit estimand labels without altering the predeclared v1.5 gate."""
    try:
        if report["experiment_id"] != "retail-store-disjoint-transfer-v15":
            raise AuditError("wrong source experiment")
        m = report["metrics"]
        orig = m["original_v12_metrics"]
        weekday_day = m["weekday_median_last4_day_weighted_mae"]
        last_day = orig["day_weighted_mae"]["last_observed"]
        weekday_macro = m["weekday_median_last4_series_macro_mae"]
        last_macro = orig["series_macro_mae"]["last_observed"]
        macro_delta = m["weekday_median_minus_last_observed_series_macro_delta"]
        ci = m["weekday_median_minus_last_observed_store_cluster_ci95"]
        gate = report["primary_gate"]["conditional_store_transfer_gate_passed"]
    except (KeyError, TypeError) as exc:
        raise AuditError("missing v1.5 aggregate fields") from exc
    if any(not finite(x) or x < 0 for x in (weekday_day, last_day, weekday_macro, last_macro)):
        raise AuditError("invalid mean absolute error")
    if not finite(macro_delta) or not isinstance(ci, list) or len(ci) != 2 or not all(finite(x) for x in ci) or ci[0] > ci[1]:
        raise AuditError("invalid macro-delta interval")
    if type(gate) is not bool:
        raise AuditError("invalid preserved gate")
    if not math.isclose(weekday_macro-last_macro, macro_delta, rel_tol=0, abs_tol=1e-12):
        raise AuditError("macro-delta identity mismatch")
    day_delta = weekday_day-last_day
    return {
        "audit_class": "POST_HOC_AGGREGATE_ONLY_ESTIMAND_ALIGNMENT_NOT_NEW_FORECAST_EVIDENCE",
        "source_experiment": report["experiment_id"],
        "day_weighted_mae_delta_weekday_minus_last": day_delta,
        "series_macro_mae_delta_weekday_minus_last": macro_delta,
        "difference_day_weighted_minus_series_macro": day_delta-macro_delta,
        "reported_cluster_ci95": ci,
        "reported_cluster_ci95_estimand": "paired series-macro MAE difference, resampled by store",
        "day_weighted_store_cluster_ci95": "TBD: per-series observed-day counts and paired errors needed",
        "different_weighting_estimands": True,
        "preserved_predeclared_v15_gate_passed": gate,
        "interpretation": "The reported interval is NOT an interval for the day-weighted point MAE difference. No retrospective gate revision or new superiority claim.",
        "independent_temporal_confirmation": "TBD",
        "decision_value": "TBD",
        "maturity_change": "NONE",
    }

def percentile(sorted_values, q):
    pos = (len(sorted_values)-1)*q
    lo = int(pos)
    return sorted_values[lo]*(1-(pos-lo)) + sorted_values[min(lo+1, len(sorted_values)-1)]*(pos-lo)

def toy_cluster_intervals(store_records, reps=2000, seed=20261027):
    """FICTIONAL one-series-per-store example; never treat as v1.5 observations."""
    if type(reps) is not int or reps < 1 or type(seed) is not int or len(store_records) < 2:
        raise AuditError("invalid toy bootstrap settings")
    for days, delta in store_records:
        if type(days) is not int or not 1 <= days <= 7 or not finite(delta):
            raise AuditError("invalid fictional store record")
    rng = random.Random(seed)
    n = len(store_records)
    macro, day = [], []
    for _ in range(reps):
        draw = [store_records[rng.randrange(n)] for _ in range(n)]
        macro.append(math.fsum(delta for _, delta in draw)/n)
        day.append(math.fsum(days*delta for days, delta in draw)/sum(days for days, _ in draw))
    macro.sort()
    day.sort()
    return {
        "fictional_only": True,
        "series_macro_ci95": [percentile(macro, .025), percentile(macro, .975)],
        "day_weighted_ci95": [percentile(day, .025), percentile(day, .975)],
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit("refusing to overwrite existing evidence")
    result = audit_v15(json.loads(a.source.read_text(encoding="utf-8")))
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
