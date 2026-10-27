"""Fictional transcripts only: no physical device or esptool execution."""
import unittest
from read_only_flash_probe_v15 import inspect_transcript, ProbeError

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
        r = inspect_transcript(V4)
        self.assertEqual(r["observed_flash_mb_claimed"], 8)
        self.assertEqual(r["flash_size_comparison"], "DIFFERENT_REQUIRES_BOARD_CONFIGURATION_REVIEW")
        self.assertFalse(r["flashed_image_attested"])

    def test_v5_match_does_not_authorize_flash(self):
        r = inspect_transcript(V5)
        self.assertEqual(r["flash_size_comparison"], "MATCH")
        self.assertEqual(r["gate"], "TRANSCRIPT_PARSED_FLASH_NOT_AUTHORIZED")

    def test_mac_redacted(self):
        self.assertNotIn("aa:bb", repr(inspect_transcript(V4)))

    def test_wrong_chip(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("ESP32-S3", "ESP32-C3"))

    def test_missing_chip(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("Chip is ", "Chip maybe "))

    def test_missing_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("Detected flash size:", "Guessed flash size:"))

    def test_multiple_sizes(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "Detected flash size: 2MB\n")

    def test_multiple_chips(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "Chip is ESP32-S3\n")

    def test_fatal_error(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "A fatal error occurred: bad link\n")

    def test_warning(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + "WARNING: flash probe fallback\n")

    def test_unsupported_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("8MB", "3MB"))

    def test_invalid_build_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4, 3)

    def test_noisy_ambiguous_size(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4.replace("8MB", "8MB extra"))

    def test_oversized(self):
        with self.assertRaises(ProbeError):
            inspect_transcript(V4 + " " * 100000)


if __name__ == "__main__":
    unittest.main()
