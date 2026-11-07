import hashlib
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from compare_firmware_rebuild_v16 import HASHED, compare


def fixture(path, attempt="1", checkout="a" * 40, tamper=False, duplicate=False):
    payload = {name: (name + "\n").encode() for name in HASHED}
    checks = "".join(hashlib.sha256(payload[n]).hexdigest() + "  " + n + "\n"
                     for n in sorted(HASHED)).encode()
    prov = ("repository=Vermicare/Haridas-Satheesh\nchecked_out_sha=" + checkout +
            "\npr_head_sha=" + "b" * 40 + "\nrun_id=123\nrun_attempt=" + attempt + "\n").encode()
    payload.update({"SHA256SUMS.txt": checks, "BUILD_PROVENANCE.txt": prov})
    if tamper:
        payload["iot_dual_sensor_capture.bin"] += b"tampered"
    with zipfile.ZipFile(path, "w") as z:
        for name, data in payload.items():
            z.writestr(name, data)
        if duplicate:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                z.writestr("flasher_args.json", b"duplicate")


class CompareFirmwareRebuildV16Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.a = Path(self.tmp.name) / "a.zip"
        self.b = Path(self.tmp.name) / "b.zip"
        fixture(self.a, attempt="1")
        fixture(self.b, attempt="2")

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_source_two_attempts_accepted(self):
        report = compare(self.a, self.b)
        self.assertEqual(report["attempts"], ["1", "2"])
        self.assertTrue(report["files"]["flasher_args.json"]["identical"])
        self.assertFalse(report["files"]["BUILD_PROVENANCE.txt"]["identical"])

    def test_different_checkout_rejected(self):
        fixture(self.b, attempt="2", checkout="c" * 40)
        with self.assertRaisesRegex(ValueError, "not the same"):
            compare(self.a, self.b)

    def test_same_attempt_rejected(self):
        fixture(self.b, attempt="1")
        with self.assertRaisesRegex(ValueError, "distinct"):
            compare(self.a, self.b)

    def test_tampered_binary_rejected(self):
        fixture(self.b, attempt="2", tamper=True)
        with self.assertRaisesRegex(ValueError, "does not verify"):
            compare(self.a, self.b)

    def test_duplicate_zip_member_rejected(self):
        fixture(self.b, attempt="2", duplicate=True)
        with self.assertRaisesRegex(ValueError, "duplicate ZIP member"):
            compare(self.a, self.b)


if __name__ == "__main__":
    unittest.main()
