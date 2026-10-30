"""Fictional-only downstream RDF contract negative controls (no human review)."""
import io
import contextlib
import json
from pathlib import Path
import tempfile
import unittest

from rdflib import Graph
import cortex_graph_contract_v07 as m

PREFIX = ("@prefix prov: <http://www.w3.org/ns/prov#> .\n"
          "@prefix cortex: <https://example.org/cortex-fictional/vocab#> .\n"
          "@prefix ex: <https://example.org/cortex-fictional/20261024/> .\n")

def original():
    # Independent frozen-case text fixture; hosted CI additionally tests the
    # unchanged real v0.5 CLI output against this separate v0.7 audit.
    triples = [
        "ex:source-b03 a prov:Entity .", "ex:source-b07 a prov:Entity .",
        "ex:archive-H11 a prov:Entity .", "ex:archive-H12 a prov:Entity .",
        "ex:hold-H11 a prov:Entity .",
        "ex:hold-H11 prov:wasDerivedFrom ex:archive-H11 .",
        "ex:checklist-H12 a prov:Entity .",
        "ex:checklist-H12 prov:wasDerivedFrom ex:archive-H12 .",
        "ex:checklist-B a prov:Entity .",
        "ex:checklist-B prov:wasDerivedFrom ex:source-b07 .",
        "ex:checklist-B cortex:supersedes ex:checklist-H12 .",
        "ex:hold-clarification a prov:Entity .",
        "ex:hold-clarification prov:wasDerivedFrom ex:source-b03 .",
        "ex:hold-clarification cortex:clarifies ex:hold-H11 .",
    ]
    return PREFIX + "\n".join(triples) + "\n"

class FrozenGraphContractTests(unittest.TestCase):
    def test_original_accepted(self):
        result = m.audit_bytes(original().encode())
        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_triples"], 14)

    def test_semantically_identical_reordering_accepted(self):
        lines = original().splitlines()
        self.assertTrue(m.audit_bytes(("\n".join(lines[:3] + list(reversed(lines[3:]))) + "\n").encode())["valid"])

    def test_semantically_identical_duplicate_triple_accepted(self):
        self.assertTrue(m.audit_bytes((original() + "ex:source-b03 a prov:Entity .\n").encode())["valid"])

    def test_forbidden_revision_detected(self):
        s = original() + "ex:checklist-B prov:wasRevisionOf ex:checklist-H12 .\n"
        self.assertEqual(m.audit_bytes(s.encode())["error"], "unsupported_prov_predicate")

    def test_false_primary_source_detected(self):
        s = original() + "ex:checklist-B prov:hadPrimarySource ex:archive-H12 .\n"
        self.assertEqual(m.audit_bytes(s.encode())["error"], "unsupported_prov_predicate")

    def test_false_hold_invalidation_detected(self):
        s = original() + "ex:hold-H11 prov:wasInvalidatedBy ex:source-b03 .\n"
        self.assertEqual(m.audit_bytes(s.encode())["error"], "unsupported_prov_predicate")

    def test_reverse_supersession_detected(self):
        s = original().replace("ex:checklist-B cortex:supersedes ex:checklist-H12", "ex:checklist-H12 cortex:supersedes ex:checklist-B")
        d = m.audit_bytes(s.encode())
        self.assertEqual((d["missing_triples"], d["unexpected_triples"]), (1, 1))

    def test_missing_derivation_detected(self):
        s = original().replace("ex:hold-H11 prov:wasDerivedFrom ex:archive-H11 .\n", "")
        self.assertEqual(m.audit_bytes(s.encode())["missing_triples"], 1)

    def test_spoofed_namespace_detected(self):
        s = original().replace("https://example.org/cortex-fictional/vocab#", "https://attacker.example/vocab#")
        self.assertFalse(m.audit_bytes(s.encode())["valid"])

    def test_unauthorized_domain_edge_detected(self):
        s = original() + "ex:hold-H11 cortex:supersedes ex:checklist-H12 .\n"
        self.assertEqual(m.audit_bytes(s.encode())["unexpected_triples"], 1)

    def test_invalid_turtle_fails_closed(self):
        self.assertEqual(m.audit_bytes(b"not turtle ???")["error"], "invalid_turtle")

    def test_oversize_fails_closed(self):
        self.assertEqual(m.audit_bytes(b"x" * (m.MAX_BYTES + 1))["error"], "invalid_or_oversized_input")

    def test_non_utf8_fails_closed(self):
        self.assertEqual(m.audit_bytes(b"\xff\xfe")["error"], "invalid_turtle")

    def test_cli_fails_closed_and_does_not_echo_path(self):
        with io.StringIO() as out, contextlib.redirect_stdout(out):
            rc = m.main(["audit", "/private/secret-cortex-fixture.ttl"])
            self.assertEqual(rc, 1)
            self.assertNotIn("/private/", out.getvalue())
            self.assertEqual(json.loads(out.getvalue())["error"], "unreadable_input")

    def test_cli_accepts_original_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fictional.ttl"
            p.write_text(original(), encoding="utf-8")
            with io.StringIO() as out, contextlib.redirect_stdout(out):
                self.assertEqual(m.main(["audit", str(p)]), 0)
                self.assertTrue(json.loads(out.getvalue())["valid"])

if __name__ == "__main__":
    unittest.main()
