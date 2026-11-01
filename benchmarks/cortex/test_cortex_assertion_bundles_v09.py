"""Synthetic-only named-graph attribution regressions; no real authority."""
import unittest

from rdflib import Dataset
import cortex_assertion_bundles_v09 as m


def change(old, new):
    raw = m.build_example().decode("ascii")
    assert old in raw, old
    return raw.replace(old, new).encode("ascii")


class FictionalBundleTests(unittest.TestCase):
    def test_expected_example_passes(self):
        result = m.audit_bytes(m.build_example())
        self.assertTrue(result["valid"])
        self.assertEqual((result["observed_quads"], result["bundle_count"]), (10, 2))
        self.assertEqual((result["independent_truth"], result["authorization"]), ("TBD", "TBD"))

    def test_deterministic(self):
        self.assertEqual(m.build_example(), m.build_example())

    def test_semantically_equivalent_reordering(self):
        lines = m.build_example().splitlines(keepends=True)
        self.assertTrue(m.audit_bytes(b"".join(reversed(lines)))["valid"])

    def test_duplicate_statement_rdf_set_semantics(self):
        data = m.build_example()
        self.assertTrue(m.audit_bytes(data + data.splitlines(keepends=True)[0])["valid"])

    def test_swapped_asserting_agent_detected(self):
        raw = m.build_example().decode("ascii")
        raw = raw.replace("fictional-analyst-A", "fictional-analyst-X")
        self.assertFalse(m.audit_bytes(raw.encode())["valid"])

    def test_missing_attribution_detected(self):
        lines = m.build_example().splitlines(keepends=True)
        self.assertFalse(m.audit_bytes(b"".join(x for x in lines if b"wasAttributedTo" not in x))["valid"])

    def test_flattened_graph_loses_assertion_origin(self):
        raw = m.build_example().decode("ascii")
        raw = raw.replace("bundle-A> .", "bundle-metadata> .").replace("bundle-B> .", "bundle-metadata> .")
        self.assertFalse(m.audit_bytes(raw.encode())["valid"])

    def test_merged_competing_claims_rejected(self):
        raw = m.build_example().decode("ascii")
        raw = raw.replace("<https://example.org/cortex-fictional/20261024/bundle-B> .", "<https://example.org/cortex-fictional/20261024/bundle-A> .")
        self.assertFalse(m.audit_bytes(raw.encode())["valid"])

    def test_false_prov_revision_rejected(self):
        raw = m.build_example() + m._line((m.EX["checklist-B"], m.PROV.wasRevisionOf, m.EX["checklist-H12"], m.EX["bundle-A"])).encode("ascii")
        self.assertFalse(m.audit_bytes(raw)["valid"])

    def test_extra_graph_rejected(self):
        raw = m.build_example() + m._line((m.EX["checklist-B"], m.CORTEX.supersedes, m.EX["checklist-H12"], m.EX["bundle-C"])).encode("ascii")
        self.assertFalse(m.audit_bytes(raw)["valid"])

    def test_predicate_changed_rejected(self):
        self.assertFalse(m.audit_bytes(change("/vocab#clarifies", "/vocab#approves"))["valid"])

    def test_source_changed_rejected(self):
        self.assertFalse(m.audit_bytes(change("source-b07", "source-b99"))["valid"])

    def test_missing_bundle_type_rejected(self):
        lines = m.build_example().splitlines(keepends=True)
        self.assertFalse(m.audit_bytes(b"".join(x for x in lines if b"prov#Bundle" not in x))["valid"])

    def test_invalid_utf8_fails_closed(self):
        self.assertEqual(m.audit_bytes(b"\xff")["error"], "invalid_nquads")

    def test_oversized_input_fails_closed(self):
        self.assertEqual(m.audit_bytes(b"x" * (m.MAX_BYTES + 1))["error"], "invalid_or_oversized_input")

    def test_empty_input_fails_closed(self):
        self.assertFalse(m.audit_bytes(b"")["valid"])

    def test_no_claim_of_authority(self):
        report = m.audit_bytes(m.build_example())
        self.assertNotIn("authorized", report)
        self.assertEqual(report["authorization"], "TBD")


if __name__ == "__main__":
    unittest.main()
