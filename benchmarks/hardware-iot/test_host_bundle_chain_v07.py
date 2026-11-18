"""Fictional-only tests for host-to-bundle chain; no physical hardware."""
import hashlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from host_bundle_chain import ChainError, verify_chain


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.host = Path(self.tmp.name) / "host"
        self.bundle = Path(self.tmp.name) / "bundle"
        self.host.mkdir()
        self.bundle.mkdir()
        self.raw = b"FICTIONAL RAW BYTES ONLY\n"
        self.sha = hashlib.sha256(self.raw).hexdigest()
        (self.host / "raw_serial.log").write_bytes(self.raw)
        (self.bundle / "raw_serial.log").write_bytes(self.raw)
        self.hm = {"raw_sha256": self.sha, "host_monotonic_elapsed_seconds": 630.0,
                   "first_byte_host_offset_seconds": 0.5,
                   "last_byte_host_offset_seconds": 625.5}
        self.bm = {"raw_serial_sha256": self.sha, "extracted_rows": 242}
        self.save()

    def save(self):
        (self.host / "capture_manifest.json").write_text(json.dumps(self.hm))
        (self.bundle / "manifest.json").write_text(json.dumps(self.bm))

    def run_chain(self, host_status="INTEGRITY_PASS_PROVENANCE_UNVERIFIED",
                  bundle_status="STRUCTURAL_PASS_PROVENANCE_UNVERIFIED", device_span=600000):
        h = types.ModuleType("verify_host_capture")
        h.VerificationError = ValueError
        h.verify = lambda path: {"status": host_status, "raw_sha256": self.sha}
        b = types.ModuleType("serial_bundle")
        b.verify = lambda path: {"status": bundle_status, "errors": ["fictional error"],
                                 "metrics": {"duration_ms": device_span}}
        with patch.dict(sys.modules, {"verify_host_capture": h, "serial_bundle": b}):
            return verify_chain(self.host, self.bundle)

    def test_valid_fictional_chain_is_not_physical_attestation(self):
        result = self.run_chain()
        self.assertEqual(result["status"], "CHAIN_PASS_PROVENANCE_UNVERIFIED")
        self.assertFalse(result["physical_origin_verified"])
        self.assertEqual(result["host_byte_exposure_seconds"], 625)

    def test_host_capture_incomplete(self):
        with self.assertRaisesRegex(ChainError, "incomplete"):
            self.run_chain(host_status="INCOMPLETE_CAPTURE_PRESERVED")

    def test_bundle_preflight_rejected(self):
        with self.assertRaisesRegex(ChainError, "bundle preflight failed"):
            self.run_chain(bundle_status="REJECT_INVALID")

    def test_bulk_replay_first_second_rejected_despite_630s_host(self):
        self.hm["last_byte_host_offset_seconds"] = 1.0
        self.save()
        with self.assertRaisesRegex(ChainError, "first-to-last-byte"):
            self.run_chain()

    def test_host_short_duration_rejected(self):
        self.hm["host_monotonic_elapsed_seconds"] = 599.9
        self.save()
        with self.assertRaisesRegex(ChainError, "insufficient host"):
            self.run_chain()

    def test_short_device_span_rejected(self):
        with self.assertRaisesRegex(ChainError, "device-monotonic"):
            self.run_chain(device_span=599999)

    def test_bundle_raw_modified_even_if_bundle_hash_rewritten(self):
        tampered = b"FABRICATED OTHER BYTES\n"
        (self.bundle / "raw_serial.log").write_bytes(tampered)
        self.bm["raw_serial_sha256"] = hashlib.sha256(tampered).hexdigest()
        self.save()
        with self.assertRaisesRegex(ChainError, "raw bytes differ"):
            self.run_chain()

    def test_host_manifest_hash_mismatch(self):
        self.hm["raw_sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ChainError, "SHA-256 chain"):
            self.run_chain()

    def test_symlink_bundle_raw_rejected(self):
        (self.bundle / "raw_serial.log").unlink()
        (self.bundle / "raw_serial.log").symlink_to(self.host / "raw_serial.log")
        with self.assertRaisesRegex(ChainError, "symlink"):
            self.run_chain()

    def test_same_directory_rejected(self):
        with self.assertRaisesRegex(ChainError, "distinct"):
            with patch.dict(sys.modules, {"verify_host_capture": types.ModuleType("verify_host_capture"),
                                          "serial_bundle": types.ModuleType("serial_bundle")}):
                sys.modules["verify_host_capture"].VerificationError = ValueError
                sys.modules["verify_host_capture"].verify = lambda p: {}
                sys.modules["serial_bundle"].verify = lambda p: {}
                verify_chain(self.host, self.host)

    def _real_validator_fixture(self):
        """Exercise actual upstream validators in CI, using ONLY fictional bytes."""
        try:
            from serial_bundle import build
            from verify_host_capture import verify as verify_host
        except ImportError:
            self.skipTest("upstream repo modules unavailable in isolated local copy")
        import csv
        import io
        text = io.StringIO(newline="")
        writer = csv.writer(text, lineterminator="\n")
        for i in range(121):
            for sensor, value, unit in (("BH1750", "100", "lux"), ("SCD40", "650", "ppm")):
                writer.writerow(["IOTCSV", "FICTIONAL-BOOT", sensor, i, i * 5000, value, unit, 1])
        raw = ("BOOT: fictional\n" + text.getvalue()).encode()
        self.raw = raw
        self.sha = hashlib.sha256(raw).hexdigest()
        (self.host / "raw_serial.log").write_bytes(raw)
        self.hm = {
            "schema_version": "iot-host-serial-capture-v1",
            "capture_status": "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED",
            "bytes_captured": len(raw), "raw_sha256": self.sha,
            "requested_host_duration_seconds": 630,
            "host_monotonic_elapsed_seconds": 630.0,
            "first_byte_host_offset_seconds": 0.5,
            "last_byte_host_offset_seconds": 625.5,
        }
        self.save()
        (self.host / "firmware.bin").write_bytes(b"FICTIONAL firmware, not flashed")
        derived = self.host.parent / "derived"
        report = build(self.host / "raw_serial.log", self.host / "firmware.bin", derived,
                       device_id="FICTIONAL-ESP32", recorded_start_utc="2026-10-25T00:00:00Z",
                       capture_origin="physical")
        self.assertEqual(report["status"], "STRUCTURAL_PASS_PROVENANCE_UNVERIFIED")
        self.assertEqual(verify_host(self.host)["status"], "INTEGRITY_PASS_PROVENANCE_UNVERIFIED")
        return derived

    def test_full_integration_fictional_no_attestation(self):
        derived = self._real_validator_fixture()
        result = verify_chain(self.host, derived)
        self.assertEqual(result["status"], "CHAIN_PASS_PROVENANCE_UNVERIFIED")
        self.assertEqual(result["device_monotonic_span_ms"], 600000)
        self.assertFalse(result["physical_origin_verified"])

    def test_full_integration_bulk_replay_rejected(self):
        derived = self._real_validator_fixture()
        self.hm["last_byte_host_offset_seconds"] = 1.0
        self.save()
        with self.assertRaisesRegex(ChainError, "first-to-last-byte"):
            verify_chain(self.host, derived)


if __name__ == "__main__":
    unittest.main()
