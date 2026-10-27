"""Fictional MAT structures only; never fetch upstream in tests."""
import hashlib
from io import BytesIO
import unittest
import numpy as np
from scipy.io import savemat
from bnci_mat_run_metadata_v02 import inspect_mat_bytes

def fixture(*, baseline=3, task=6, cues=48, bad_labels=False):
    runs = []
    for i in range(baseline + task):
        n = 0 if i < baseline else cues
        positions = np.arange(1, n + 1, dtype=np.int32)
        labels = np.ones(max(0, n - 1) if bad_labels and i == baseline else n, dtype=np.int32)
        runs.append({"X": np.zeros((250, 25), dtype=np.float64), "fs": 250.0,
                     "trial": positions, "y": labels})
    buffer = BytesIO()
    savemat(buffer, {"data": np.array(runs, dtype=object)})
    return buffer.getvalue()

class TestMetadata(unittest.TestCase):
    def inspect(self, raw):
        return inspect_mat_bytes(raw, expected_sha256=hashlib.sha256(raw).hexdigest(), expected_bytes=len(raw))

    def test_separate_baseline_blocks_from_task_runs(self):
        r = self.inspect(fixture())
        self.assertEqual((r["mat_blocks"], r["baseline_blocks_without_cues"], r["task_blocks_with_cues"], r["task_cues_total"]), (9, 3, 6, 288))
        self.assertTrue(r["documented_six_task_runs_48_cues_each"])
        self.assertTrue(r["mat_block_indices_are_not_task_run_indices"])
        self.assertFalse(r["class_labels_reported"])

    def test_wrong_run_count_is_reported_not_rewritten(self):
        self.assertFalse(self.inspect(fixture(task=5))["documented_six_task_runs_48_cues_each"])

    def test_wrong_cue_count_is_reported(self):
        self.assertFalse(self.inspect(fixture(cues=47))["documented_six_task_runs_48_cues_each"])

    def test_mismatched_labels_rejected(self):
        with self.assertRaisesRegex(ValueError, "cardinality"):
            self.inspect(fixture(bad_labels=True))

    def test_changed_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "byte identity"):
            inspect_mat_bytes(fixture())

    def test_wrong_format_rejected(self):
        raw = b"A" * 500
        with self.assertRaisesRegex(ValueError, "MATLAB 5"):
            self.inspect(raw)

    def test_no_cue_blocks_fail_documented_gate(self):
        r = self.inspect(fixture(task=0))
        self.assertEqual(r["task_cues_total"], 0)
        self.assertFalse(r["documented_six_task_runs_48_cues_each"])

if __name__ == "__main__":
    unittest.main()
