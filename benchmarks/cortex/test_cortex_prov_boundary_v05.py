"""Fictional-only regression and adversarial tests for the narrow PROV projection."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cortex_prov_boundary_v05 as m


def fixture():
    return ({"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
             "case_id": "CORTEX-BLIND-20261024-A", "meeting": {"utterances": [
                 {"id": "b03", "text": "fictional hold clarification"},
                 {"id": "b07", "text": "fictional version B replaces H12"}]}},
            {"synthetic": True, "provenance": "AUTHOR_CREATED_FICTIONAL",
             "archive_id": "CORTEX-BLIND-ARCHIVE-20261024-A",
             "records": [{"decision_id": "H-11"}, {"decision_id": "H-12"}]})


class BoundaryTests(unittest.TestCase):
    def test_positive_static_projection(self):
        case, archive = fixture()
        text = m.render_turtle(case, archive)
        self.assertIn("cortex:supersedes ex:checklist-H12", text)
        self.assertIn("cortex:clarifies ex:hold-H11", text)
        self.assertIn("prov:wasDerivedFrom ex:source-b07", text)
        self.assertEqual(len([x for x in text.splitlines() if x.startswith("ex:") and x.endswith(" .")]), len(m.TRIPLES))

    def test_no_false_prov_revision_or_primary_source(self):
        text = m.render_turtle(*fixture())
        for forbidden in m.FORBIDDEN_PREDICATES:
            self.assertNotIn(forbidden + " ", text)
        self.assertNotIn("ex:checklist-B prov:wasDerivedFrom ex:checklist-H12", text)

    def test_no_hold_supersession(self):
        text = m.render_turtle(*fixture())
        self.assertNotIn("ex:hold-H11 cortex:supersedes", text)

    def test_duplicate_utterance_rejected(self):
        case, archive = fixture()
        case["meeting"]["utterances"].append({"id": "b03"})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            m.render_turtle(case, archive)

    def test_missing_archive_predecessor_rejected(self):
        case, archive = fixture()
        archive["records"].pop()
        with self.assertRaisesRegex(ValueError, "unresolved"):
            m.render_turtle(case, archive)

    def test_missing_source_rejected(self):
        case, archive = fixture()
        case["meeting"]["utterances"].pop()
        with self.assertRaisesRegex(ValueError, "unresolved"):
            m.render_turtle(case, archive)

    def test_nonfictional_rejected(self):
        case, archive = fixture()
        case["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "not_explicitly_fictional"):
            m.render_turtle(case, archive)

    def test_unknown_fixture_identity_rejected(self):
        case, archive = fixture()
        archive["archive_id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "wrong_fixture_identity"):
            m.render_turtle(case, archive)

    def test_tampered_raw_bytes_rejected_before_parse(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "input.json"
            p.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "frozen_hash_mismatch"):
                m._read_pinned(str(p), m.CASE_SHA256)

    def test_oversized_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "oversized.json"
            p.write_bytes(b"X" * (m.MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "oversized_input"):
                m._read_pinned(str(p), m.CASE_SHA256)

    def test_cli_does_not_echo_private_path(self):
        with io.StringIO() as err, contextlib.redirect_stderr(err):
            status = m.main(["export", "/private/do-not-echo.json", "/private/also-secret.json"])
            self.assertEqual(status, 1)
            self.assertNotIn("/private/", err.getvalue())

    def test_frozen_triples_have_declared_entities(self):
        entities = {s for s, p, o in m.TRIPLES if p == "a" and o == "prov:Entity"}
        for s, p, o in m.TRIPLES:
            if p != "a":
                self.assertIn(s, entities)
                self.assertIn(o, entities)

    def test_no_unsupported_edge_added(self):
        case, archive = fixture()
        with patch.object(m, "TRIPLES", m.TRIPLES + (("ex:checklist-B", "prov:wasRevisionOf", "ex:checklist-H12"),)):
            with self.assertRaisesRegex(ValueError, "unsupported_prov_relation"):
                m.render_turtle(case, archive)

    def test_no_false_hold_supersession_added(self):
        case, archive = fixture()
        with patch.object(m, "TRIPLES", m.TRIPLES + (("ex:hold-H11", "cortex:supersedes", "ex:checklist-H12"),)):
            with self.assertRaisesRegex(ValueError, "false_hold_supersession"):
                m.render_turtle(case, archive)


if __name__ == "__main__":
    unittest.main()
