"""Fictional metadata tests; not real EEG benchmark evidence."""
import copy
import unittest
from bnci2a_split_preflight import build, validate


def fixture():
    return {"dataset": "BNCI2014_001", "trials": [
        {"subject": s, "session": session, "run": run,
         "trial_id": f"fictional-S{s:02d}-{session}-R{run:02d}-E{i:02d}"}
        for s in range(1, 10) for session in ("T", "E")
        for run in range(1, 7) for i in range(48)]}


class TestSplitPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = fixture()

    def test_full_coverage_and_fold_sizes(self):
        result = build(self.good)
        self.assertEqual(result["expected_trials"], 5184)
        self.assertEqual(len(result["folds"]), 18)
        for fold in result["folds"]:
            self.assertEqual(fold["test_n"], 288)
            self.assertEqual(fold["train_n"], 192 if fold["protocol"] == "cross_session" else 1536)
            self.assertEqual(fold["calibration_n"], 96 if fold["protocol"] == "cross_session" else 768)

    def test_order_invariance(self):
        a = build(self.good)
        b = copy.deepcopy(self.good)
        b["trials"].reverse()
        self.assertEqual(a, build(b))

    def test_duplicate_trial_fails(self):
        x = copy.deepcopy(self.good)
        x["trials"][1]["trial_id"] = x["trials"][0]["trial_id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(x)

    def test_missing_run_trial_fails(self):
        x = copy.deepcopy(self.good)
        x["trials"].pop()
        with self.assertRaisesRegex(ValueError, "run counts"):
            validate(x)

    def test_wrong_dataset_fails(self):
        x = copy.deepcopy(self.good)
        x["dataset"] = "PhysionetMI"
        with self.assertRaisesRegex(ValueError, "wrong dataset"):
            validate(x)

    def test_extra_label_field_fails_closed(self):
        x = copy.deepcopy(self.good)
        x["trials"][0]["label"] = "left_hand"
        with self.assertRaisesRegex(ValueError, "fields"):
            validate(x)

    def test_invalid_subject_fails(self):
        x = copy.deepcopy(self.good)
        x["trials"][0]["subject"] = 0
        with self.assertRaisesRegex(ValueError, "invalid subject"):
            validate(x)

    def test_invalid_session_fails(self):
        x = copy.deepcopy(self.good)
        x["trials"][0]["session"] = "session1"
        with self.assertRaisesRegex(ValueError, "invalid subject"):
            validate(x)

    def test_boolean_subject_fails(self):
        x = copy.deepcopy(self.good)
        x["trials"][0]["subject"] = True
        with self.assertRaisesRegex(ValueError, "invalid subject"):
            validate(x)


if __name__ == "__main__":
    unittest.main()
