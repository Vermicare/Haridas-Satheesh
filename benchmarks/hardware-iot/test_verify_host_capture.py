"""Adversarial injected-port verification; NO physical sensor evidence."""
import json
import tempfile
import unittest
from pathlib import Path

from serial_acquire import CaptureError, capture
from verify_host_capture import VerificationError, verify


class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self):
        self.t += 0.25
        return self.t


class Port:
    def __init__(self, chunks): self.chunks = iter(chunks)
    def read(self, n): return next(self.chunks, b"")
    def close(self): pass


class VerifyHostCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "capture"
        self.clock = Clock()

    def capture(self, chunks):
        return capture(lambda **kw: Port(chunks), self.root, port="FAKE", seconds=2,
                       monotonic=self.clock, now=lambda: "2026-10-25T00:00:00Z")

    def manifest(self):
        return json.loads((self.root / "capture_manifest.json").read_text())

    def set_manifest(self, m):
        (self.root / "capture_manifest.json").write_text(json.dumps(m))

    def test_valid_synthetic_capture_is_not_attestation(self):
        self.capture([b"IOTCSV,fake\n"])
        r = verify(self.root)
        self.assertEqual(r["status"], "INTEGRITY_PASS_PROVENANCE_UNVERIFIED")
        self.assertFalse(r["physical_sensor_origin_verified"])
        self.assertFalse(r["firmware_attested"])

    def test_raw_same_size_tamper_detected(self):
        self.capture([b"abc"])
        (self.root / "raw_serial.log").write_bytes(b"xyz")
        with self.assertRaisesRegex(VerificationError, "SHA-256 mismatch"): verify(self.root)

    def test_raw_truncation_detected(self):
        self.capture([b"abcdef"])
        (self.root / "raw_serial.log").write_bytes(b"abc")
        with self.assertRaisesRegex(VerificationError, "byte count mismatch"): verify(self.root)

    def test_status_swap_detected(self):
        self.capture([b"abc"])
        m = self.manifest()
        m["capture_status"] = "FAILED_OR_INTERRUPTED"
        self.set_manifest(m)
        with self.assertRaises(VerificationError): verify(self.root)

    def test_forged_duration_detected(self):
        self.capture([b"abc"])
        m = self.manifest()
        m["host_monotonic_elapsed_seconds"] = 1
        self.set_manifest(m)
        with self.assertRaisesRegex(VerificationError, "required host elapsed"): verify(self.root)

    def test_byte_offset_inversion_detected(self):
        self.capture([b"abc"])
        m = self.manifest()
        m["first_byte_host_offset_seconds"] = 10
        self.set_manifest(m)
        with self.assertRaisesRegex(VerificationError, "offsets"): verify(self.root)

    def test_duplicate_json_key_detected(self):
        self.capture([b"abc"])
        p = self.root / "capture_manifest.json"
        s = p.read_text()
        p.write_text(s[:-2] + ', "capture_status": "FAILED_OR_INTERRUPTED"}')
        with self.assertRaisesRegex(VerificationError, "duplicate manifest key"): verify(self.root)

    def test_raw_symlink_rejected(self):
        self.capture([b"abc"])
        p = self.root / "raw_serial.log"
        outside = Path(self.temp.name) / "other"
        outside.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(outside)
        with self.assertRaisesRegex(VerificationError, "symlink"): verify(self.root)

    def test_no_data_is_incomplete_not_success(self):
        with self.assertRaises(CaptureError): self.capture([])
        r = verify(self.root)
        self.assertEqual(r["status"], "INCOMPLETE_CAPTURE_PRESERVED")

    def test_forged_complete_empty_fails(self):
        with self.assertRaises(CaptureError): self.capture([])
        m = self.manifest()
        m["capture_status"] = "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED"
        (self.root / "raw_serial.partial").rename(self.root / "raw_serial.log")
        self.set_manifest(m)
        with self.assertRaisesRegex(VerificationError, "zero bytes"): verify(self.root)


if __name__ == "__main__": unittest.main()
