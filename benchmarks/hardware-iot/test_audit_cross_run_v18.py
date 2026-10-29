"""Fictional ZIP negative controls; no device firmware or private telemetry."""
import hashlib
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from audit_cross_run_v18 import EvidenceError, HASHED, audit


def make(path, checkout, mutation=None):
    data = {n: (n.split("-")[0] + "-fictional\n").encode() for n in HASHED}
    data.update({
        "checkout_sha.txt": (checkout + "\n").encode(),
        "comparison_status.txt": b"MATCH\n",
        "compiler_version.txt": b"fictional-compiler 1.0\n",
        "idf_version.txt": b"fictional-IDF 1.0\n",
        "sdkconfig_sha256.txt": ("a" * 64 + "  sdkconfig\n").encode(),
    })
    if mutation == "cross_binary":
        for n in ("app-first.bin", "app-second.bin"):
            data[n] += b"different"
    if mutation == "within_binary":
        data["boot-second.bin"] += b"different"
    if mutation == "compiler":
        data["compiler_version.txt"] = b"fictional-compiler 2.0\n"
    if mutation == "config":
        data["sdkconfig_sha256.txt"] = b"b" * 64 + b"  sdkconfig\n"
    if mutation == "status":
        data["comparison_status.txt"] = b"MISMATCH\n"
    data["SHA256SUMS.txt"] = "".join(
        hashlib.sha256(data[n]).hexdigest() + "  " + n + "\n"
        for n in sorted(HASHED)).encode()
    if mutation == "tamper":
        data["app-first.bin"] += b"tamper"
    with zipfile.ZipFile(path, "w") as z:
        for name, payload in sorted(data.items()):
            z.writestr(name, payload)
        if mutation == "duplicate":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                z.writestr("app-first.bin", b"duplicate")
        if mutation == "extra":
            z.writestr("unexpected.txt", b"not allowed")


class CrossRunAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.a = Path(self.tmp.name) / "a.zip"
        self.b = Path(self.tmp.name) / "b.zip"
        make(self.a, "a" * 40)
        make(self.b, "b" * 40)

    def test_clean_cross_run(self):
        report = audit(self.a, self.b)
        self.assertEqual(report["gate"], "PASS_STATIC_UNFLASHED_BINARY_EQUALITY_SOURCE_REVIEW_REQUIRED")
        self.assertFalse(report["flash_authorized"])
        self.assertEqual(report["source_equivalence_from_artifacts"], "NOT_ESTABLISHED")

    def test_same_checkout_not_cross_run_case(self):
        make(self.b, "a" * 40)
        with self.assertRaisesRegex(EvidenceError, "distinct"):
            audit(self.a, self.b)

    def test_changed_binaries_even_with_updated_hashes(self):
        make(self.b, "b" * 40, "cross_binary")
        with self.assertRaisesRegex(EvidenceError, "cross-run binary mismatch"):
            audit(self.a, self.b)

    def test_within_run_mismatch_even_with_updated_hashes(self):
        make(self.b, "b" * 40, "within_binary")
        with self.assertRaisesRegex(EvidenceError, "within-run binary mismatch"):
            audit(self.a, self.b)

    def test_changed_compiler_rejected(self):
        make(self.b, "b" * 40, "compiler")
        with self.assertRaisesRegex(EvidenceError, "differs"):
            audit(self.a, self.b)

    def test_changed_config_rejected(self):
        make(self.b, "b" * 40, "config")
        with self.assertRaisesRegex(EvidenceError, "differs"):
            audit(self.a, self.b)

    def test_reported_mismatch_rejected(self):
        make(self.b, "b" * 40, "status")
        with self.assertRaisesRegex(EvidenceError, "not MATCH"):
            audit(self.a, self.b)

    def test_tampered_member_rejected(self):
        make(self.b, "b" * 40, "tamper")
        with self.assertRaisesRegex(EvidenceError, "manifest hash mismatch"):
            audit(self.a, self.b)

    def test_duplicate_member_rejected(self):
        make(self.b, "b" * 40, "duplicate")
        with self.assertRaisesRegex(EvidenceError, "duplicate"):
            audit(self.a, self.b)

    def test_extra_member_rejected(self):
        make(self.b, "b" * 40, "extra")
        with self.assertRaisesRegex(EvidenceError, "unexpected"):
            audit(self.a, self.b)

    def test_corrupted_zip_rejected(self):
        self.b.write_bytes(b"not a zip")
        with self.assertRaises(zipfile.BadZipFile):
            audit(self.a, self.b)


if __name__ == "__main__":
    unittest.main()
