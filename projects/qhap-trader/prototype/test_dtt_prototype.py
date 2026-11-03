"""Synthetic invariant tests; NOT a trading-performance test."""
import unittest
from dtt_prototype import Plan, State, action, scan

class TestDTT(unittest.TestCase):
    def setUp(self):
        self.plans = [
            Plan("breakout", "buy_above", 101.0, 1.0, 2),
            Plan("reversal", "buy_below", 98.0, 1.0, 1),
            Plan("loss_exit", "exit_below", 99.0, 1.0, 1),
        ]

    def test_shock_switches_only_threshold_policy(self):
        s = scan(self.plans, State(100, 1.3), [0, 120])
        self.assertEqual(s[0]["switching_mass"], 0)
        self.assertEqual(s[1]["switching_mass"], 0.5)
        self.assertEqual(s[1]["new_buy_activation_mass"], 0.5)

    def test_far_shock_below_can_trigger_exit(self):
        s = scan(self.plans, State(100, 1.3), [-150])[0]
        self.assertEqual(s["switching_mass"], 0.25)
        self.assertEqual(s["new_exit_activation_mass"], 0.25)

    def test_volume_gate_disables_all(self):
        s = scan(self.plans, State(100, 0.3), [-300, 0, 300])
        self.assertTrue(all(x["switching_mass"] == 0 for x in s))

    def test_weight_scale_is_invariant(self):
        same = [Plan(p.name, p.rule, p.threshold, p.min_relative_volume, p.weight*17) for p in self.plans]
        self.assertEqual(scan(same, State(100, 1.3), [0, 120]), scan(self.plans, State(100, 1.3), [0, 120]))

    def test_no_plans_and_bad_weights_rejected(self):
        with self.assertRaises(ValueError): scan([], State(100, 1), [0])
        with self.assertRaises(ValueError): scan([Plan("a", "buy_above", 101, 1, 0)], State(100, 1), [0])

    def test_invalid_shock_rejected(self):
        with self.assertRaises(ValueError): scan(self.plans, State(100, 1), [-20000])

    def test_policy_action_by_threshold(self):
        self.assertEqual(action(self.plans[0], State(100, 1.2)), 0)
        self.assertEqual(action(self.plans[0], State(101, 1.2)), 1)

if __name__ == "__main__": unittest.main()
