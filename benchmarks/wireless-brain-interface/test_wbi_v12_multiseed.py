"""Fictional-only regression tests; never validate EEG or an online policy."""
import unittest
from pathlib import Path
from wbi_matched_coverage_v11 import frozen_module
from wbi_v12_multiseed import run

FROZEN = Path(__file__).with_name("synthetic_evaluator.py")


class MultiSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = frozen_module(FROZEN)

    def test_reproducible(self):
        self.assertEqual(run(self.frozen, 3), run(self.frozen, 3))

    def test_pair_count(self):
        self.assertEqual(len(run(self.frozen, 3)["records"]), 3)

    def test_distinct_seeds(self):
        rows = run(self.frozen, 4)["records"]
        self.assertEqual(len({s for r in rows for s in (r["cal_seed"], r["test_seed"])}), 8)

    def test_calibration_alpha_allowed(self):
        self.assertTrue(all(
            r["alpha"] in (0.0, 0.05, 0.10, 0.20, 0.40, 0.80)
            for r in run(self.frozen, 4)["records"]
        ))

    def test_identity_delta(self):
        self.assertTrue(all(
            r["delta_wrong"] == r["drift_wrong"] - r["baseline_wrong"]
            for r in run(self.frozen, 5)["records"]
        ))

    def test_zero_pairs_rejected(self):
        with self.assertRaises(ValueError):
            run(self.frozen, 0)

    def test_count_partition(self):
        x = run(self.frozen, 9)
        a = x["aggregate"]
        self.assertEqual(
            a["drift_better_pairs"] + a["tie_pairs"] + a["drift_worse_pairs"], 9
        )

    def test_seed_base(self):
        r = run(self.frozen, 2)["records"]
        self.assertEqual(
            (r[0]["cal_seed"], r[0]["test_seed"],
             r[1]["cal_seed"], r[1]["test_seed"]),
            (100000, 100001, 100002, 100003)
        )


if __name__ == "__main__":
    unittest.main()
