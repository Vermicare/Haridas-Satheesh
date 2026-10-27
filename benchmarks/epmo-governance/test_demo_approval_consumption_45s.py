import unittest
from demo_approval_consumption_45s import demonstration


class DemonstrationTests(unittest.TestCase):
    def test_deterministic_and_no_real_actions(self):
        self.assertEqual(demonstration(), demonstration())
        self.assertEqual(demonstration()["external_actions"], 0)

    def test_consumed_retry_and_rejected_change(self):
        x = demonstration()
        self.assertEqual(x["outcomes"], ["consumed", "idempotent", "rejected"])
        self.assertEqual(x["changed_reason"], "already_consumed")
        self.assertEqual(x["receipts"], 1)
