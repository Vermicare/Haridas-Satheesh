"""Fictional negative controls for WBI v1.1 matched-budget diagnostic; no EEG."""
import unittest
from dataclasses import dataclass
from wbi_matched_coverage_v11 import (
    ALPHAS, choose_alpha, git_blob, score, select_indices, wrong_acted
)


@dataclass(frozen=True)
class Row:
    y: int
    p1: float
    drift: float


def pc(r):
    return int(r.p1 >= 0.5), max(r.p1, 1 - r.p1)


class MatchedBudgetTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            Row(1, 0.9, 0.9), Row(0, 0.1, 0.1),
            Row(1, 0.8, 0.2), Row(0, 0.2, 0.8)
        ]

    def test_equal_budget_for_every_candidate(self):
        for a in ALPHAS:
            self.assertEqual(len(select_indices(self.rows, 2, a, pc)), 2)

    def test_test_labels_cannot_affect_action_selection(self):
        flipped = [Row(1-r.y, r.p1, r.drift) for r in self.rows]
        for a in ALPHAS:
            self.assertEqual(select_indices(self.rows, 2, a, pc),
                             select_indices(flipped, 2, a, pc))

    def test_unlabeled_rows_can_be_selected(self):
        class Unlabeled:
            def __init__(self, p1, drift):
                self.p1, self.drift = p1, drift
        unlabeled = [Unlabeled(r.p1, r.drift) for r in self.rows]
        self.assertEqual(select_indices(unlabeled, 2, 0.0, pc), (0, 1))

    def test_confidence_top_k(self):
        self.assertEqual(select_indices(self.rows, 2, 0.0, pc), (0, 1))

    def test_invalid_budget_rejected(self):
        for k in (-1, 0, 5):
            with self.assertRaises(ValueError):
                select_indices(self.rows, k, 0, pc)

    def test_negative_alpha_rejected(self):
        with self.assertRaises(ValueError):
            select_indices(self.rows, 2, -0.1, pc)

    def test_manual_risk_and_retention(self):
        got = score(self.rows, (0, 2), pc)
        self.assertEqual(got["incorrect_acted"], 0)
        self.assertEqual(got["incorrect_action_risk"], 0)
        self.assertEqual(got["correct_action_retention"], 0.5)

    def test_wrong_action_count(self):
        wrong = [Row(0, 0.9, 0.0), Row(1, 0.9, 0.0)]
        self.assertEqual(wrong_acted(wrong, (0, 1), pc), 1)

    def test_calibration_tie_prefers_simpler_baseline(self):
        self.assertEqual(choose_alpha(self.rows, 2, pc), 0.0)

    def test_git_blob_known_vector(self):
        self.assertEqual(git_blob(b"test\n"), "9daeafb9864cf43055ae93beb0afd6c7d144bfa4")


if __name__ == "__main__":
    unittest.main()
