"""Fictional adversarial controls; optionally validate a separately pinned real v0.5 JSON."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from collections import Counter, defaultdict
from zhou2020_event_concentration_v06 import analyze, PINNED_JSON_SHA256, PINNED_SOURCE_REF


def fictional_census():
    """Fabricated 833-file structural census, never real EEG or labels."""
    counts = [40] * 815 + [80] * 6 + [56] + [39] * 4 + [38] * 2 + [37] * 4 + [18]
    records = []
    i = 0
    for subject in range(1, 21):
        for session in range(7 if subject < 20 else 6):
            for run in range(5 if (subject, session) == (20, 5) else 6):
                n = counts[i]
                i += 1
                records.append({
                    "subject": subject, "session": session, "event_rows": n,
                    "path": f"sub-{subject}/ses-{session}/eeg/sub-{subject}_ses-{session}_task-imagery_run-{run}_events.tsv",
                    "git_blob_sha1": "a" * 40,
                })
    assert i == 833 and sum(x["event_rows"] for x in records) == 33534
    by_s = defaultdict(lambda: {"files": 0, "event_rows": 0})
    by_ss = defaultdict(lambda: {"files": 0, "event_rows": 0})
    for r in records:
        for target in (by_s[str(r["subject"])], by_ss[f'{r["subject"]}/ses-{r["session"]}']):
            target["files"] += 1
            target["event_rows"] += r["event_rows"]
    return {
        "schema": "ZHOU2020_EVENT_ROW_CENSUS_V05", "pinned_source_ref": PINNED_SOURCE_REF,
        "files": 833, "total_event_rows": 33534, "file_provenance": records,
        "by_subject": dict(by_s), "by_subject_session": dict(by_ss),
        "event_rows_per_file_histogram": dict(Counter(str(x["event_rows"]) for x in records)),
    }


class FictionalControls(unittest.TestCase):
    def setUp(self):
        self.source = fictional_census()

    def test_structural_roundtrip(self):
        r = analyze(self.source)
        self.assertEqual((r["files"], r["structural_event_rows"], r["non40_files"]), (833, 33534, 18))
        self.assertFalse(r["maturity_advanced"])

    def test_changed_row_count_rejected(self):
        self.source["file_provenance"][0]["event_rows"] += 1
        with self.assertRaisesRegex(ValueError, "row_total_mismatch"):
            analyze(self.source)

    def test_duplicate_path_rejected(self):
        self.source["file_provenance"][1]["path"] = self.source["file_provenance"][0]["path"]
        with self.assertRaisesRegex(ValueError, "duplicate_or_invalid_path"):
            analyze(self.source)

    def test_source_ref_change_rejected(self):
        self.source["pinned_source_ref"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source_ref_mismatch"):
            analyze(self.source)

    def test_histogram_tamper_rejected(self):
        self.source["event_rows_per_file_histogram"]["40"] = 814
        with self.assertRaisesRegex(ValueError, "histogram_mismatch"):
            analyze(self.source)

    def test_subject_rollup_tamper_rejected(self):
        self.source["by_subject"]["1"]["event_rows"] += 1
        with self.assertRaisesRegex(ValueError, "subject_rollup_mismatch"):
            analyze(self.source)

    def test_session_rollup_tamper_rejected(self):
        self.source["by_subject_session"]["1/ses-0"]["event_rows"] += 1
        with self.assertRaisesRegex(ValueError, "session_rollup_mismatch"):
            analyze(self.source)

    def test_boolean_as_int_rejected(self):
        self.source["file_provenance"][0]["event_rows"] = True
        with self.assertRaisesRegex(ValueError, "invalid_subject_session_or_rows"):
            analyze(self.source)

    def test_real_pinned_census_if_supplied(self):
        path = os.environ.get("ZHOU2020_CENSUS_JSON")
        if not path:
            self.skipTest("optional real source absent; fictional tests still run")
        raw = Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PINNED_JSON_SHA256)
        r = analyze(json.loads(raw))
        self.assertEqual(r["by_subject"]["17"]["delta_from_40_per_file"], 136)
        self.assertEqual(r["by_subject"]["20"]["delta_from_40_per_file"], 120)
        self.assertEqual(r["session0_delta_from_40_per_file"], 254)


if __name__ == "__main__":
    unittest.main()
