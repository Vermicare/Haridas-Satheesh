"""Fictional, tiny target-key fixtures only. No publisher labels/data."""
import csv
import io
import math
import unittest
from unittest.mock import patch

import freshretail_lt_full_target_gate_v27 as gate


class FullTargetFictionalTests(unittest.TestCase):
    def setUp(self):
        self.targets = [
            {"store_id": 1, "product_id": 3, "dt": "2025-07-14"},
            {"store_id": 1, "product_id": 3, "dt": "2025-07-15"},
        ]
        self.predictions = [dict(row, prediction="0") for row in self.targets]

    def check(self, targets=None, predictions=None):
        return gate.validate(self.targets if targets is None else targets,
                             self.predictions if predictions is None else predictions,
                             expected=2)

    def test_complete_coverage_only_not_official_score(self):
        r = self.check()
        self.assertEqual(r["coverage"], "PASS_FULL_TARGET_ONLY")
        self.assertFalse(r["official_leaderboard_comparable"])
        self.assertEqual(r["scored_rows"], "TBD")

    def test_row_order_independent(self):
        self.assertEqual(self.check(), self.check(predictions=list(reversed(self.predictions))))

    def test_missing_prediction_fails(self):
        with self.assertRaisesRegex(gate.CoverageError, "missing prediction"):
            self.check(predictions=self.predictions[:1])

    def test_extra_prediction_fails(self):
        extra = dict(self.predictions[0], product_id=5)
        with self.assertRaisesRegex(gate.CoverageError, "absent"):
            self.check(predictions=self.predictions + [extra])

    def test_duplicate_prediction_fails(self):
        with self.assertRaisesRegex(gate.CoverageError, "duplicate prediction"):
            self.check(predictions=self.predictions + [self.predictions[0]])

    def test_duplicate_target_fails(self):
        with self.assertRaisesRegex(gate.CoverageError, "duplicate evaluation"):
            self.check(targets=[self.targets[0], self.targets[0]])

    def test_incomplete_target_fails(self):
        with self.assertRaisesRegex(gate.CoverageError, "target count"):
            self.check(targets=self.targets[:1])

    def test_outside_horizon_fails(self):
        wrong = dict(self.predictions[0], dt="2025-07-21")
        with self.assertRaisesRegex(gate.CoverageError, "horizon"):
            self.check(predictions=[wrong, self.predictions[1]])

    def test_noncanonical_date_fails(self):
        wrong = dict(self.predictions[0], dt="2025-7-14")
        with self.assertRaises(gate.CoverageError):
            self.check(predictions=[wrong, self.predictions[1]])

    def test_bad_identifiers_fail(self):
        for bad in ("01", "-1", "1.0", " 1", "1" * 19, None, True):
            with self.subTest(bad=bad), self.assertRaises(gate.CoverageError):
                self.check(predictions=[dict(self.predictions[0], store_id=bad), self.predictions[1]])

    def test_nonfinite_negative_and_malformed_fail(self):
        for bad in ("nan", "inf", "-inf", "-0.1", "bad", "", None, True, math.inf):
            with self.subTest(bad=bad), self.assertRaises(gate.CoverageError):
                self.check(predictions=[dict(self.predictions[0], prediction=bad), self.predictions[1]])

    def test_header_order_and_extra_column_fail(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "pred.csv"
            p.write_text("prediction,store_id,product_id,dt\n0,1,3,2025-07-14\n")
            with self.assertRaisesRegex(gate.CoverageError, "header"):
                list(gate._predictions(p))
            p.write_text("store_id,product_id,dt,prediction\n1,3,2025-07-14,0,EXTRA\n")
            with self.assertRaisesRegex(gate.CoverageError, "extra CSV"):
                list(gate._predictions(p))

    def test_no_raw_identifiers_in_result(self):
        s = str(self.check())
        self.assertNotIn("store_id", s)
        self.assertNotIn("product_id", s)
        self.assertNotIn("2025-07-14", s)

    def test_eval_byte_pin_fails_before_parquet_read(self):
        with patch.object(gate, "_verify_eval", side_effect=gate.CoverageError("EVAL byte pin mismatch")), \
             patch.object(gate, "_targets") as target_reader:
            with self.assertRaisesRegex(gate.CoverageError, "pin"):
                gate.run("/fictional/eval", "/fictional/pred")
            target_reader.assert_not_called()

    def test_existing_512_cohort_cannot_pass_full_target_gate(self):
        with self.assertRaisesRegex(gate.CoverageError, "target count"):
            gate.validate(self.targets, self.predictions, expected=gate.EXPECTED_TARGETS)


if __name__ == "__main__":
    unittest.main()
