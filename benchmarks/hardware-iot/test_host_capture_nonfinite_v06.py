"""Synthetic manifest non-finite number regression tests; NO physical hardware data.

The JSON encoder deliberately emits NaN/Infinity in negative controls to
represent malformed or overflowed evidence manifests. A verifier must fail
closed, even when the raw bytes and SHA-256 are internally consistent.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from verify_host_capture import VerificationError, verify


class NonfiniteCaptureManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.raw = b"FICTIONAL-SERIAL-CAPTURE\n"
        (self.root / "raw_serial.log").write_bytes(self.raw)
        self.manifest = {
            "schema_version": "iot-host-serial-capture-v1",
            "capture_status": "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED",
            "bytes_captured": len(self.raw),
            "raw_sha256": hashlib.sha256(self.raw).hexdigest(),
            "requested_host_duration_seconds": 2.0,
            "host_monotonic_elapsed_seconds": 2.5,
            "first_byte_host_offset_seconds": 0.25,
            "last_byte_host_offset_seconds": 2.0,
        }

    def write_manifest(self):
        # Intentionally allow non-standard constants for adversarial fixtures.
        (self.root / "capture_manifest.json").write_text(
            json.dumps(self.manifest, allow_nan=True), encoding="utf-8"
        )

    def test_valid_finite_synthetic_manifest_remains_unattested(self):
        self.write_manifest()
        report = verify(self.root)
        self.assertEqual(report["status"], "INTEGRITY_PASS_PROVENANCE_UNVERIFIED")
        self.assertFalse(report["physical_sensor_origin_verified"])

    def test_nonfinite_elapsed_fails_closed(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=str(value)):
                self.manifest["host_monotonic_elapsed_seconds"] = value
                self.write_manifest()
                with self.assertRaises(VerificationError):
                    verify(self.root)

    def test_nonfinite_byte_offsets_fail_closed(self):
        for field in ("first_byte_host_offset_seconds", "last_byte_host_offset_seconds"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=str(value)):
                    self.manifest = {
                        **self.manifest,
                        "host_monotonic_elapsed_seconds": 2.5,
                        "first_byte_host_offset_seconds": 0.25,
                        "last_byte_host_offset_seconds": 2.0,
                    }
                    self.manifest[field] = value
                    self.write_manifest()
                    with self.assertRaises(VerificationError):
                        verify(self.root)

    def test_nonfinite_unchecked_metadata_fails_closed(self):
        self.manifest["instrument_uncertainty_seconds"] = float("nan")
        self.write_manifest()
        with self.assertRaises(VerificationError):
            verify(self.root)

    def test_overflowed_standard_json_number_fails_closed(self):
        self.write_manifest()
        p = self.root / "capture_manifest.json"
        s = p.read_text(encoding="utf-8")
        # 1e400 is legal JSON syntax, but Python float parsing overflows to inf.
        p.write_text(s.replace('"host_monotonic_elapsed_seconds": 2.5',
                               '"host_monotonic_elapsed_seconds": 1e400'), encoding="utf-8")
        with self.assertRaises(VerificationError):
            verify(self.root)

    def test_preserved_incomplete_capture_still_passes_as_incomplete(self):
        (self.root / "raw_serial.log").rename(self.root / "raw_serial.partial")
        self.manifest.update({
            "capture_status": "FAILED_OR_INTERRUPTED",
            "host_monotonic_elapsed_seconds": "TBD",
            "first_byte_host_offset_seconds": "TBD",
            "last_byte_host_offset_seconds": "TBD",
        })
        self.write_manifest()
        self.assertEqual(verify(self.root)["status"], "INCOMPLETE_CAPTURE_PRESERVED")


if __name__ == "__main__":
    unittest.main()
