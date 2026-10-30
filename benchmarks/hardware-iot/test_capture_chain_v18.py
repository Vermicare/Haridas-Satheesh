"""All test bytes and timestamps are fictional; zero real devices involved."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from capture_chain_v18 import check_chain


def fictional_stream():
    rows = []
    for t in range(0, 601000, 1000):
        rows.append((t, f"IOTCSV,deadbeefcafefeed,BH1750,{t//1000},{t},100.00,lux,1\n"))
        if t % 5000 == 0:
            rows.append((t, f"IOTCSV,deadbeefcafefeed,SCD40,{t//5000},{t},800.00,ppm,1\n"))
    return ("I (0) fictional boot\n" + "".join(s for _, s in sorted(rows, key=lambda r: r[0]))).encode()


class CaptureChainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.cap = root / "host"
        self.cap.mkdir()
        self.bundle = root / "bundle"
        self.raw = fictional_stream()
        (self.cap / "raw_serial.log").write_bytes(self.raw)
        (self.bundle).mkdir()
        (self.bundle / "raw_serial.log").write_bytes(self.raw)
        csv_bytes = b"boot_id,sensor,seq,elapsed_ms,value,unit,ready\n" + self.raw.split(b"IOTCSV,")[1].split(b"\n")[0] + b"\n"
        (self.bundle / "samples.csv").write_bytes(csv_bytes)
        (self.bundle / "manifest.json").write_text(json.dumps({
            "schema_version": "iot-capture-preflight-v1",
            "capture_origin": "physical",  # deliberately false operator declaration
            "raw_serial_sha256": hashlib.sha256(self.raw).hexdigest(),
            "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
        }))
        manifest = {
            "schema_version": "iot-host-serial-capture-v1",
            "port_operator_declared": "FICTIONAL-PORT", "baudrate": 115200,
            "requested_host_duration_seconds": 610,
            "host_start_utc": "2026-10-29T00:00:00Z",
            "host_end_utc": "2026-10-29T00:10:10Z",
            "host_monotonic_elapsed_seconds": 610.1,
            "first_byte_host_offset_seconds": 0.2,
            "last_byte_host_offset_seconds": 609.9,
            "bytes_captured": len(self.raw),
            "raw_sha256": hashlib.sha256(self.raw).hexdigest(),
            "capture_status": "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED",
            "physical_sensor_origin_verified": False,
            "device_monotonic_span_verified": False,
        }
        self.meta = manifest
        self.write_meta()

    def tearDown(self):
        self.temp.cleanup()

    def write_meta(self):
        (self.cap / "capture_manifest.json").write_text(json.dumps(self.meta))

    def assert_rejected(self, fragment):
        r = check_chain(self.cap, self.bundle)
        self.assertEqual(r["status"], "REJECT_INVALID", r)
        self.assertIn(fragment, " ".join(r["errors"]))

    def test_complete_fictional_chain_is_only_structural(self):
        r = check_chain(self.cap, self.bundle)
        self.assertEqual(r["status"], "HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD", r)
        self.assertFalse(r["physical_origin_verified"])
        self.assertFalse(r["flashed_firmware_verified"])
        self.assertIn("serial_bundle.py verify", r["required_next_gate"])

    def test_interrupted_capture_rejected(self):
        self.meta["capture_status"] = "FAILED_OR_INTERRUPTED"; self.write_meta()
        self.assert_rejected("incomplete")

    def test_raw_mutation_rejected(self):
        (self.cap / "raw_serial.log").write_bytes(self.raw + b"x")
        self.assert_rejected("SHA-256")

    def test_host_byte_count_mismatch_rejected(self):
        self.meta["bytes_captured"] -= 1; self.write_meta()
        self.assert_rejected("byte count")

    def test_host_duration_under_ten_minutes_rejected(self):
        self.meta["host_monotonic_elapsed_seconds"] = 599.9; self.write_meta()
        self.assert_rejected("ten-minute")

    def test_host_requested_duration_too_short_rejected(self):
        self.meta["requested_host_duration_seconds"] = 500; self.write_meta()
        self.assert_rejected("ten-minute")

    def test_out_of_range_offset_rejected(self):
        self.meta["last_byte_host_offset_seconds"] = 650; self.write_meta()
        self.assert_rejected("offsets")

    def test_duplicate_manifest_key_rejected(self):
        p = self.cap / "capture_manifest.json"
        p.write_text(p.read_text().rstrip()[:-1] + ',"capture_status":"HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED"}')
        self.assert_rejected("duplicate JSON key")

    def test_nonfinite_number_rejected(self):
        self.meta["host_monotonic_elapsed_seconds"] = float("nan"); self.write_meta()
        self.assert_rejected("nonfinite")

    def test_partial_file_rejected(self):
        (self.cap / "raw_serial.partial").write_bytes(b"incomplete")
        self.assert_rejected("partial")

    def test_bundle_raw_mutation_rejected(self):
        (self.bundle / "raw_serial.log").write_bytes(self.raw + b"x")
        self.assert_rejected("bundle raw bytes")

    def test_bundle_csv_tampering_rejected(self):
        with (self.bundle / "samples.csv").open("ab") as f:
            f.write(b"malicious")
        self.assert_rejected("derived CSV SHA-256")

    def test_utc_order_rejected(self):
        self.meta["host_end_utc"] = "2026-10-28T23:00:00Z"; self.write_meta()
        self.assert_rejected("precedes")

    def test_boolean_duration_rejected(self):
        self.meta["host_monotonic_elapsed_seconds"] = True; self.write_meta()
        self.assert_rejected("not boolean")


if __name__ == "__main__":
    unittest.main()
