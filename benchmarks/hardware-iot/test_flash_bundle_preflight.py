"""Synthetic-only adversarial tests; never represent fabricated bytes as device firmware."""
import hashlib
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from flash_bundle_preflight import AuditError, audit_zip

HEAD = "a" * 40


def fake_esp_image(payload):
    """Synthetic ESP32-S3 image: structural fixture, never flash to a board."""
    header = bytearray(24)
    header[0] = 0xE9
    header[1] = 1
    header[2] = 2  # DIO
    header[3] = 0x1F  # 2 MB, 80 MHz
    struct.pack_into("<H", header, 12, 9)  # ESP32-S3
    header[23] = 1  # appended digest
    body = bytes(header) + struct.pack("<II", 0x3FC90000, len(payload)) + payload
    body += bytes((15 - len(body)) % 16)
    checksum = 0xEF
    for byte in payload:
        checksum ^= byte
    body += bytes([checksum])
    return body + hashlib.sha256(body).digest()


def fake_members():
    # Minimal fictional partition table with one factory partition; NOT valid firmware.
    part = bytearray(b"\xff" * 96)
    struct.pack_into("<HBBII", part, 0, 0x50AA, 0, 0, 0x10000, 0x100000)
    part[12:20] = b"factory\x00"
    part[32:48] = bytes.fromhex("ebeb") + bytes([0xFF] * 14)
    part[48:64] = hashlib.md5(part[:32]).digest()
    args = {
        "flash_settings": {"flash_mode": "dio", "flash_size": "2MB", "flash_freq": "80m"},
        "write_flash_args": ["--flash-mode", "dio", "--flash-size", "2MB", "--flash-freq", "80m"],
        "flash_files": {"0x0": "bootloader/bootloader.bin", "0x8000": "partition_table/partition-table.bin", "0x10000": "iot_dual_sensor_capture.bin"},
    }
    provenance = "\n".join([
        "repository=Vermicare/Haridas-Satheesh", "checked_out_sha=" + "b" * 40,
        "event=pull_request", "pr_head_sha=" + HEAD, "esp_idf_requested=v6.1",
        "target=esp32s3", "evidence=UNFLASHED_CI_BUILD_ONLY",
        "physical_sensor_capture=NOT_PERFORMED", "device_identity=TBD", "",
    ])
    return {
        "iot_dual_sensor_capture.bin": fake_esp_image(b"fictional-app"),
        "bootloader/bootloader.bin": fake_esp_image(b"fictional-bootloader"),
        "partition_table/partition-table.bin": bytes(part),
        "flasher_args.json": json.dumps(args).encode(),
        "BUILD_PROVENANCE.txt": provenance.encode(),
    }


def write_zip(path, members, rehash=True):
    data = dict(members)
    if rehash:
        names = ["iot_dual_sensor_capture.bin", "bootloader/bootloader.bin",
                 "partition_table/partition-table.bin", "flasher_args.json"]
        data["SHA256SUMS.txt"] = "".join(
            hashlib.sha256(data[name]).hexdigest() + "  " + name + "\n" for name in names
        ).encode()
    with zipfile.ZipFile(path, "w") as z:
        for name, value in data.items():
            z.writestr(name, value)


class BundlePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fixture.zip"
        self.members = fake_members()

    def audit(self, observed=None, expected=HEAD, rehash=True):
        write_zip(self.path, self.members, rehash=rehash)
        return audit_zip(self.path, observed_flash_mb=observed, expected_pr_head=expected)

    def test_valid_fictional_package_remains_unflashed_hold(self):
        r = self.audit()
        self.assertEqual(r["status"], "STATIC_PACKAGE_PASS_FLASH_NOT_AUTHORIZED")
        self.assertEqual(r["observed_flash_bytes"], "TBD")
        self.assertEqual(r["physical_sensor_measurements"], "NONE")

    def test_observed_flash_size_mismatch_requires_review(self):
        r = self.audit(observed=8)
        self.assertIn("BUILD_DECLARED_FLASH_SIZE_DIFFERS_FROM_DEVICE_REVIEW_REQUIRED", r["flash_size_review_flags"])
        self.assertEqual(r["flash_authorization"], "HOLD_PENDING_OPERATOR_AND_DEVICE_REVIEW")

    def test_same_size_still_cannot_authorize_flash(self):
        r = self.audit(observed=2)
        self.assertFalse(r["flash_size_review_flags"])
        self.assertIn("HOLD", r["flash_authorization"])

    def test_mismatched_expected_pr_head_rejected(self):
        with self.assertRaisesRegex(AuditError, "PR head SHA"):
            self.audit(expected="c" * 40)

    def test_corrupted_binary_rejected_by_checksum(self):
        self.audit()
        with zipfile.ZipFile(self.path) as z:
            files = {n: z.read(n) for n in z.namelist()}
        files["iot_dual_sensor_capture.bin"] += b"tamper"
        write_zip(self.path, files, rehash=False)
        with self.assertRaisesRegex(AuditError, "checksum mismatch"):
            audit_zip(self.path)

    def test_wrong_flash_offset_rejected_even_when_rehashed(self):
        args = json.loads(self.members["flasher_args.json"])
        args["flash_files"]["0x20000"] = args["flash_files"].pop("0x10000")
        self.members["flasher_args.json"] = json.dumps(args).encode()
        with self.assertRaisesRegex(AuditError, "unexpected flash offset"):
            self.audit()

    def test_duplicate_json_key_rejected(self):
        self.members["flasher_args.json"] = self.members["flasher_args.json"].replace(
            b'"flash_size": "2MB"', b'"flash_size": "2MB", "flash_size": "8MB"')
        with self.assertRaisesRegex(AuditError, "duplicate JSON key"):
            self.audit()

    def test_app_overflows_factory_partition(self):
        self.members["iot_dual_sensor_capture.bin"] = b"\xe9" + b"x" * (0x100000 + 1)
        with self.assertRaisesRegex(AuditError, "application does not fit"):
            self.audit()

    def test_partition_outside_declared_flash(self):
        part = bytearray(self.members["partition_table/partition-table.bin"])
        struct.pack_into("<I", part, 8, 0x300000)
        self.members["partition_table/partition-table.bin"] = bytes(part)
        with self.assertRaisesRegex(AuditError, "partition extends"):
            self.audit()

    def test_malformed_provenance_rejected(self):
        self.members["BUILD_PROVENANCE.txt"] = self.members["BUILD_PROVENANCE.txt"].replace(
            b"UNFLASHED_CI_BUILD_ONLY", b"PHYSICAL_VALIDATED")
        with self.assertRaisesRegex(AuditError, "unexpected provenance"):
            self.audit()

    def test_unexpected_archive_member_rejected(self):
        self.members["secrets.txt"] = b"fictional"
        with self.assertRaisesRegex(AuditError, "unexpected/missing"):
            self.audit()

    def test_duplicate_zip_member_rejected(self):
        write_zip(self.path, self.members)
        with zipfile.ZipFile(self.path, "a") as z:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                z.writestr("BUILD_PROVENANCE.txt", b"extra")
        with self.assertRaisesRegex(AuditError, "duplicate archive entries"):
            audit_zip(self.path)

    def test_bad_image_magic_rejected(self):
        self.members["iot_dual_sensor_capture.bin"] = b"\x00" + b"x" * 100
        with self.assertRaisesRegex(AuditError, "ESP image magic"):
            self.audit()

    def test_overlapping_partitions_rejected(self):
        part = bytearray(self.members["partition_table/partition-table.bin"])
        struct.pack_into("<HBBII", part, 32, 0x50AA, 1, 2, 0x10000, 0x1000)
        part[44:49] = b"test\x00"
        self.members["partition_table/partition-table.bin"] = bytes(part)
        with self.assertRaisesRegex(AuditError, "overlapping partitions"):
            self.audit()


    def test_internal_header_and_partition_digests_are_verified(self):
        r = self.audit()
        internal = r["internal_image_integrity"]
        self.assertEqual(internal["application"]["chip_id"], 9)
        self.assertEqual(internal["bootloader"]["segment_count"], 1)
        self.assertEqual(internal["partition_table"]["partition_count"], 1)
        self.assertEqual(r["flash_authorization"], "HOLD_PENDING_OPERATOR_AND_DEVICE_REVIEW")

    def test_wrong_chip_id_rejected_even_with_new_zip_hashes(self):
        image = bytearray(self.members["iot_dual_sensor_capture.bin"])
        struct.pack_into("<H", image, 12, 0)
        self.members["iot_dual_sensor_capture.bin"] = bytes(image)
        with self.assertRaisesRegex(AuditError, "chip id mismatch"):
            self.audit()

    def test_wrong_image_header_flash_size_rejected(self):
        image = bytearray(self.members["bootloader/bootloader.bin"])
        image[3] = 0x3F
        self.members["bootloader/bootloader.bin"] = bytes(image)
        with self.assertRaisesRegex(AuditError, "image header flash size"):
            self.audit()

    def test_forged_embedded_image_digest_rejected(self):
        image = bytearray(self.members["iot_dual_sensor_capture.bin"])
        image[-1] ^= 1
        self.members["iot_dual_sensor_capture.bin"] = bytes(image)
        with self.assertRaisesRegex(AuditError, "embedded image SHA256 mismatch"):
            self.audit()

    def test_forged_partition_entry_with_stale_md5_rejected(self):
        part = bytearray(self.members["partition_table/partition-table.bin"])
        part[12] ^= 1
        self.members["partition_table/partition-table.bin"] = bytes(part)
        with self.assertRaisesRegex(AuditError, "partition table: MD5 mismatch"):
            self.audit()

    def test_segment_xor_corruption_rejected_with_new_zip_hashes(self):
        image = bytearray(self.members["iot_dual_sensor_capture.bin"])
        image[32] ^= 1
        self.members["iot_dual_sensor_capture.bin"] = bytes(image)
        with self.assertRaisesRegex(AuditError, "segment XOR checksum mismatch"):
            self.audit()

    def test_missing_embedded_image_digest_flag_rejected(self):
        image = bytearray(self.members["iot_dual_sensor_capture.bin"])
        image[23] = 0
        self.members["iot_dual_sensor_capture.bin"] = bytes(image)
        with self.assertRaisesRegex(AuditError, "embedded SHA256 flag missing"):
            self.audit()

if __name__ == "__main__":
    unittest.main()
