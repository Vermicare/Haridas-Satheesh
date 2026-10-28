#!/usr/bin/env python3
"""30-second fictional CORTEX exact-disagreement demonstration; no private data."""
import json
from unittest.mock import patch

from reviewer_pair_exact_disagreement_v04 import compare_exact_disagreement
from test_reviewer_pair_semantic_gate_v03 import CASE, ARCHIVE, submission


def demo():
    a = submission("R01")
    b = submission("R02")
    with patch("reviewer_pair_preflight_v01.EXPECTED_CASE_SHA256", "case-sha"), \
         patch("reviewer_pair_preflight_v01.EXPECTED_ARCHIVE_SHA256", "archive-sha"):
        matching = compare_exact_disagreement(CASE, ARCHIVE, a, b, "case-sha", "archive-sha")
        b["objects"][0]["statement"] = "A different fictional decision interpretation"
        conflicting = compare_exact_disagreement(CASE, ARCHIVE, a, b, "case-sha", "archive-sha")
    assert matching["pair_ready"] and conflicting["pair_ready"]
    assert not matching["exact_disagreement_detected"]
    assert conflicting["field_mismatch_counts"]["statement"] == 1
    return {
        "fictional": True, "external_actions": 0, "human_reviewers": 0,
        "matching": matching, "different_text": conflicting,
        "semantic_accuracy": "TBD", "actual_review_burden": "TBD",
    }


if __name__ == "__main__":
    print(json.dumps(demo(), sort_keys=True, indent=2, allow_nan=False))
