"""Synthetic-only exception-aware metadata contract tests (no EEG files)."""
import copy
import hashlib
import unittest
from unittest.mock import patch

import bnci_a04t_exception_v05 as target

RAW = b"MATLAB 5.0 MAT-file" + b"x" * 240


def make_report(baselines=1):
    blocks = [{"block_index_zero_based": i, "samples": 1000, "channels": 25,
               "sampling_rate_hz": 250.0, "cue_count": 0 if i < baselines else 48}
              for i in range(baselines + 6)]
    return {"dataset": "BNCI2014_001", "session": "T_training",
            "source_sha256": hashlib.sha256(RAW).hexdigest(), "source_bytes": len(RAW),
            "sha256_is_provider_authenticated": False,
            "class_label_values_inspected": False, "raw_eeg_persisted_or_uploaded": False,
            "evaluation_session_or_labels_accessed": False,
            "decode_accuracy": "TBD", "false_action_risk": "TBD",
            "blocks": len(blocks), "cue_free_baseline_blocks": baselines,
            "cued_task_blocks": 6, "cues_total": 288,
            "six_task_runs_48_cues_each": True, "block_metadata": blocks}


class TestExceptionGate(unittest.TestCase):
    def test_shorter_eog_baseline_allowed(self):
        target.validate_derived(make_report(1), RAW)

    def test_three_baselines_also_allowed(self):
        target.validate_derived(make_report(3), RAW)

    def test_two_baselines_also_allowed(self):
        target.validate_derived(make_report(2), RAW)

    def test_wrong_source_bytes_rejected(self):
        with self.assertRaises(ValueError):
            target.validate_derived(make_report(), RAW + b"x")

    def test_missing_baseline_rejected(self):
        with self.assertRaises(ValueError):
            target.validate_derived(make_report(0), RAW)

    def test_cue_in_baseline_rejected(self):
        report = make_report()
        report["block_metadata"][0]["cue_count"] = 48
        with self.assertRaises(ValueError):
            target.validate_derived(report, RAW)

    def test_task_cue_missing_rejected(self):
        report = make_report()
        report["block_metadata"][-1]["cue_count"] = 47
        with self.assertRaises(ValueError):
            target.validate_derived(report, RAW)

    def test_privacy_claim_rejected(self):
        report = make_report()
        report["class_label_values_inspected"] = True
        with self.assertRaises(ValueError):
            target.validate_derived(report, RAW)

    def test_performance_claim_rejected(self):
        report = make_report()
        report["decode_accuracy"] = 0.99
        with self.assertRaises(ValueError):
            target.validate_derived(report, RAW)

    def test_unexpected_channel_count_rejected(self):
        report = make_report()
        report["block_metadata"][0]["channels"] = 22
        with self.assertRaises(ValueError):
            target.validate_derived(report, RAW)

    def test_block_index_gap_rejected(self):
        report = make_report()
        report["block_metadata"][2]["block_index_zero_based"] = 7
        with self.assertRaises(ValueError):
            target.validate_derived(report, RAW)

    def test_bad_source_url_rejected(self):
        for url in ("http://bnci-horizon-2020.eu/database/data-sets/001-2014/A04T.mat",
                    "https://evil.example/A04T.mat",
                    "https://bnci-horizon-2020.eu/database/data-sets/001-2014/A04T.mat?token=x"):
            with self.assertRaises(ValueError):
                target.validate_url(url)

    def test_inspector_metadata_override_and_flag(self):
        with patch.object(target.base, "inspect_bytes", return_value=copy.deepcopy(make_report())):
            report = target.inspect_training_bytes(RAW)
        self.assertEqual(report["file"], "A04T.mat")
        self.assertEqual(report["source_url"], target.SOURCE)
        self.assertEqual(report["source_hash_status"], "observed, not independently pinned")
        self.assertFalse(report["evaluation_session_or_labels_accessed"])


if __name__ == "__main__":
    unittest.main()
