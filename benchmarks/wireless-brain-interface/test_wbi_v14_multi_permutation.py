"""WBI v1.4 synthetic-only repeated-permutation regression tests."""
import unittest
from pathlib import Path
from wbi_matched_coverage_v11 import frozen_module
from wbi_v14_multi_permutation import evaluate, FROZEN_BLOB

class RepeatedPermutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = frozen_module(Path(__file__).with_name('synthetic_evaluator.py'))

    def test_determinism(self):
        self.assertEqual(evaluate(self.frozen, 3, 2), evaluate(self.frozen, 3, 2))

    def test_repeat_seeds_are_distinct(self):
        self.assertNotEqual(1400000 + 20000*0 + 2*2, 1400000 + 20000*1 + 2*2)

    def test_baseline_is_identical_across_repeats(self):
        a = evaluate(self.frozen, 5, 3)
        self.assertEqual({r['baseline_wrong'] for r in a['replicates']}, {a['original']['baseline_wrong']})

    def test_exact_action_budget_and_counts(self):
        a = evaluate(self.frozen, 5, 3)
        self.assertEqual(a['actions_per_pair'], 120)
        for r in a['replicates']:
            self.assertEqual(r['both_better'] + r['both_tied'] + r['both_worse'], 5)
            self.assertEqual(r['test_only_better'] + r['test_only_tied'] + r['test_only_worse'], 5)

    def test_original_frozen_200_pair_parity(self):
        a = evaluate(self.frozen, 200, 2)
        self.assertEqual((a['original']['baseline_wrong'], a['original']['candidate_wrong']), (3716, 3645))
        self.assertEqual((a['original']['better'], a['original']['tied'], a['original']['worse']), (76, 86, 38))

    def test_descriptive_summary_matches_replicates(self):
        a = evaluate(self.frozen, 6, 3)
        both = [r['both_delta_wrong'] for r in a['replicates']]
        self.assertEqual(a['summary']['permuted_both_delta_min'], min(both))
        self.assertEqual(a['summary']['permuted_both_delta_max'], max(both))

    def test_repeated_permutations_vary(self):
        a = evaluate(self.frozen, 15, 4)
        self.assertGreater(len({r['both_wrong'] for r in a['replicates']}), 1)

    def test_evidence_flags(self):
        a = evaluate(self.frozen, 1, 2)
        self.assertEqual(a['source_evaluator_git_blob'], FROZEN_BLOB)
        self.assertFalse(a['labels_or_confidence_changed'])
        self.assertFalse(a['maturity_advanced'])
        self.assertEqual(a['unknowns']['real_eeg'], 'TBD')

    def test_invalid_pairs_rejected(self):
        for v in (0, -1, 1001, True, 1.5):
            with self.subTest(v=v), self.assertRaises(ValueError):
                evaluate(self.frozen, v, 2)

    def test_invalid_repeats_rejected(self):
        for v in (0, 1, 101, True, 2.5):
            with self.subTest(v=v), self.assertRaises(ValueError):
                evaluate(self.frozen, 2, v)

    def test_work_budget_rejected(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            evaluate(self.frozen, 1000, 5)

if __name__ == '__main__':
    unittest.main()
