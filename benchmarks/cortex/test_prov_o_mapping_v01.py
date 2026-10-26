"""Adversarial tests for synthetic-only illustrative PROV-O mapping."""
import copy
import json
import unittest
from pathlib import Path
from prov_o_mapping_v01 import map_fixture

FIXTURE = json.loads((Path(__file__).parent / "independent_scenario_v03.json").read_text(encoding="utf-8"))


class ProvenanceMappingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = copy.deepcopy(FIXTURE)

    def test_fictional_graph_contains_resolved_provenance_and_domain_supersession(self):
        graph = map_fixture(self.fixture)["@graph"]
        by_id = {node["@id"]: node for node in graph}
        self.assertEqual(len(graph), len(by_id))
        new = by_id["urn:cortex:synthetic:decision:D3"]
        self.assertEqual(new["cortex:supersedes"]["@id"], "urn:cortex:synthetic:decision:H0")
        self.assertEqual(new["prov:wasDerivedFrom"], [{"@id": "urn:cortex:synthetic:utterance:n01"}])
        old = by_id["urn:cortex:synthetic:decision:H0"]
        self.assertEqual(old["prov:wasDerivedFrom"], [{"@id": "urn:cortex:synthetic:archive:SYN-ARCHIVE-001"}])
        self.assertIn("urn:cortex:synthetic:dependency:D-05", by_id)
        self.assertNotIn("urn:cortex:synthetic:utterance:n06", new["prov:wasDerivedFrom"])
        self.assertTrue(all("prov:wasRevisionOf" not in node for node in graph))

    def test_deterministic_serialization(self):
        first = json.dumps(map_fixture(self.fixture), sort_keys=True, separators=(",", ":"))
        second = json.dumps(map_fixture(self.fixture), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)

    def test_requires_explicit_synthetic_mark(self):
        self.fixture["synthetic"] = False
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_unknown_utterance_rejected(self):
        self.fixture["ground_truth"]["actions"][0]["source"] = ["unknown"]
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_negative_utterance_promoted_rejected(self):
        self.fixture["ground_truth"]["actions"][0]["source"] = ["n06"]
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_dangling_historical_reference_rejected(self):
        self.fixture["history"]["records"] = []
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_mismatched_archive_record_rejected(self):
        self.fixture["history"]["records"][0]["decision_id"] = "NOT-H0"
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_duplicate_archive_reference_rejected(self):
        self.fixture["history"]["records"].append(copy.deepcopy(self.fixture["history"]["records"][0]))
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_duplicate_object_id_rejected(self):
        self.fixture["ground_truth"]["actions"].append(copy.deepcopy(self.fixture["ground_truth"]["actions"][0]))
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_self_supersession_rejected(self):
        self.fixture["ground_truth"]["decisions"][0]["supersedes"] = "D3"
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_unknown_predecessor_rejected(self):
        self.fixture["ground_truth"]["decisions"][0]["supersedes"] = "H999"
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_malformed_identifier_rejected(self):
        self.fixture["ground_truth"]["decisions"][0]["id"] = "D3> malicious"
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)

    def test_duplicate_source_rejected(self):
        self.fixture["ground_truth"]["decisions"][0]["source"] = ["n01", "n01"]
        with self.assertRaises(ValueError):
            map_fixture(self.fixture)


if __name__ == "__main__":
    unittest.main()
