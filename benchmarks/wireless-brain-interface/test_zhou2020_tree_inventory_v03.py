"""Fictional Git-tree metadata fixtures only; no EEG files."""
import unittest
from zhou2020_tree_inventory_v03 import REF, audit


def fixture():
    root = {"sha": REF, "truncated": False, "tree": []}
    trees = {}
    for s in range(1, 21):
        sha = f"test-tree-{s}"
        root["tree"].append({"path": f"sub-{s}", "sha": sha, "type": "tree"})
        t = {"sha": sha, "truncated": False, "tree": []}
        for ses in range(7):
            t["tree"].append({"path": f"ses-{ses}", "type": "tree"})
            for run in range(6):
                for kind in ("channels", "events"):
                    t["tree"].append({"type": "blob", "path": f"ses-{ses}/eeg/sub-{s}_ses-{ses}_task-imagery_run-{run}_{kind}.tsv"})
        trees[s] = t
    return root, trees


class InventoryTests(unittest.TestCase):
    def test_nominal_fictional_inventory(self):
        r = audit(*fixture())
        self.assertEqual((r["observed_subjects"], r["observed_channel_metadata_files"]), (20, 840))
        self.assertEqual(r["noncanonical_run_sets"], [])
        self.assertFalse(r["eeg_signals_read"])

    def test_missing_session_flagged_without_inventing_runs(self):
        root, trees = fixture()
        t = trees[20]["tree"]
        trees[20]["tree"] = [e for e in t if not e["path"].startswith("ses-6")]
        r = audit(root, trees)
        self.assertEqual(r["observed_channel_metadata_files"], 834)
        self.assertEqual(r["absent_session_directories"], [{"subject": 20, "session": 6}])

    def test_extra_run_not_called_missing(self):
        root, trees = fixture()
        for kind in ("channels", "events"):
            trees[1]["tree"].append({"type": "blob", "path": f"ses-2/eeg/sub-1_ses-2_task-imagery_run-6_{kind}.tsv"})
        r = audit(root, trees)
        self.assertEqual(r["observed_channel_metadata_files"], 841)
        self.assertIn(6, r["noncanonical_run_sets"][0]["run_indices"])

    def test_orphan_event_fails(self):
        root, trees = fixture()
        trees[1]["tree"] = [e for e in trees[1]["tree"] if e["path"] != "ses-0/eeg/sub-1_ses-0_task-imagery_run-0_events.tsv"]
        with self.assertRaisesRegex(ValueError, "unpaired"):
            audit(root, trees)

    def test_truncated_subject_fails(self):
        root, trees = fixture()
        trees[3]["truncated"] = True
        with self.assertRaisesRegex(ValueError, "truncated"):
            audit(root, trees)

    def test_wrong_ref_fails(self):
        root, trees = fixture()
        root["sha"] = "different"
        with self.assertRaisesRegex(ValueError, "pinned"):
            audit(root, trees)

    def test_missing_subject_fails(self):
        root, trees = fixture()
        root["tree"].pop()
        with self.assertRaisesRegex(ValueError, "subjects"):
            audit(root, trees)

    def test_malformed_metadata_name_fails(self):
        root, trees = fixture()
        trees[2]["tree"].append({"type": "blob", "path": "ses-0/eeg/strange_channels.tsv"})
        with self.assertRaisesRegex(ValueError, "unexpected"):
            audit(root, trees)

    def test_mismatched_embedded_subject_fails(self):
        root, trees = fixture()
        trees[2]["tree"].append({"type": "blob", "path": "ses-0/eeg/sub-1_ses-0_task-imagery_run-8_channels.tsv"})
        with self.assertRaisesRegex(ValueError, "identifier"):
            audit(root, trees)

    def test_renumbered_runs_are_reported(self):
        root, trees = fixture()
        for kind in ("channels", "events"):
            trees[5]["tree"] = [e for e in trees[5]["tree"] if e["path"] != f"ses-0/eeg/sub-5_ses-0_task-imagery_run-0_{kind}.tsv"]
            trees[5]["tree"].append({"type": "blob", "path": f"ses-0/eeg/sub-5_ses-0_task-imagery_run-7_{kind}.tsv"})
        r = audit(root, trees)
        self.assertEqual(r["observed_channel_metadata_files"], 840)
        self.assertEqual(r["noncanonical_run_sets"][0]["run_indices"], [1, 2, 3, 4, 5, 7])


if __name__ == "__main__":
    unittest.main()
