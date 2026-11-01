"""Synthetic byte fixtures only; not a real-data acquisition or forecast."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import freshretail_lt_source_gate_v18 as gate


class SourceGateV18Tests(unittest.TestCase):
    def test_publisher_pin_is_frozen(self):
        self.assertEqual(gate.REVISION, "01c3bb306415e09d3ccd2fe762f33eb3aeb2affd")
        self.assertEqual(gate.TRAIN_BYTES, 315398578)
        self.assertEqual(gate.EVAL_BYTES, 2009424)
        self.assertEqual(len(gate.TRAIN_SHA256), 64)
        self.assertEqual(len(gate.EVAL_SHA256), 64)

    def test_fictional_fixture_accepts_exact_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fictional.bin"
            data = b"FICTIONAL_SOURCE_ONLY\x00\x01"
            path.write_bytes(data)
            result = gate.verify_file(path, len(data), hashlib.sha256(data).hexdigest())
            self.assertEqual(result["bytes"], len(data))
            self.assertIn("NOT_INDEPENDENT_AUTHENTICITY", result["verified_against"])

    def test_modified_and_truncated_fictional_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fictional.bin"
            data = b"FICTIONAL_SOURCE_ONLY"
            path.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            for changed in (data[:-1], data[:-1] + b"X", data + b"X"):
                with self.subTest(changed=changed):
                    path.write_bytes(changed)
                    with self.assertRaises(gate.SourceGateError):
                        gate.verify_file(path, len(data), expected)

    def test_invalid_expected_pins_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fictional.bin"
            path.write_bytes(b"x")
            for size, sha in ((True, "a"*64), (0, "a"*64), (1, "A"*64), (1, "a"*63), (1, None)):
                with self.subTest(size=size, sha=sha), self.assertRaises(gate.SourceGateError):
                    gate.verify_file(path, size, sha)

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(gate.SourceGateError):
                gate.verify_file(Path(d)/"absent", 1, "a"*64)

    def test_same_path_rejected_without_hashing(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"fictional.bin"
            path.write_bytes(b"x")
            with patch.object(gate, "verify_file", side_effect=AssertionError("must not hash")):
                with self.assertRaises(gate.SourceGateError):
                    gate.audit_sources(path, path)

    def test_production_gate_cannot_accept_fictional_pins(self):
        with tempfile.TemporaryDirectory() as d:
            t, e = Path(d)/"train", Path(d)/"eval"
            t.write_bytes(b"synthetic train")
            e.write_bytes(b"synthetic eval")
            with self.assertRaises(gate.SourceGateError):
                gate.audit_sources(t, e)


if __name__ == "__main__":
    unittest.main()
