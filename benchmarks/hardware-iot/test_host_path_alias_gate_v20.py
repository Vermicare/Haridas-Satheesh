"""Fictional path-alias negative controls; no hardware, no raw private data."""
import unittest
from pathlib import Path

import test_capture_chain_v18 as original
from capture_chain_v18 import check_chain
from host_byte_exposure_gate_v19 import audit as audit_v19
from host_path_alias_gate_v20 import audit


class HostPathAliasV20Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = original.CaptureChainTests(
            methodName="test_complete_fictional_chain_is_only_structural")
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def make_symlink(self, link, target, *, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("Symlinks unavailable on this runner: " + str(exc))

    def test_regular_fictional_inputs_pass_path_check_only(self):
        result = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(result["status"], "PATHS_REGULAR_BOUNDED_ORIGIN_UNVERIFIED")
        self.assertFalse(result["physical_origin_authenticated"])
        self.assertFalse(result["race_free_file_identity"])

    def test_raw_symlink_alias_passes_original_v18_v19_but_v20_rejects(self):
        link = self.fixture.bundle / "raw_serial.log"
        link.unlink()
        self.make_symlink(link, self.fixture.cap / "raw_serial.log")
        self.assertEqual(check_chain(self.fixture.cap, self.fixture.bundle)["status"],
                         "HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD")
        self.assertEqual(audit_v19(self.fixture.cap, self.fixture.bundle)["status"],
                         "HOST_BYTE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED")
        result = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("SYMLINK_raw_serial.log", " ".join(result["problems"]))

    def test_capture_manifest_symlink_rejected_before_read(self):
        original_path = self.fixture.cap / "capture_manifest.json"
        external = self.fixture.cap.parent / "external_manifest.json"
        external.write_bytes(original_path.read_bytes())
        original_path.unlink()
        self.make_symlink(original_path, external)
        result = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("SYMLINK_capture_manifest.json", " ".join(result["problems"]))

    def test_bundle_directory_symlink_rejected(self):
        alias = self.fixture.cap.parent / "alias"
        self.make_symlink(alias, self.fixture.bundle, directory=True)
        self.assertEqual(audit(self.fixture.cap, alias)["status"], "REVIEW_REQUIRED")

    def test_oversize_manifest_rejected_before_json_parse(self):
        (self.fixture.bundle / "manifest.json").write_bytes(b"x" * 1_000_001)
        result = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("SIZE_LIMIT_manifest.json", " ".join(result["problems"]))

    def test_same_directory_rejected(self):
        result = audit(self.fixture.cap, self.fixture.cap)
        self.assertIn("SAME_DIRECTORY", " ".join(result["problems"]))

    def test_missing_bundle_csv_rejected(self):
        (self.fixture.bundle / "samples.csv").unlink()
        result = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")

    def test_short_burst_still_rejected_by_v19(self):
        self.fixture.meta["first_byte_host_offset_seconds"] = 0.2
        self.fixture.meta["last_byte_host_offset_seconds"] = 0.3
        self.fixture.write_meta()
        result = audit(self.fixture.cap, self.fixture.bundle)
        self.assertIn("V19_GATE_NOT_ACCEPTED", result["problems"])

    def test_original_raw_tampering_still_rejected(self):
        (self.fixture.cap / "raw_serial.log").write_bytes(self.fixture.raw + b"x")
        self.assertEqual(audit(self.fixture.cap, self.fixture.bundle)["status"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
