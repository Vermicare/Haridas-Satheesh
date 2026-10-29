"""Fully fictional adversarial regression tests; no reviewer submissions."""
import copy
import unittest
from provenance_oracle_v05 import audit
from evaluator import evaluate

FIXTURE = {
    "synthetic": True,
    "meeting": {"utterances": [{"id": x} for x in ("u1", "u2", "u3")]},
    "ground_truth": {
        "decisions": [{"id": "D1", "source": ["u1", "u2"], "statement": "Approve fictional test", "status": "active", "supersedes": "D0"}],
        "negative_examples": [{"source": ["u3"]}],
    },
}
CANDIDATE = {"decisions": [{"source": ["u1", "u2"], "statement": "Approve fictional test", "status": "active", "supersedes": "D0"}]}

class ProvenanceOracleTests(unittest.TestCase):
    def run_audit(self, sources=None, statement=None):
        obj = copy.deepcopy(CANDIDATE)
        if sources is not None:
            obj["decisions"][0]["source"] = sources
        if statement is not None:
            obj["decisions"][0]["statement"] = statement
        return audit(FIXTURE, obj)

    def test_exact_sources_pass_but_predecessor_unresolved(self):
        r = self.run_audit()
        self.assertEqual(r["source_integrity_gate"], "PASS")
        self.assertEqual(r["external_predecessor_validation"], "TBD")
        self.assertEqual(r["unresolved_external_predecessor_refs"], 1)

    def test_original_scorer_accepts_partial_source_as_full_traceability(self):
        partial = copy.deepcopy(CANDIDATE)
        partial["decisions"][0]["source"] = ["u1"]
        old = evaluate(FIXTURE, partial)
        self.assertEqual(old["metrics"]["source_span_traceability"], 1.0)
        self.assertEqual(audit(FIXTURE, partial)["source_integrity_gate"], "FAIL")

    def test_partial_source_false_pass_blocked(self):
        r = self.run_audit(["u1"])
        self.assertEqual(r["source_integrity_gate"], "FAIL")
        self.assertEqual(r["counts"]["incomplete_gold_source_objects"], 1)

    def test_unknown_source_fails(self):
        r = self.run_audit(["u1", "u2", "invented"])
        self.assertEqual(r["counts"]["unknown_source_ids_objects"], 1)
        self.assertEqual(r["source_integrity_gate"], "FAIL")

    def test_negative_example_promoted_fails(self):
        r = self.run_audit(["u1", "u2", "u3"])
        self.assertEqual(r["counts"]["negative_source_objects"], 1)
        self.assertEqual(r["source_integrity_gate"], "FAIL")

    def test_duplicate_source_fails(self):
        r = self.run_audit(["u1", "u1", "u2"])
        self.assertEqual(r["counts"]["duplicate_source_ids"], 1)
        self.assertEqual(r["source_integrity_gate"], "FAIL")

    def test_missing_source_fails(self):
        r = self.run_audit([])
        self.assertEqual(r["counts"]["missing_or_malformed_source"], 1)
        self.assertEqual(r["source_integrity_gate"], "FAIL")

    def test_semantically_unmatched_is_not_provenance_success(self):
        r = self.run_audit(statement="Unrelated fictional decision")
        self.assertEqual(r["counts"]["unmatched_semantic_signature_objects"], 1)
        self.assertEqual(r["source_integrity_gate"], "FAIL")

    def test_empty_candidate_does_not_invent_recall(self):
        r = audit(FIXTURE, {"decisions": []})
        self.assertEqual(r["counts"]["candidate_objects"], 0)
        self.assertEqual(r["source_integrity_gate"], "NOT_EVALUABLE")
        self.assertEqual(r["semantic_accuracy"], "TBD")

    def test_reject_nonfictional(self):
        bad = copy.deepcopy(FIXTURE)
        bad["synthetic"] = False
        with self.assertRaises(ValueError):
            audit(bad, CANDIDATE)

    def test_reject_duplicate_utterance_ids(self):
        bad = copy.deepcopy(FIXTURE)
        bad["meeting"]["utterances"].append({"id": "u1"})
        with self.assertRaises(ValueError):
            audit(bad, CANDIDATE)

    def test_no_source_text_or_identifiers_in_report(self):
        output = str(self.run_audit())
        for private in ("u1", "u2", "u3", "D0", "Approve fictional test"):
            self.assertNotIn(private, output)

    def test_inputs_unchanged(self):
        fixture, candidate = copy.deepcopy(FIXTURE), copy.deepcopy(CANDIDATE)
        audit(fixture, candidate)
        self.assertEqual(fixture, FIXTURE)
        self.assertEqual(candidate, CANDIDATE)

if __name__ == "__main__":
    unittest.main()
