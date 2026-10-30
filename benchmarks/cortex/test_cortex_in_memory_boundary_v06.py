"""Fictional mutation negative controls; no actual human/organizational records."""
import copy
import unittest
from unittest.mock import patch

import cortex_prov_boundary_v05 as frozen
from cortex_in_memory_boundary_v06 import render_checked


def fixture():
    case = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
            "case_id": "CORTEX-BLIND-20261024-A", "meeting": {
                "metadata": {"validated": True},
                "utterances": [{"id": "b03", "text": "hold remains"},
                               {"id": "b07", "text": "checklist replaced"}]}}
    archive = {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
               "archive_id": "CORTEX-BLIND-ARCHIVE-20261024-A",
               "records": [{"decision_id": "H-11", "text": "public hold", "status": "active"},
                           {"decision_id": "H-12", "text": "old checklist", "status": "historical"}]}
    return case, archive


def checked(case, archive, original_case, original_archive):
    with patch.object(frozen, "_read_pinned", side_effect=[original_case, original_archive]):
        return render_checked(case, archive, "fictional-case.json", "fictional-archive.json")


class InMemoryBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.case, self.archive = fixture()
        self.baseline = frozen.render_turtle(self.case, self.archive)

    def test_unchanged_fictional_fixture_passes(self):
        self.assertEqual(checked(self.case, self.archive, self.case, self.archive), self.baseline)

    def _mutate_and_reject(self, fn):
        case, archive = copy.deepcopy(self.case), copy.deepcopy(self.archive)
        fn(case, archive)
        # Demonstrate the original narrow in-memory projector is ID-based.
        self.assertEqual(frozen.render_turtle(case, archive), self.baseline)
        with self.assertRaisesRegex(ValueError, "^in_memory_source_mismatch$"):
            checked(case, archive, self.case, self.archive)

    def test_false_hold_revocation_text_rejected(self):
        self._mutate_and_reject(lambda c, a: c["meeting"]["utterances"][0].update(text="public hold revoked"))

    def test_false_checklist_supersession_text_rejected(self):
        self._mutate_and_reject(lambda c, a: c["meeting"]["utterances"][1].update(text="H-12 not replaced"))

    def test_archive_record_text_mutation_rejected(self):
        self._mutate_and_reject(lambda c, a: a["records"][0].update(text="public hold removed"))

    def test_archive_status_mutation_rejected(self):
        self._mutate_and_reject(lambda c, a: a["records"][0].update(status="revoked"))

    def test_added_unreviewed_utterance_rejected(self):
        self._mutate_and_reject(lambda c, a: c["meeting"]["utterances"].append({"id":"b08","text":"new"}))

    def test_boolean_to_integer_mutation_rejected(self):
        # Python dict equality would incorrectly consider True == 1; canonical JSON does not.
        self._mutate_and_reject(lambda c, a: c["meeting"]["metadata"].update(validated=1))

    def test_missing_pinned_source_fails_without_path_leak(self):
        with patch.object(frozen, "_read_pinned", side_effect=OSError("/private/path")):
            with self.assertRaisesRegex(ValueError, "^invalid_or_unreadable_frozen_input$") as ctx:
                render_checked(self.case, self.archive, "/private/path", "x")
            self.assertNotIn("/private/", str(ctx.exception))

    def test_nonfinite_data_rejected(self):
        case = copy.deepcopy(self.case)
        case["meeting"]["metadata"]["validated"] = float("nan")
        with self.assertRaisesRegex(ValueError, "^invalid_or_unreadable_frozen_input$"):
            checked(case, self.archive, self.case, self.archive)


if __name__ == "__main__":
    unittest.main()
