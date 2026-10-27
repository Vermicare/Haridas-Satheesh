"""Fictional-only regressions: no device data or performance claims."""
import unittest
from collections import Counter
from order_confounding_v1 import balanced_orders, fixed_orders, simulate, CONDITIONS


class OrderConfoundingTests(unittest.TestCase):
    def test_complete_counterbalance(self):
        orders = balanced_orders()
        self.assertEqual(len(orders), 6)
        self.assertEqual(len(set(orders)), 6)
        for pos in range(3):
            self.assertEqual(Counter(order[pos] for order in orders),
                             Counter({condition: 2 for condition in CONDITIONS}))

    def test_schedule_seed_reproducible(self):
        self.assertEqual(balanced_orders(11), balanced_orders(11))

    def test_fixed_order_creates_false_prototype_advantage(self):
        r = simulate(fixed_orders())
        self.assertAlmostEqual(r['prototype_minus_ambient_c'], -0.4, places=10)
        self.assertFalse(r['performance_claim_permitted'])

    def test_balancing_cancels_linear_drift_under_no_effect(self):
        r = simulate(balanced_orders())
        self.assertAlmostEqual(r['prototype_minus_ambient_c'], 0.0, places=10)

    def test_balancing_recovers_assumed_true_effect_in_linear_model(self):
        r = simulate(balanced_orders(), prototype_effect_c=-0.6)
        self.assertAlmostEqual(r['prototype_minus_ambient_c'], -0.6, places=10)

    def test_balancing_does_not_guarantee_carryover_control(self):
        r = simulate(balanced_orders(), carryover_after_prototype_c=-0.6)
        self.assertGreater(abs(r['prototype_minus_ambient_c']), 0.01)

    def test_rejects_incomplete_blocks(self):
        with self.assertRaises(ValueError):
            simulate([CONDITIONS] * 5)


if __name__ == '__main__':
    unittest.main()
