"""Synthetic-only v0.2 annotation contract negative controls; no human data."""
import copy
import json
import unittest
from semantic_annotation_contract_v02 import validate_semantic_annotation, VERSION


def fixture():
    return {"synthetic": True, "annotation_schema_version": VERSION,
            "method": "manual_structured_notes", "reviewer_code": "R01",
            "objects": [
                {"kind": "decisions", "record_id": "D1", "source": ["b01"],
                 "statement": "Fictional approval", "status": "active"},
                {"kind": "actions", "record_id": "A1", "source": ["b02"],
                 "action": "Record a fictional sensor check", "owner": None, "due": None},
                {"kind": "risks", "record_id": "R1", "source": ["b03"],
                 "statement": "Fictional device uncertainty", "status": None},
                {"kind": "dependencies", "record_id": "P1", "source": ["b04"],
                 "statement": "Fictional input availability"},
                {"kind": "conditional_followups", "record_id": "F1", "source": ["b05"],
                 "condition": "If a fictional condition occurs", "action": "Recheck"}]}


class SemanticAnnotationContractTests(unittest.TestCase):
    def setUp(self):
        self.item = fixture()

    def errors(self):
        return validate_semantic_annotation(self.item)

    def test_valid_all_five_kinds_with_explicit_unknowns(self):
        self.assertEqual(self.errors(), [])

    def test_empty_annotations_allowed_without_inventing_labels(self):
        self.item["objects"] = []
        self.assertEqual(self.errors(), [])

    def test_version_required(self):
        self.item.pop("annotation_schema_version")
        self.assertIn("v02:wrong_schema_version", self.errors())

    def test_reject_template_pseudonym(self):
        self.item["reviewer_code"] = "R00"
        self.assertIn("v02:template_reviewer_code", self.errors())

    def test_reject_non_manual_method(self):
        self.item["method"] = "extractor_correction"
        self.assertIn("v02:manual_method_required", self.errors())

    def test_reject_semantically_empty_decision(self):
        self.item["objects"][0].pop("statement")
        self.assertIn("v02:object[0]:missing_semantic_fields", self.errors())

    def test_reject_blank_action(self):
        self.item["objects"][1]["action"] = "   "
        self.assertIn("v02:object[1]:invalid_action", self.errors())

    def test_unknown_owner_due_allowed_explicitly(self):
        self.assertEqual(self.errors(), [])

    def test_reject_invalid_calendar_date(self):
        self.item["objects"][1]["due"] = "2026-02-30"
        self.assertIn("v02:object[1]:invalid_due", self.errors())

    def test_reject_non_iso_date(self):
        self.item["objects"][1]["due"] = "Oct 27"
        self.assertIn("v02:object[1]:invalid_due", self.errors())

    def test_valid_iso_date(self):
        self.item["objects"][1]["due"] = "2026-10-27"
        self.assertEqual(self.errors(), [])

    def test_reject_unknown_object_field(self):
        self.item["objects"][0]["model_confidence"] = 0.99
        self.assertIn("v02:object[0]:unsupported_fields", self.errors())

    def test_reject_missing_explicit_unknowns(self):
        self.item["objects"][1].pop("owner")
        self.assertIn("v02:object[1]:missing_semantic_fields", self.errors())

    def test_reject_nonfinite_status_type(self):
        self.item["objects"][2]["status"] = {"open": True}
        self.assertIn("v02:object[2]:invalid_status", self.errors())

    def test_reject_nontext_semantic_claim(self):
        self.item["objects"][3]["statement"] = ["fictional"]
        self.assertIn("v02:object[3]:invalid_statement", self.errors())

    def test_reject_control_characters(self):
        self.item["objects"][4]["condition"] = "A\x00B"
        self.assertIn("v02:object[4]:invalid_condition", self.errors())

    def test_no_private_text_echoed_in_error_codes(self):
        self.item["objects"][0]["statement"] = "SECRET" * 100
        self.assertNotIn("SECRET", json.dumps(self.errors()))

    def test_reject_unsupported_kind(self):
        self.item["objects"][0]["kind"] = "payments"
        self.assertIn("v02:object[0]:unknown_kind", self.errors())

    def test_input_unchanged(self):
        before = copy.deepcopy(self.item)
        self.errors()
        self.assertEqual(before, self.item)

    def test_reject_malformed_objects(self):
        self.item["objects"] = [None]
        self.assertIn("v02:object[0]:invalid_object", self.errors())


if __name__ == "__main__":
    unittest.main()
