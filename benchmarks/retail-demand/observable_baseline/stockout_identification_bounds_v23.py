#!/usr/bin/env python3
"""Retail v2.3: sharp paired-MAE difference bounds under unknown stockout demand.

Standard-library-only research diagnostic. Fictional tests; no publisher scoring.
Not a causal estimate, confidence interval, forecast benchmark or lost-demand model.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

SCHEMA = "retail-stockout-paired-mae-bounds-v2.3"
INPUT_SCHEMA = "retail-stockout-bounds-input-v1"
MAX_BYTES = 5_000_000
MAX_ROWS = 100_000
MAX_MAGNITUDE = 1e12  # Numeric safety limit, NOT a scientific demand cap.

class ContractError(ValueError):
    pass


def _number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= MAX_MAGNITUDE:
        raise ContractError("invalid_nonnegative_finite_number")
    return float(value)


def _strict_load(raw):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ContractError("duplicate_json_key")
            result[k] = v
        return result
    def reject(_):
        raise ContractError("nonfinite_json_literal")
    try:
        return json.loads(raw, object_pairs_hook=unique, parse_constant=reject)
    except (ValueError, UnicodeError) as exc:
        raise ContractError("invalid_json") from exc


def _delta(a, b, y):
    return abs(a-y) - abs(b-y)


def _row_bounds(a, b, cap):
    # Piecewise-linear delta has kinks only at a and b. With no cap, it is
    # constant beyond max(a,b), so unbounded demand has FINITE delta bounds
    # even though each model's absolute error has no finite upper bound.
    candidates = [0.0]
    if cap is None:
        candidates.extend((a, b, max(a, b)))
    else:
        candidates.append(cap)
        candidates.extend(x for x in (a, b) if x <= cap)
    vals = [_delta(a, b, y) for y in candidates]
    return min(vals), max(vals)


def evaluate(doc):
    if not isinstance(doc, dict) or set(doc) != {"schema", "cap", "rows"} or doc["schema"] != INPUT_SCHEMA:
        raise ContractError("invalid_top_level_schema")
    cap = None if doc["cap"] is None else _number(doc["cap"])
    rows = doc["rows"]
    if not isinstance(rows, list) or not 0 < len(rows) <= MAX_ROWS:
        raise ContractError("invalid_row_count")
    seen = set(); lowers = []; uppers = []; observed = []; censored = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) not in ({"key","a","b","observed"}, {"key","a","b","observed","y"}):
            raise ContractError("invalid_row_schema")
        key = row["key"]
        if not isinstance(key, str) or not 0 < len(key) <= 120 or key in seen:
            raise ContractError("invalid_or_duplicate_key")
        seen.add(key)
        a, b = _number(row["a"]), _number(row["b"])
        if type(row["observed"]) is not bool:
            raise ContractError("invalid_observation_flag")
        if row["observed"]:
            if "y" not in row:
                raise ContractError("missing_observed_outcome")
            y = _number(row["y"])
            if cap is not None and y > cap:
                raise ContractError("observed_outcome_exceeds_declared_global_cap")
            d = _delta(a, b, y)
            lowers.append(d); uppers.append(d); observed.append(d)
        else:
            if "y" in row:
                raise ContractError("censored_outcome_must_be_unknown")
            lo, hi = _row_bounds(a, b, cap)
            lowers.append(lo); uppers.append(hi); censored += 1
    n = len(rows)
    lo, hi = math.fsum(lowers)/n, math.fsum(uppers)/n
    if lo > hi + 1e-9:
        raise ContractError("invalid_bounds")
    decision = ("A_lower_MAE_for_all_admissible_outcomes" if hi < 0 else
                "B_lower_MAE_for_all_admissible_outcomes" if lo > 0 else
                "undetermined_including_ties")
    return {
        "schema": SCHEMA, "fictional_or_external_input_not_authenticated": True,
        "outcome_assumption": "all demand >= 0" if cap is None else "all demand in [0, cap]",
        "cap": cap, "total_days": n, "observed_days": len(observed),
        "censored_days": censored, "censored_fraction": censored/n,
        "observed_only_paired_mae_delta_A_minus_B": (math.fsum(observed)/len(observed) if observed else None),
        "full_period_paired_mae_delta_lower": lo,
        "full_period_paired_mae_delta_upper": hi,
        "identification_decision": decision,
        "uncertainty_type": "sharp logical identification interval; NOT a statistical confidence interval",
        "latent_demand_measured": False,
        "individual_model_full_period_mae": "TBD",
        "statistical_sampling_uncertainty": "TBD",
        "independent_data_validation": "TBD",
        "real_inventory_decision_value": "TBD",
    }


def score_file(input_path, output_path):
    path = Path(input_path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ContractError("invalid_or_oversized_input")
    raw = path.read_bytes()
    result = evaluate(_strict_load(raw.decode("utf-8")))
    result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    result["python_version"] = sys.version.split()[0]
    result["code_version"] = SCHEMA
    # Exclusive creation; do not replace historical evidence.
    with open(output_path, "x", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    return result


class ContractTests(unittest.TestCase):
    def row(self, a, b, *, y=None, key="1"):
        r = {"key":key,"a":a,"b":b,"observed":y is not None}
        if y is not None: r["y"] = y
        return r
    def doc(self, rows, cap=None):
        return {"schema":INPUT_SCHEMA,"cap":cap,"rows":rows}
    def test_no_censor_exact(self):
        r = evaluate(self.doc([self.row(1,2,y=1),self.row(3,1,y=2,key="2")]))
        self.assertEqual((r["full_period_paired_mae_delta_lower"],r["full_period_paired_mae_delta_upper"]),(-0.5,-0.5))
    def test_two_unknowns_can_reverse_observed_winner(self):
        r = evaluate(self.doc([self.row(1,2,y=1),self.row(1,2,key="2"),self.row(1,2,key="3")]))
        self.assertEqual((r["full_period_paired_mae_delta_lower"],r["full_period_paired_mae_delta_upper"]),(-1.0,1.0/3.0))
        self.assertEqual(r["identification_decision"],"undetermined_including_ties")
    def test_censored_alone_is_undetermined(self):
        r = evaluate(self.doc([self.row(1,2)]))
        self.assertEqual((r["full_period_paired_mae_delta_lower"],r["full_period_paired_mae_delta_upper"]),(-1,1))
        self.assertIsNone(r["observed_only_paired_mae_delta_A_minus_B"])
    def test_finite_cap_narrows_bounds(self):
        r = evaluate(self.doc([self.row(1,2)],cap=0))
        self.assertEqual((r["full_period_paired_mae_delta_lower"],r["full_period_paired_mae_delta_upper"]),(-1,-1))
    def test_kinks_inside_cap(self):
        self.assertEqual(_row_bounds(2,5,3),(-3, -1))
    def test_no_cap_has_finite_paired_bounds(self):
        self.assertEqual(_row_bounds(1,3,None),(-2,2))
    def test_zero_delta(self):
        r=evaluate(self.doc([self.row(3,3)]))
        self.assertEqual((r["full_period_paired_mae_delta_lower"],r["full_period_paired_mae_delta_upper"]),(0,0))
    def test_invalid_or_duplicate_rows(self):
        for rows in ([self.row(1,2),self.row(1,2)], [self.row(float("nan"),2)], [self.row(-1,2)], [dict(self.row(1,2),y=0)], [dict(self.row(1,2),observed="false")]):
            with self.subTest(rows=rows), self.assertRaises(ContractError):evaluate(self.doc(rows))
    def test_cap_rejects_impossible_observed(self):
        with self.assertRaises(ContractError):evaluate(self.doc([self.row(1,2,y=3)],cap=2))
    def test_strict_json_duplicate_key_and_nan(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.subTest(raw=raw),self.assertRaises(ContractError):_strict_load(raw)
    def test_all_outputs_aggregate_no_identifiers(self):
        r=evaluate(self.doc([self.row(1,2,key="PRIVATE-ID-DO-NOT-PRINT")]))
        self.assertNotIn("PRIVATE-ID-DO-NOT-PRINT",json.dumps(r))
    def test_A_and_B_decisions(self):
        a=evaluate(self.doc([self.row(1,2,y=1)]))
        b=evaluate(self.doc([self.row(1,2,y=2)]))
        self.assertEqual(a["identification_decision"],"A_lower_MAE_for_all_admissible_outcomes")
        self.assertEqual(b["identification_decision"],"B_lower_MAE_for_all_admissible_outcomes")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args == ["selftest"]:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests))
        return 0 if result.wasSuccessful() else 1
    if len(args)==3 and args[0]=="score":
        try:
            score_file(args[1],args[2])
        except (OSError, ValueError, UnicodeError) as exc:
            print("error:"+str(exc),file=sys.stderr)
            return 2
        return 0
    print("usage: stockout_identification_bounds_v23.py selftest | score INPUT.json NEW_OUTPUT.json",file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
