"""Fictional transcripts only: no physical device or esptool execution."""
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from read_only_flash_probe_v15 import inspect_transcript, ProbeError, main

V4 = """esptool.py v4.10.0
Serial port COM7
Chip is ESP32-S3 (QFN56) (revision v0.2)
MAC: aa:bb:cc:dd:ee:ff
Manufacturer: ef
Device: 4017
Detected flash size: 8MB
"""
V5 = """esptool v5.0
Connected to ESP32-S3 on COM7:
Chip type:          ESP32-S3 (QFN56)
MAC:                aa:bb:cc:dd:ee:ff
Detected flash size: 2MB
"""


class FlashProbeTests(unittest.TestCase):
    def test_v4_detected_mismatch_requires_review(self):
        r = inspect_transcript(V4, 2)
        self.assertEqual(r["observed_flash_mb_claimed"], 8)
        self.assertEqual(r["flash_size_comparison"], "DIFFERENT_REQUIRES_BOARD_CONFIGURATION_REVIEW")
        self.assertFalse(r["flashed_image_attested"])

    def test_v5_match_does_not_authorize_flash(self):
        r = inspect_transcript(V5, 2)
        self.assertEqual(r["flash_size_comparison"], "MATCH")
        self.assertEqual(r["gate"], "TRANSCRIPT_PARSED_FLASH_NOT_AUTHORIZED")


    def test_v19_eight_mb_match_never_authorizes_flash(self):
        r = inspect_transcript(V4, 8)
        self.assertEqual(r["flash_size_comparison"], "MATCH")
        self.assertEqual(r["build_flash_mb_declared"], 8)
        self.assertFalse(r["physical_device_attested"])

    def test_v19_eight_mb_rejects_two_mb_transcript(self):
        r = inspect_transcript(V5, 8)
        self.assertEqual(r["flash_size_comparison"], "DIFFERENT_REQUIRES_BOARD_CONFIGURATION_REVIEW")

    def test_missing_image_size_rejected(self):
        with self.assertRaisesRegex(ProbeError, "explicit build flash size required"):
            inspect_transcript(V4)

    def test_bool_build_size_rejected(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4, True)

    def test_cli_missing_build_size_fails_before_file_read(self):
        sink = StringIO()
        with redirect_stdout(sink):
            status = main(["/private/secret-home/esp32-flash-id.txt"])
        self.assertEqual(status, 2)
        self.assertNotIn("secret-home", sink.getvalue())
        self.assertIn("explicit --build-flash-mb required", sink.getvalue())
        self.assertFalse(json.loads(sink.getvalue())["flash_authorized"])

    def test_cli_v19_image_size_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "private.txt"
            p.write_text(V4, encoding="utf-8")
            sink = StringIO()
            with redirect_stdout(sink):
                status = main([str(p), "--build-flash-mb", "8"])
            self.assertEqual(status, 0)
            data = json.loads(sink.getvalue())
            self.assertEqual(data["build_flash_mb_declared"], 8)
            self.assertEqual(data["gate"], "TRANSCRIPT_PARSED_FLASH_NOT_AUTHORIZED")
            self.assertNotIn("aa:bb", sink.getvalue())

    def test_mac_redacted(self):
        self.assertNotIn("aa:bb", repr(inspect_transcript(V4, 8)))

    def test_wrong_chip(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("ESP32-S3", "ESP32-C3"), 8)

    def test_missing_chip(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("Chip is ", "Chip maybe "), 8)

    def test_missing_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("Detected flash size:", "Guessed flash size:"), 8)

    def test_multiple_sizes(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "Detected flash size: 2MB\n", 8)

    def test_multiple_chips(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "Chip is ESP32-S3\n", 8)

    def test_fatal_error(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "A fatal error occurred: bad link\n", 8)

    def test_warning(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "WARNING: flash probe fallback\n", 8)

    def test_unsupported_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("8MB", "3MB"), 8)

    def test_invalid_build_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4, 3)

    def test_noisy_ambiguous_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("8MB", "8MB extra"), 8)

    def test_missing_private_path_not_echoed(self):
        sink = StringIO()
        with redirect_stdout(sink):
            status = main(["/private/secret-home/esp32-flash-id.txt", "--build-flash-mb", "8"])
        self.assertEqual(status, 2)
        self.assertNotIn("secret-home", sink.getvalue())
        self.assertIn("HOLD_PROBE_REJECTED", sink.getvalue())

    def test_oversized(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + " " * 100000, 8)


if __name__ == "__main__":
    unittest.main()
