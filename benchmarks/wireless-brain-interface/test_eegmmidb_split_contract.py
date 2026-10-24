"""Pure-stdlib contract tests: no EEG or private data."""
import copy
import hashlib
import unittest

from eegmmidb_split_contract import (
    RUNS, SEED_TAG, SUBJECTS, canonical_json, generate, ordered_subjects,
    subject_id, validate,
)


class SplitContractTests(unittest.TestCase):
    def setUp(self):
        self.m = generate()

    def test_subject_disjointness_and_complete_coverage(self):
        groups = [set(ids) for ids in self.m["subject_splits"].values()]
        self.assertEqual(list(map(len, groups)), [70, 19, 20])
        self.assertEqual(len(set.union(*groups)), 109)
        self.assertFalse(groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])

    def test_three_imagery_runs_only_and_unique_files(self):
        files = [p for split in self.m["expected_edf_files"].values() for p in split]
        self.assertEqual(len(files), 327)
        self.assertEqual(len(set(files)), 327)
        self.assertEqual(RUNS, (4, 8, 12))
        self.assertTrue(all(p.endswith(("R04.edf", "R08.edf", "R12.edf")) for p in files))

    def test_all_subjects_present(self):
        self.assertEqual(len(SUBJECTS), 109)
        self.assertEqual(sorted(ordered_subjects()), list(SUBJECTS))

    def test_event_codes_not_conflated(self):
        self.assertEqual(self.m["event_mapping"], {
            "T0": "rest-exclude", "T1": "imagined-left-fist", "T2": "imagined-right-fist"})

    def test_sampling_rate_exceptions_explicit(self):
        self.assertEqual(self.m["sampling_rate_exceptions_subjects_128hz"], [88, 92, 100])
        self.assertIn("TBD", self.m["sampling_rate_check"])

    def test_deterministic_bytes_and_hash(self):
        a, b = canonical_json(generate()), canonical_json(generate())
        self.assertEqual(a, b)
        self.assertEqual(hashlib.sha256(a).digest(), hashlib.sha256(b).digest())
        self.assertTrue(a.endswith(b"\n"))

    def test_mutated_test_subject_rejected(self):
        bad = copy.deepcopy(self.m)
        bad["subject_splits"]["test"][0] = bad["subject_splits"]["train"][0]
        with self.assertRaises(ValueError):
            validate(bad)

    def test_mutated_run_rejected(self):
        bad = copy.deepcopy(self.m)
        bad["imagery_runs"] = [4, 6, 12]
        with self.assertRaises(ValueError):
            validate(bad)

    def test_fabricated_verification_rejected(self):
        bad = copy.deepcopy(self.m)
        bad["data_access"] = "VERIFIED"
        with self.assertRaises(ValueError):
            validate(bad)

    def test_invalid_subject_rejected(self):
        for n in (0, 110, "1"):
            with self.assertRaises(ValueError):
                subject_id(n)

    def test_source_provenance_and_scope(self):
        self.assertIn("20261024", SEED_TAG)
        self.assertEqual(self.m["data_access"], "NOT PERFORMED")
        self.assertEqual(self.m["performance"], "TBD")
        self.assertIn("NOT longitudinal", self.m["design"])


if __name__ == "__main__":
    unittest.main()
