"""Fictional negative controls; imports original v1.8 fixtures unchanged."""
import unittest
import test_capture_chain_v18 as prior
from capture_chain_v18 import check_chain
from host_byte_exposure_gate_v19 import audit


class HostByteExposureV19Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = prior.CaptureChainTests(methodName="test_complete_fictional_chain_is_only_structural")
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_original_v18_accepts_early_burst_but_v19_rejects(self):
        self.fixture.meta["first_byte_host_offset_seconds"] = 0.2
        self.fixture.meta["last_byte_host_offset_seconds"] = 0.3
        self.fixture.write_meta()
        self.assertEqual(check_chain(self.fixture.cap, self.fixture.bundle)["status"],
                         "HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD")
        r = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(r["status"], "REVIEW_REQUIRED")
        self.assertAlmostEqual(r["host_byte_exposure_s"], 0.1)
        self.assertIn("HOST_BYTE_EXPOSURE_UNDER_600_SECONDS", r["problems"])

    def test_original_v18_accepts_late_burst_but_v19_rejects(self):
        self.fixture.meta["first_byte_host_offset_seconds"] = 609.7
        self.fixture.meta["last_byte_host_offset_seconds"] = 609.9
        self.fixture.write_meta()
        self.assertEqual(check_chain(self.fixture.cap, self.fixture.bundle)["status"],
                         "HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD")
        self.assertEqual(audit(self.fixture.cap, self.fixture.bundle)["status"], "REVIEW_REQUIRED")

    def test_exact_600_second_exposure_is_structurally_consistent(self):
        self.fixture.meta["first_byte_host_offset_seconds"] = 0.2
        self.fixture.meta["last_byte_host_offset_seconds"] = 600.2
        self.fixture.write_meta()
        r = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(r["status"], "HOST_BYTE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED")
        self.assertFalse(r["physical_origin_authenticated"])
        self.assertFalse(r["device_span_verified"])

    def test_just_below_boundary_rejected(self):
        self.fixture.meta["first_byte_host_offset_seconds"] = 0.2
        self.fixture.meta["last_byte_host_offset_seconds"] = 600.199
        self.fixture.write_meta()
        self.assertEqual(audit(self.fixture.cap, self.fixture.bundle)["status"], "REVIEW_REQUIRED")

    def test_v18_raw_hash_rejection_is_not_bypassed(self):
        (self.fixture.cap / "raw_serial.log").write_bytes(self.fixture.raw + b"x")
        r = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(r["status"], "REVIEW_REQUIRED")
        self.assertIn("V18_CHAIN_NOT_ACCEPTED", r["problems"])

    def test_existing_nominal_fixture_is_only_structural(self):
        r = audit(self.fixture.cap, self.fixture.bundle)
        self.assertEqual(r["status"], "HOST_BYTE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED")
        self.assertAlmostEqual(r["host_byte_exposure_s"], 609.7)
        self.assertFalse(r["physical_time_attested"])
        self.assertIn("host_bundle_chain.py", r["required_next_gate"])


if __name__ == "__main__":
    unittest.main()
