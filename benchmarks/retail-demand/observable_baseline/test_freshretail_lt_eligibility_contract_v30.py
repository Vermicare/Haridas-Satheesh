"""Adversarial fictional mask-contract tests; no publisher EVAL labels or private data."""
import copy
import unittest

from freshretail_lt_eligibility_contract_v30 import MaskContractError, audit


class FictionalEligibilityContractTests(unittest.TestCase):
    def setUp(self):
        self.targets = [
            {"store_id": 1, "product_id": 2, "dt": "2025-07-14", "stock_hour6_22_cnt": 0},
            {"store_id": 1, "product_id": 2, "dt": "2025-07-15", "stock_hour6_22_cnt": 3},
            {"store_id": 1, "product_id": 3, "dt": "2025-07-14", "stock_hour6_22_cnt": 0},
            {"store_id": 1, "product_id": 3, "dt": "2025-07-15", "stock_hour6_22_cnt": 2},
        ]
        self.predictions = [{k: row[k] for k in ("store_id", "product_id", "dt")}
                            | {"prediction": "0.25"} for row in self.targets]
        self.psd = [
            {"store_id": 1, "product_id": 2, "psd": "0"},
            {"store_id": 1, "product_id": 3, "psd": "-0.25"},
        ]

    def run_audit(self, targets=None, predictions=None, psd=None, expected=4):
        return audit(self.targets if targets is None else targets,
                     self.predictions if predictions is None else predictions,
                     self.psd if psd is None else psd, expected=expected)

    def test_four_mask_categories_and_per_day(self):
        r = self.run_audit()
        self.assertEqual((r["eligible_rows"], r["excluded_psd"],
                          r["excluded_stockout"], r["excluded_both"]), (1, 1, 1, 1))
        self.assertEqual(r["target_rows"], 4)
        self.assertEqual(r["per_day"]["2025-07-14"]["eligible"], 1)
        self.assertEqual(r["per_day"]["2025-07-15"]["excluded_both"], 1)
        self.assertFalse(r["official_leaderboard_comparable"])
        self.assertEqual(r["publisher_reference_equivalence"], "TBD")
        self.assertEqual(r["metrics"], "TBD")
        self.assertFalse(r["eval_sales_labels_read"])
        self.assertTrue(r["eval_stockout_mask_read"])

    def test_order_invariant(self):
        self.assertEqual(self.run_audit(), self.run_audit(
            list(reversed(self.targets)), list(reversed(self.predictions)),
            list(reversed(self.psd))))

    def test_missing_psd_reference_fails(self):
        with self.assertRaisesRegex(MaskContractError, "series mismatch"):
            self.run_audit(psd=self.psd[:1])

    def test_extra_psd_reference_fails(self):
        with self.assertRaisesRegex(MaskContractError, "series mismatch"):
            self.run_audit(psd=self.psd + [
                {"store_id": 5, "product_id": 5, "psd": 1}])

    def test_duplicate_psd_reference_fails(self):
        with self.assertRaisesRegex(MaskContractError, "duplicate"):
            self.run_audit(psd=self.psd + [self.psd[0]])

    def test_nonfinite_psd_fails(self):
        for bad in ("nan", "inf", "-inf", None, True, " 1"):
            with self.subTest(bad=bad), self.assertRaisesRegex(MaskContractError, "psd"):
                rows = copy.deepcopy(self.psd)
                rows[0]["psd"] = bad
                self.run_audit(psd=rows)

    def test_stockout_count_rejects_malformed(self):
        for bad in (None, True, 1.5, "1.0", "-1", "01", "", " 0"):
            with self.subTest(bad=bad), self.assertRaises(MaskContractError):
                rows = copy.deepcopy(self.targets)
                rows[0]["stock_hour6_22_cnt"] = bad
                self.run_audit(targets=rows)

    def test_stockout_count_rejects_out_of_range(self):
        for bad in (-1, 25, "25"):
            with self.subTest(bad=bad), self.assertRaisesRegex(MaskContractError, "bounds"):
                rows = copy.deepcopy(self.targets)
                rows[0]["stock_hour6_22_cnt"] = bad
                self.run_audit(targets=rows)

    def test_missing_stockout_field_fails(self):
        rows = copy.deepcopy(self.targets)
        del rows[0]["stock_hour6_22_cnt"]
        with self.assertRaisesRegex(MaskContractError, "fields"):
            self.run_audit(targets=rows)

    def test_eval_answer_fields_forbidden(self):
        for field in ("sale_amount", "hours_sale", "hours_stock_status", "psd"):
            with self.subTest(field=field), self.assertRaisesRegex(MaskContractError, "answer"):
                rows = copy.deepcopy(self.targets)
                rows[0][field] = 100
                self.run_audit(targets=rows)

    def test_prediction_coverage_required(self):
        with self.assertRaisesRegex(MaskContractError, "coverage"):
            self.run_audit(predictions=self.predictions[:-1])

    def test_duplicate_target_fails(self):
        rows = copy.deepcopy(self.targets)
        rows[3] = copy.deepcopy(rows[0])
        with self.assertRaisesRegex(MaskContractError, "coverage"):
            self.run_audit(targets=rows)

    def test_original_512_cohort_cannot_pass(self):
        with self.assertRaisesRegex(MaskContractError, "coverage"):
            self.run_audit(expected=70_000)

    def test_psd_reference_extra_answer_field_fails(self):
        rows = copy.deepcopy(self.psd)
        rows[0]["sale_amount"] = 12
        with self.assertRaisesRegex(MaskContractError, "fields"):
            self.run_audit(psd=rows)

    def test_output_contains_no_raw_identifiers_or_labels(self):
        s = str(self.run_audit())
        self.assertNotIn("store_id", s)
        self.assertNotIn("product_id", s)
        self.assertNotIn("sale_amount", s)
        self.assertNotIn("0.25", s)

    def test_stockout_nonzero_excludes_even_if_psd_zero(self):
        r = self.run_audit()
        self.assertEqual(r["per_day"]["2025-07-15"]["excluded_stockout"], 1)


if __name__ == "__main__":
    unittest.main()
