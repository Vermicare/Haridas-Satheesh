"""Host-only C CRC/framing test. Never claims firmware build or sensor validation."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent / "firmware" / "espidf_dual_sensor_capture"
COMPILER = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")


class FirmwareWireContractTests(unittest.TestCase):
    @unittest.skipUnless(COMPILER, "no host C compiler; hardware and IDF build not tested")
    def test_crc_and_exact_serial_framing(self):
        with tempfile.TemporaryDirectory() as td:
            exe = Path(td) / ("wire_test.exe" if __import__("os").name == "nt" else "wire_test")
            cmd = [COMPILER, "-std=c11", "-Wall", "-Wextra", "-Werror",
                   "-I", str(ROOT / "main"), str(ROOT / "tests" / "telemetry_wire_test.c"),
                   "-o", str(exe)]
            built = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            tested = subprocess.run([str(exe)], capture_output=True, text=True)
            self.assertEqual(tested.returncode, 0, tested.stdout + tested.stderr)


if __name__ == "__main__":
    unittest.main()
