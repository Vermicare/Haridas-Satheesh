"""Fictional-only, independent exhaustive-grid tests for v2.5 sales-floor bounds."""
import itertools
import json
import math
import random
import unittest
import retail_sales_floor_bounds_v25 as v25
import stockout_identification_bounds_v23 as v23


def doc(rows):
    return {"schema": v25.INPUT_SCHEMA, "rows": rows}


def censored(a, b, floor, key="1"):
    return {"key": key, "a": a, "b": b, "observed": False, "sales_floor": floor}


def observed(a, b, y, key="1"):
    return {"key": key, "a": a, "b": b, "observed": True, "y": y}


class FloorTests(unittest.TestCase):
    def test_exhaustive_integer_grid_exact_sharp_bounds(self):
        for a, b, floor in itertools.product(range(9), repeat=3):
            lo, hi = v25.row_bounds(a, b, floor)
            vals = [v23._delta(a, b, y) for y in range(floor, max(a, b, floor) + 11)]
            self.assertEqual((lo, hi), (min(vals), max(vals)), (a, b, floor))

    def test_zero_floor_reproduces_v23(self):
        for a, b in itertools.product(range(9), repeat=2):
            r = v25.evaluate(doc([censored(a, b, 0)]))
            self.assertEqual((r["sales_floor_lower"], r["sales_floor_upper"]),
                             (r["nonnegative_only_lower"], r["nonnegative_only_upper"]))

    def test_positive_sales_floor_can_identify_sign(self):
        r = v25.evaluate(doc([censored(1, 3, 4)]))
        self.assertEqual((r["nonnegative_only_lower"], r["nonnegative_only_upper"]), (-2, 2))
        self.assertEqual((r["sales_floor_lower"], r["sales_floor_upper"]), (2, 2))
        self.assertEqual(r["identification_decision"], "B_lower_MAE_for_all_admissible_outcomes")

    def test_no_censor_reproduces_exact_observed_difference(self):
        r = v25.evaluate(doc([observed(1, 3, 1), observed(1, 3, 3, "2")]))
        self.assertEqual((r["sales_floor_lower"], r["sales_floor_upper"]), (0, 0))
        self.assertEqual(r["observed_days"], 2)

    def test_random_mixed_bounds_nested(self):
        rng = random.Random(20261029)
        for _ in range(100):
            rows = []
            for j in range(30):
                a, b, y = (rng.randrange(0, 100) for _ in range(3))
                rows.append(observed(a, b, y, str(j)) if j % 3 == 0
                            else censored(a, b, y, str(j)))
            r = v25.evaluate(doc(rows))
            self.assertLessEqual(r["nonnegative_only_lower"] - 1e-10, r["sales_floor_lower"])
            self.assertLessEqual(r["sales_floor_upper"], r["nonnegative_only_upper"] + 1e-10)

    def test_reordered_rows_equivalent(self):
        rows = [observed(2, 5, 4), censored(4, 8, 7, "2"), censored(5, 2, 1, "3")]
        self.assertEqual(v25.evaluate(doc(rows)), v25.evaluate(doc(list(reversed(rows)))))

    def test_invalid_schema_and_missing_floor_fail_closed(self):
        for rows in ([{"key":"1","a":1,"b":2,"observed":False}],
                     [dict(censored(1, 2, 0), y=0)],
                     [dict(observed(1, 2, 0), sales_floor=0)],
                     [dict(censored(1, 2, 0), observed="false")]):
            with self.subTest(rows=rows), self.assertRaises((v25.FloorError, v23.ContractError)):
                v25.evaluate(doc(rows))

    def test_invalid_numeric_floors_rejected(self):
        for bad in (-1, float("nan"), float("inf"), True, 1e13):
            with self.subTest(bad=bad), self.assertRaises(v23.ContractError):
                v25.evaluate(doc([censored(1, 2, bad)]))

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(v23.ContractError):
            v25.evaluate(doc([censored(1, 2, 0), censored(2, 3, 1)]))

    def test_identifiers_never_emitted(self):
        r = v25.evaluate(doc([censored(1, 2, 2, "PRIVATE-SERIES-123")]))
        self.assertNotIn("PRIVATE-SERIES-123", json.dumps(r))
        self.assertTrue(r["no_censored_latent_demand_imputed"])

    def test_both_signs_and_ties(self):
        self.assertEqual(v25.evaluate(doc([observed(1, 2, 1)]))["identification_decision"],
                         "A_lower_MAE_for_all_admissible_outcomes")
        self.assertEqual(v25.evaluate(doc([observed(1, 2, 2)]))["identification_decision"],
                         "B_lower_MAE_for_all_admissible_outcomes")
        self.assertEqual(v25.evaluate(doc([censored(1, 2, 0)]))["identification_decision"],
                         "undetermined_including_ties")


if __name__ == "__main__":
    unittest.main()
