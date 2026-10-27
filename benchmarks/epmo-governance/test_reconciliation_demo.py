"""Executable short-demo acceptance checks; synthetic inputs only."""
import copy
import json
import unittest
from pathlib import Path

from demo_reconciliation_45s import demonstration


class DemonstrationTests(unittest.TestCase):
    def setUp(self):
        self.scenario = json.loads(Path(__file__).with_name("synthetic_scenario.json").read_text(encoding="utf-8"))

    def test_positive_and_injected_negative_control(self):
        report = demonstration(self.scenario)
        self.assertTrue(report["positive_reconciled"])
        self.assertTrue(report["negative_control_detected"])
        self.assertEqual((report["accepted_executions"], report["corrected_receipts"]), (1, 1))
        self.assertEqual(report["external_actions"], 0)
        self.assertFalse(report["identity_authenticated"])
        self.assertFalse(report["durable_policy_enforced"])

    def test_nonfictional_origin_rejected(self):
        altered = copy.deepcopy(self.scenario)
        altered["origin"] = "PHYSICAL"
        with self.assertRaises(ValueError):
            demonstration(altered)


if __name__ == "__main__":
    unittest.main()
