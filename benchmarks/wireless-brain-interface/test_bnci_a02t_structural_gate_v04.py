"""Synthetic negative controls for the A02T metadata gate. No network or EEG."""
import copy
import unittest

from bnci_a02t_structural_gate_v04 import (
    EXPECTED_BYTES, EXPECTED_SHA256, EXPECTED_SOURCE, validate,
)


def valid_report():
    blocks = [
        {"block_index_zero_based": i, "samples": 30000,
         "channels": 25, "sampling_rate_hz": 250.0,
         "cue_count": 0 if i < 3 else 48}
        for i in range(9)
    ]
    return {
        "dataset": "BNCI2014_001", "file": "A02T.mat",
        "session": "T_training", "source_url": EXPECTED_SOURCE,
        "source_sha256": EXPECTED_SHA256, "source_bytes": EXPECTED_BYTES,
        "sha256_is_provider_authenticated": False,
        "class_label_values_inspected": False,
        "raw_eeg_persisted_or_uploaded": False,
        "evaluation_session_or_labels_accessed": False,
        "six_task_runs_48_cues_each": True,
        "blocks": 9, "cue_free_baseline_blocks": 3,
        "cued_task_blocks": 6, "cues_total": 288,
        "decode_accuracy": "TBD", "false_action_risk": "TBD",
        "block_metadata": blocks,
    }


class GateTests(unittest.TestCase):
    def test_valid_synthetic_metadata_passes(self):
        self.assertEqual(validate(valid_report())["cues"], 288)

    def test_summary_only_cannot_hide_wrong_cues(self):
        r = valid_report()
        r["block_metadata"][8]["cue_count"] = 47
        with self.assertRaisesRegex(ValueError, "baseline/task"):
            validate(r)

    def test_wrong_task_order_rejected(self):
        r = valid_report()
        r["block_metadata"][0]["cue_count"] = 48
        r["block_metadata"][3]["cue_count"] = 0
        with self.assertRaisesRegex(ValueError, "baseline/task"):
            validate(r)

    def test_missing_block_rejected(self):
        r = valid_report()
        r["block_metadata"].pop()
        with self.assertRaisesRegex(ValueError, "block list"):
            validate(r)

    def test_duplicate_index_rejected(self):
        r = valid_report()
        r["block_metadata"][3]["block_index_zero_based"] = 2
        with self.assertRaisesRegex(ValueError, "block index"):
            validate(r)

    def test_wrong_channel_rejected(self):
        r = valid_report()
        r["block_metadata"][4]["channels"] = 24
        with self.assertRaisesRegex(ValueError, "channel count"):
            validate(r)

    def test_wrong_sampling_rate_rejected(self):
        r = valid_report()
        r["block_metadata"][5]["sampling_rate_hz"] = 200
        with self.assertRaisesRegex(ValueError, "sampling frequency"):
            validate(r)

    def test_source_byte_change_rejected(self):
        r = valid_report()
        r["source_bytes"] += 1
        with self.assertRaisesRegex(ValueError, "source byte"):
            validate(r)

    def test_source_hash_change_rejected(self):
        r = valid_report()
        r["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source_sha256"):
            validate(r)

    def test_label_leakage_flag_rejected(self):
        r = valid_report()
        r["evaluation_session_or_labels_accessed"] = True
        with self.assertRaisesRegex(ValueError, "privacy/provenance"):
            validate(r)

    def test_missing_provenance_flag_rejected(self):
        r = valid_report()
        del r["class_label_values_inspected"]
        with self.assertRaisesRegex(ValueError, "privacy/provenance"):
            validate(r)

    def test_bogus_performance_claim_rejected(self):
        r = valid_report()
        r["decode_accuracy"] = 0.99
        with self.assertRaisesRegex(ValueError, "performance claim"):
            validate(r)

    def test_boolean_does_not_count_as_integer(self):
        r = valid_report()
        r["block_metadata"][1]["channels"] = True
        with self.assertRaisesRegex(ValueError, "channel count"):
            validate(r)

    def test_nonpositive_sample_count_rejected(self):
        r = valid_report()
        r["block_metadata"][1]["samples"] = 0
        with self.assertRaisesRegex(ValueError, "sample count"):
            validate(r)

    def test_summary_mismatch_rejected(self):
        r = valid_report()
        r["cues_total"] = 287
        with self.assertRaisesRegex(ValueError, "summary"):
            validate(r)


if __name__ == "__main__":
    unittest.main()
