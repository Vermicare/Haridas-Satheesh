"""Synthetic injected-port tests. No actual serial port or sensor is used."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from serial_acquire import CaptureError, capture, outside_git_tree


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def __call__(self):
        self.value += 0.25
        return self.value


class FakePort:
    def __init__(self, chunks, fail=False):
        self.chunks = iter(chunks)
        self.fail = fail
        self.closed = False

    def read(self, size):
        if self.fail:
            raise OSError("injected read failure")
        return next(self.chunks, b"")

    def close(self):
        self.closed = True


class HostCaptureContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.clock = FakeClock()

    def run_capture(self, chunks, *, fail=False, max_bytes=10_000_000):
        port = FakePort(chunks, fail=fail)
        def opener(**kwargs):
            self.assertEqual(kwargs, {"port": "FICTIONAL-COM", "baudrate": 115200, "timeout": 0.25})
            return port
        def run():
            return capture(opener, self.root / "capture", port="FICTIONAL-COM",
                           seconds=2, monotonic=self.clock, now=lambda: "2026-10-24T00:00:00Z",
                           max_bytes=max_bytes, reader_version="FAKE")
        return port, run

    def test_exact_raw_bytes_preserved_without_attestation(self):
        data = [b"BOOT\r\n", b"IOTCSV,abc,\xff\x00\n"]
        port, run = self.run_capture(data)
        report = run()
        self.assertTrue(port.closed)
        self.assertEqual((self.root / "capture/raw_serial.log").read_bytes(), b"".join(data))
        self.assertEqual(report["raw_sha256"], hashlib.sha256(b"".join(data)).hexdigest())
        self.assertFalse(report["physical_sensor_origin_verified"])
        self.assertFalse(report["device_monotonic_span_verified"])
        self.assertEqual(report["capture_status"], "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED")
        self.assertEqual(json.loads((self.root / "capture/capture_manifest.json").read_text()), report)

    def test_no_data_fails_and_preserves_manifest(self):
        port, run = self.run_capture([])
        with self.assertRaisesRegex(CaptureError, "no bytes"):
            run()
        self.assertTrue(port.closed)
        self.assertTrue((self.root / "capture/raw_serial.partial").exists())
        self.assertFalse((self.root / "capture/raw_serial.log").exists())
        self.assertEqual(json.loads((self.root / "capture/capture_manifest.json").read_text())["capture_status"], "FAILED_OR_INTERRUPTED")

    def test_reader_failure_preserves_partial(self):
        port, run = self.run_capture([b"x"], fail=True)
        with self.assertRaisesRegex(CaptureError, "injected read failure"):
            run()
        self.assertTrue(port.closed)
        self.assertTrue((self.root / "capture/raw_serial.partial").exists())

    def test_size_limit_fails_without_silent_truncation(self):
        port, run = self.run_capture([b"AB", b"CD"], max_bytes=3)
        with self.assertRaisesRegex(CaptureError, "size limit"):
            run()
        self.assertEqual((self.root / "capture/raw_serial.partial").read_bytes(), b"AB")
        self.assertTrue(port.closed)

    def test_reject_nonbytes(self):
        _, run = self.run_capture(["not bytes"])
        with self.assertRaisesRegex(CaptureError, "non-bytes"):
            run()

    def test_reject_existing_output_directory(self):
        (self.root / "capture").mkdir()
        _, run = self.run_capture([b"X"])
        with self.assertRaises(FileExistsError):
            run()

    def test_reject_invalid_port(self):
        with self.assertRaisesRegex(CaptureError, "port"):
            capture(lambda **kw: None, self.root / "new", port="", seconds=1)
        self.assertFalse((self.root / "new").exists())

    def test_reject_invalid_baud(self):
        with self.assertRaisesRegex(CaptureError, "baudrate"):
            capture(lambda **kw: None, self.root / "new", port="X", baudrate=True, seconds=1)

    def test_reject_invalid_duration(self):
        with self.assertRaisesRegex(CaptureError, "duration"):
            capture(lambda **kw: None, self.root / "new", port="X", seconds=0)

    def test_refuse_git_worktree_raw_output(self):
        (self.root / ".git").mkdir()
        with self.assertRaisesRegex(CaptureError, "outside a Git"):
            outside_git_tree(self.root / "private/raw")

    def test_failed_port_open_leaves_failure_manifest(self):
        def fail_open(**kwargs):
            raise OSError("injected port open error")
        with self.assertRaisesRegex(CaptureError, "injected port open"):
            capture(fail_open, self.root / "capture", port="X", seconds=1,
                    monotonic=self.clock, now=lambda: "2026-10-24T00:00:00Z")
        self.assertTrue((self.root / "capture/raw_serial.partial").exists())
        self.assertTrue((self.root / "capture/capture_manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
