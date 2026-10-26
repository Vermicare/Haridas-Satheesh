"""Fictional-only tests; physical-labeled fixtures deliberately remain unauthenticated."""
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from serial_bundle import BundleError, build, extract, verify


def fabricated_stream():
    text = io.StringIO(newline="")
    writer = csv.writer(text, lineterminator="\n")
    for i in range(121):
        for sensor, value, unit in (("BH1750", "100", "lux"), ("SCD40", "650", "ppm")):
            writer.writerow(["IOTCSV", "FICTIONAL-BOOT", sensor, i, i * 5000, value, unit, 1])
    return ("BOOT: fictional\n" + text.getvalue() + "STOP: fictional\n").encode()


class BundleContract(unittest.TestCase):
    def make(self, raw=None, origin="physical"):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        path = Path(root.name)
        (path / "raw.log").write_bytes(fabricated_stream() if raw is None else raw)
        (path / "firmware.bin").write_bytes(b"fictional firmware; not flashed")
        result = build(path / "raw.log", path / "firmware.bin", path / "bundle",
                       device_id="FICTIONAL-ESP32", recorded_start_utc="2026-10-24T00:00:00Z",
                       capture_origin=origin)
        return path / "bundle", result

    def test_declared_physical_is_not_attestation(self):
        folder, report = self.make()
        self.assertEqual(report["status"], "STRUCTURAL_PASS_PROVENANCE_UNVERIFIED")
        self.assertEqual(report["raw_serial_integrity"], "MATCHED_UNAUTHENTICATED")
        self.assertEqual(report["metrics"]["sample_counts"]["SCD40"], 121)
        self.assertEqual(verify(folder), report)

    def test_default_synthetic_is_rejected_as_physical(self):
        _, report = self.make(origin="synthetic")
        self.assertEqual(report["status"], "REJECT_INVALID")
        self.assertIn("synthetic origin", " ".join(report["errors"]))

    def test_raw_tampering_rejected(self):
        folder, _ = self.make()
        with (folder / "raw_serial.log").open("ab") as f:
            f.write(b"debug line\n")
        self.assertIn("raw serial SHA-256 mismatch", verify(folder)["errors"])

    def test_csv_tampering_rejected(self):
        folder, _ = self.make()
        with (folder / "samples.csv").open("ab") as f:
            f.write(b"junk\n")
        self.assertIn("CSV differs from raw serial extraction", verify(folder)["errors"])

    def test_mixed_boot_rejected(self):
        raw = fabricated_stream().replace(b"FICTIONAL-BOOT", b"OTHER-BOOT", 1)
        with self.assertRaisesRegex(BundleError, "mixed boot"):
            extract(raw)

    def test_missing_markers_rejected(self):
        with self.assertRaisesRegex(BundleError, "no IOTCSV"):
            extract(b"no sensor telemetry\n")

    def test_malformed_marker_rejected(self):
        with self.assertRaisesRegex(BundleError, "malformed telemetry marker"):
            extract(b"IOTCSV: broken\n")

    def test_prefixed_monitor_line_rejected(self):
        with self.assertRaisesRegex(BundleError, "must start"):
            extract(b"I (123) sensor: IOTCSV,boot,BH1750,0,0,1,lux,1\n")

    def test_extra_column_rejected(self):
        with self.assertRaisesRegex(BundleError, "seven fields"):
            extract(b"IOTCSV,boot,BH1750,0,0,1,lux,1,EXTRA\n")

    def test_invalid_utf8_rejected(self):
        with self.assertRaisesRegex(BundleError, "UTF-8"):
            extract(b"\xffIOTCSV,boot,BH1750,0,0,1,lux,1\n")

    def test_output_never_overwritten(self):
        folder, _ = self.make()
        parent = folder.parent
        with self.assertRaises(FileExistsError):
            build(parent / "raw.log", parent / "firmware.bin", folder,
                  device_id="FICTIONAL-ESP32", recorded_start_utc="2026-10-24T00:00:00Z",
                  capture_origin="physical")

    def test_invalid_local_time_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)
            (p / "raw").write_bytes(fabricated_stream())
            (p / "fw").write_bytes(b"fw")
            with self.assertRaisesRegex(BundleError, "explicit UTC"):
                build(p / "raw", p / "fw", p / "out", device_id="TEST",
                      recorded_start_utc="2026-10-24T09:00:00", capture_origin="physical")
            self.assertFalse((p / "out").exists())

    def test_manifest_tampering_rejected(self):
        folder, _ = self.make()
        p = folder / "manifest.json"
        data = json.loads(p.read_text())
        data["extracted_rows"] = 100
        p.write_text(json.dumps(data))
        self.assertIn("manifest extracted_rows mismatch", verify(folder)["errors"])

    def test_deterministic_extraction(self):
        raw = fabricated_stream()
        self.assertEqual(extract(raw), extract(raw))
        csv_bytes, boot, count = extract(raw)
        self.assertEqual(count, 242)
        self.assertEqual(boot, "FICTIONAL-BOOT")
        self.assertEqual(csv_bytes.count(b"\n"), 243)


    def test_reject_bundle_output_inside_git_directory(self):
        """Fictional raw serial must not be written into a publishable Git tree."""
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / ".git").mkdir()
            (base / "raw.log").write_bytes(fabricated_stream())
            (base / "firmware.bin").write_bytes(b"fictional firmware")
            destination = base / "nested" / "bundle"
            with self.assertRaisesRegex(BundleError, "Git worktree"):
                build(base / "raw.log", base / "firmware.bin", destination,
                      device_id="FICTIONAL-ESP32",
                      recorded_start_utc="2026-10-24T00:00:00Z",
                      capture_origin="physical")
            self.assertFalse(destination.exists())

    def test_reject_bundle_output_inside_linked_git_worktree(self):
        """Git worktrees can have a .git FILE, not just a directory."""
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / ".git").write_text("gitdir: /fictional/elsewhere\n")
            (base / "raw.log").write_bytes(fabricated_stream())
            (base / "firmware.bin").write_bytes(b"fictional firmware")
            destination = base / "bundle"
            with self.assertRaisesRegex(BundleError, "Git worktree"):
                build(base / "raw.log", base / "firmware.bin", destination,
                      device_id="FICTIONAL-ESP32",
                      recorded_start_utc="2026-10-24T00:00:00Z",
                      capture_origin="physical")
            self.assertFalse(destination.exists())



if __name__ == "__main__":
    unittest.main()
