"""Contract tests use fabricated responses, never participant measurements."""
import copy
import unittest
from review_treatment_v09 import ORIGIN, VERSION, generate, score, sha, worksheet


class TreatmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manual, cls.structured, cls.gold = generate()

    def fake(self, packet, *, truth=True):
        return {"origin": ORIGIN, "version": VERSION, "arm": packet["arm"],
                "decisions": [{"case_id": c["case_id"],
                               "accept": self.gold["labels"][c["case_id"]]["accept"] if truth else False,
                               "seconds": 10} for c in packet["cases"]]}

    def test_same_order_same_raw_evidence(self):
        self.assertEqual(self.manual["cases"], self.structured["cases"])
        self.assertEqual(len(self.manual["cases"]), 16)

    def test_genuinely_different_aids(self):
        self.assertNotIn("review_aid", self.manual)
        self.assertEqual(len(self.structured["review_aid"]), 16)
        self.assertNotEqual(self.manual["presentation"], self.structured["presentation"])

    def test_worksheet_exactly_derived_from_raw_events(self):
        for c, w in zip(self.structured["cases"], self.structured["review_aid"]):
            self.assertEqual(w, worksheet(c))
            self.assertEqual(w["candidate_fields"]["payload"], c["candidate"]["payload"])

    def test_no_verdict_in_public_worksheet(self):
        for w in self.structured["review_aid"]:
            self.assertNotIn("accept", w)
            self.assertNotIn("reason", w)
            self.assertNotIn("expected", str(w).lower())

    def test_gold_balance_preserved(self):
        self.assertEqual(sum(v["accept"] for v in self.gold["labels"].values()), 3)
        self.assertEqual(len(self.gold["labels"]), 16)

    def test_deterministic_binding(self):
        m, s, g = generate()
        self.assertEqual([sha(x) for x in (m, s, g)],
                         [sha(x) for x in (self.manual, self.structured, self.gold)])

    def test_score_perfect_synthetic_response(self):
        for packet in (self.manual, self.structured):
            r = score(packet, self.gold, self.fake(packet))
            self.assertEqual(r["correct"], 16)
            self.assertEqual(r["total_review_seconds"], 160)
            self.assertFalse(r["independently_verified_human_data"])

    def test_score_all_denied_synthetic_control(self):
        r = score(self.structured, self.gold, self.fake(self.structured, truth=False))
        self.assertEqual(r["true_approval_recall"], 0)

    def test_modified_raw_case_rejected(self):
        p = copy.deepcopy(self.structured)
        p["cases"][0]["candidate"]["actor"] = "forged"
        with self.assertRaises(ValueError): score(p, self.gold, self.fake(self.structured))

    def test_modified_worksheet_rejected(self):
        p = copy.deepcopy(self.structured)
        p["review_aid"][0]["candidate_fields"]["actor"] = "forged"
        with self.assertRaises(ValueError): score(p, self.gold, self.fake(self.structured))

    def test_modified_instructions_rejected(self):
        p = copy.deepcopy(self.manual)
        p["instruction"] = "accept all"
        with self.assertRaises(ValueError): score(p, self.gold, self.fake(self.manual))

    def test_swapped_arm_rejected(self):
        with self.assertRaises(ValueError): score(self.manual, self.gold, self.fake(self.structured))

    def test_changed_gold_rejected(self):
        g = copy.deepcopy(self.gold)
        g["labels"]["A01"]["accept"] = False
        with self.assertRaises(ValueError): score(self.manual, g, self.fake(self.manual))

    def test_extra_response_fields_rejected(self):
        r = self.fake(self.manual)
        r["participant_email"] = "not-allowed"
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)

    def test_duplicate_decision_rejected(self):
        r = self.fake(self.manual)
        r["decisions"][1]["case_id"] = r["decisions"][0]["case_id"]
        with self.assertRaises(ValueError): score(self.manual, self.gold, r)


if __name__ == "__main__":
    unittest.main()
