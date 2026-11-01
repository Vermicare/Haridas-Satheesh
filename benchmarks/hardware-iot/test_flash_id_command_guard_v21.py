"""All command and transcript inputs are fictional. No hardware is accessed."""
import json
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from flash_id_command_guard_v21 import (
    CommandGuardError, assess, main, validate_declared_command,
)

GOOD = "python -m esptool --chip esp32s3 -p COM7 flash-id"
LOG = "esptool v5.4.0\nChip type: ESP32-S3\nDetected flash size: 8MB\nMAC: aa:bb:cc:dd:ee:ff\n"


class CommandGuardTests(unittest.TestCase):
    def test_valid_v5_and_v4_forms(self):
        for cmd in (GOOD, "esptool.py --chip esp32s3 -p COM7 flash_id",
                    "esptool --port /dev/ttyACM0 --chip esp32s3 flash-id",
                    "py -m esptool -b 115200 --chip esp32s3 --port COM7 flash-id"):
            with self.subTest(cmd=cmd):
                result = validate_declared_command(cmd)
                self.assertFalse(result["flash_authorized"])
                self.assertEqual(result["port"], "REDACTED")
                self.assertFalse(result["command_execution_attested"])

    def test_reject_unsafe_and_ambiguous(self):
        invalid = (
            "", "esptool --chip esp32s3 -p COM7 write-flash",
            "esptool --chip esp32s3 -p COM7 erase-flash",
            GOOD + " ; erase_flash", GOOD + " && write_flash",
            GOOD + " | tee output.txt", GOOD + " > output.txt",
            GOOD + "\nwrite_flash", GOOD + " @args.txt",
            GOOD.replace("esp32s3", "esp32"),
            GOOD.replace("-p COM7", ""),
            GOOD.replace("-p COM7", "-p COM7 --port COM8"),
            GOOD.replace("COM7", "tcp://example.com:1234"),
            GOOD.replace("COM7", "COM7 --force"),
            GOOD.replace("flash-id", "flash-id read-mac"),
            GOOD.replace("python -m esptool", "python -c esptool"),
            GOOD.replace("flash-id", "flash-id --help"),
            GOOD.replace("-p COM7", "-p COM7 -b 99999999"),
            GOOD.replace("-p COM7", "-p COM7 -b notanumber"),
        )
        for cmd in invalid:
            with self.subTest(cmd=cmd):
                with self.assertRaises(CommandGuardError):
                    validate_declared_command(cmd)

    def test_mutating_output_rejected_before_transcript_parser(self):
        for extra in ("Flash will be erased from 0x0 to 0x1000...",
                      "Wrote 100 bytes at 0x0", "Hash of data verified.",
                      "write_flash", "erase-region", "Compressed 100 bytes to 80"):
            with self.subTest(extra=extra):
                with self.assertRaisesRegex(CommandGuardError, "write/erase"):
                    assess(GOOD, LOG + extra + "\n", 8)

    def test_delegation_never_attests_physical_origin(self):
        stub = types.ModuleType("read_only_flash_probe_v15")
        class ProbeError(ValueError):
            pass
        stub.ProbeError = ProbeError
        stub.inspect_transcript = lambda transcript, size: {
            "gate": "TRANSCRIPT_PARSED_FLASH_NOT_AUTHORIZED",
            "chip_family_claimed": "ESP32-S3", "observed_flash_mb_claimed": 8,
            "build_flash_mb_declared": size, "flash_size_comparison": "MATCH",
        }
        with patch.dict(sys.modules, {"read_only_flash_probe_v15": stub}):
            result = assess(GOOD, LOG, 8)
        self.assertFalse(result["physical_device_attested"])
        self.assertFalse(result["actual_command_proven"])
        self.assertFalse(result["flash_authorized"])
        self.assertEqual(result["psram_physical_identity"], "TBD")
        self.assertNotIn("aa:bb", json.dumps(result))
        self.assertNotIn("COM7", json.dumps(result))

    def test_cli_rejects_without_echoing_sensitive_content(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "command.txt").write_text(GOOD + " && write_flash SECRET", encoding="utf-8")
            (p / "log.txt").write_text(LOG, encoding="utf-8")
            sink = StringIO()
            with redirect_stdout(sink):
                code = main([str(p / "command.txt"), str(p / "log.txt"), "8"])
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(sink.getvalue())["flash_authorized"])
            self.assertNotIn("SECRET", sink.getvalue())
            self.assertNotIn(d, sink.getvalue())


if __name__ == "__main__":
    unittest.main()
