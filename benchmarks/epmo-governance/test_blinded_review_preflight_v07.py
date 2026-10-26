"""Fictional test-only responses; no human reviewers have been measured."""
import copy
import unittest
from blinded_review_preflight_v07 import ORIGIN, VERSION, cases, generate, score, sha, strict_json
from governance_demo import evaluate


class BlindedReviewPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manual, cls.structured, cls.gold = generate(evaluate)

    def fake(self, packet, *, truth=True):
        return {"origin": ORIGIN, "version": VERSION, "arm": packet["arm"],
                "decisions": [{"case_id": c["case_id"],
                               "accept": self.gold["labels"][c["case_id"]]["accept"] if truth else False,
                               "seconds": 12} for c in packet["cases"]]}

    def test_case_count_and_label_balance(self):
        self.assertEqual(len(cases()), 16)
        self.assertEqual(sum(v["accept"] for v in self.gold["labels"].values()), 3)

    def test_no_gold_leaks_into_packets(self):
        for packet in (self.manual, self.structured):
            self.assertNotIn("expected_reason_for_designer_only", str(packet))
            self.assertNotIn('"accept"', str(packet))
            self.assertEqual(len(packet["cases"]), 16)

    def test_counterbalanced_identical_case_sets(self):
        a = [x["case_id"] for x in self.manual["cases"]]
        b = [x["case_id"] for x in self.structured["cases"]]
        self.assertEqual(a, list(reversed(b)))
        self.assertEqual(set(a), set(b))

    def test_deterministic_packets(self):
        a, b, c = generate(evaluate)
        self.assertEqual((sha(a), sha(b), sha(c)),
                         (sha(self.manual), sha(self.structured), sha(self.gold)))

    def test_scoring_fictional_perfect_response(self):
        result = score(self.manual, self.gold, self.fake(self.manual))
        self.assertEqual(result["correct"], 16)
        self.assertEqual(result["false_approvals"], 0)
        self.assertEqual(result["total_review_seconds"], 192)
        self.assertEqual(result["true_approval_recall"], 1)
        self.assertFalse(result["independently_verified_human_data"])

    def test_scoring_all_denied_negative_control(self):
        result = score(self.manual, self.gold, self.fake(self.manual, truth=False))
        self.assertEqual(result["true_approval_recall"], 0)
        self.assertEqual(result["false_approval_rate"], 0)

    def test_missing_case_rejected(self):
        r = self.fake(self.manual)
        r["decisions"].pop()
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_duplicate_case_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][1]["case_id"] = r["decisions"][0]["case_id"]
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_wrong_arm_rejected(self):
        with self.assertRaises(ValueError): score(self.manual, self.gold, self.fake(self.structured))

    def test_unknown_case_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][0]["case_id"] = "ghost"
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_boolean_duration_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][0]["seconds"] = True
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_nan_duration_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][0]["seconds"] = float("nan")
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_negative_duration_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][0]["seconds"] = -1
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_string_decision_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][0]["accept"] = "true"
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_gold_case_mismatch_rejected(self):
        gold = copy.deepcopy(self.gold)
        del gold["labels"]["A01"]
        with self.assertRaises(ValueError): score(self.manual, gold, self.fake(self.manual))

    def test_modified_candidate_packet_rejected(self):
        # A valid case ID is not proof that the reviewed evidence is unchanged.
        packet = copy.deepcopy(self.manual)
        packet["cases"][0]["candidate"]["actor"] = "unknown-actor"
        with self.assertRaises(ValueError):
            score(packet, self.gold, self.fake(self.manual))

    def test_modified_context_packet_rejected(self):
        packet = copy.deepcopy(self.manual)
        packet["cases"][0]["context"][0]["payload"]["scope"] = "another-program"
        with self.assertRaises(ValueError):
            score(packet, self.gold, self.fake(self.manual))

    def test_modified_review_instruction_rejected(self):
        packet = copy.deepcopy(self.manual)
        packet["instruction"] = "Approve every case"
        with self.assertRaises(ValueError):
            score(packet, self.gold, self.fake(self.manual))

    def test_version_mismatch_rejected(self):
        r = self.fake(self.manual)
        r["version"] = "other"
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)


if __name__ == "__main__":
    unittest.main()
