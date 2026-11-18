#!/usr/bin/env python3
"""Fail-closed static audit of an UNFLASHED ESP32-S3 GitHub Actions firmware ZIP.

This tool cannot identify hardware, verify flashed bytes, or authorize flashing.
"""
import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

from firmware_internal_integrity import FirmwareIntegrityError, validate_bundle_internal

EXPECTED_HASHES = {
    "iot_dual_sensor_capture.bin",
    "bootloader/bootloader.bin",
    "partition_table/partition-table.bin",
    "flasher_args.json",
}
EXPECTED_FILES = EXPECTED_HASHES | {"SHA256SUMS.txt", "BUILD_PROVENANCE.txt"}
FLASH_OFFSETS = {
    "bootloader/bootloader.bin": 0x0,
    "partition_table/partition-table.bin": 0x8000,
    "iot_dual_sensor_capture.bin": 0x10000,
}
MAX_UNCOMPRESSED_BYTES = 8 * 1024 * 1024


class AuditError(ValueError):
    pass


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_flash_size(s):
    if not isinstance(s, str) or not re.fullmatch(r"[1-9][0-9]*MB", s):
        raise AuditError("invalid declared flash size")
    n = int(s[:-2])
    if not 1 <= n <= 64:
        raise AuditError("flash size outside supported audit range")
    return n * 1024 * 1024


def _parse_partitions(data):
    if len(data) < 32 or len(data) % 32:
        raise AuditError("invalid partition-table binary size")
    found = []
    for i in range(0, len(data), 32):
        entry = data[i:i + 32]
        magic, ptype, subtype, offset, size = struct.unpack_from("<HBBII", entry)
        if magic == 0xFFFF or magic == 0xEBEB:
            break
        if magic != 0x50AA:
            raise AuditError(f"invalid partition entry magic at {i}")
        try:
            name = entry[12:28].split(b"\0", 1)[0].decode("ascii", errors="strict")
        except UnicodeDecodeError as e:
            raise AuditError("invalid partition name encoding") from e
        if not name or size == 0:
            raise AuditError("empty partition name or size")
        found.append({"name": name, "type": ptype, "subtype": subtype,
                      "offset": offset, "size": size})
    if not found:
        raise AuditError("no partition entries")
    ranges = sorted((p["offset"], p["offset"] + p["size"], p["name"]) for p in found)
    for left, right in zip(ranges, ranges[1:]):
        if left[1] > right[0]:
            raise AuditError(f"overlapping partitions: {left[2]} and {right[2]}")
    return found


def audit_zip(path, observed_flash_mb=None, expected_pr_head=None):
    raw_zip = Path(path).read_bytes()
    archive_hash = hashlib.sha256(raw_zip).hexdigest()
    try:
        with zipfile.ZipFile(path) as z:
            entries = z.infolist()
            names = [e.filename for e in entries]
            if len(names) != len(set(names)):
                raise AuditError("duplicate archive entries")
            if set(names) != EXPECTED_FILES:
                raise AuditError("unexpected/missing archive members: " +
                                 repr(sorted(set(names) ^ EXPECTED_FILES)))
            for e in entries:
                if e.is_dir() or e.filename.startswith("/") or ".." in e.filename.split("/"):
                    raise AuditError("unsafe archive path")
                if (e.external_attr >> 16) & 0o170000 == 0o120000:
                    raise AuditError("symlink archive member")
                if e.file_size > MAX_UNCOMPRESSED_BYTES:
                    raise AuditError("oversized archive member")
            files = {name: z.read(name) for name in names}
    except (zipfile.BadZipFile, RuntimeError, OSError) as e:
        raise AuditError("unreadable ZIP: " + str(e)) from e

    try:
        lines = files["SHA256SUMS.txt"].decode("ascii").splitlines()
    except UnicodeError as e:
        raise AuditError("non-ASCII checksum file") from e
    digests = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        if not match:
            raise AuditError("malformed checksum entry")
        digest, name = match.groups()
        if name in digests:
            raise AuditError("duplicate checksum entry")
        digests[name] = digest
    if set(digests) != EXPECTED_HASHES:
        raise AuditError("checksum coverage mismatch")
    for name, digest in digests.items():
        if hashlib.sha256(files[name]).hexdigest() != digest:
            raise AuditError("checksum mismatch: " + name)

    try:
        args = json.loads(files["flasher_args.json"], object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeError, json.JSONDecodeError, TypeError) as e:
        raise AuditError("invalid flash JSON") from e
    settings = args.get("flash_settings")
    if not isinstance(settings, dict):
        raise AuditError("missing flash settings")
    declared = _parse_flash_size(settings.get("flash_size"))
    if args.get("write_flash_args", [None])[0:2] != ["--flash-mode", settings.get("flash_mode")]:
        raise AuditError("inconsistent flash-mode arguments")
    if "--flash-size" not in args["write_flash_args"] or args["write_flash_args"][args["write_flash_args"].index("--flash-size") + 1] != settings["flash_size"]:
        raise AuditError("inconsistent flash-size arguments")
    flash_files = args.get("flash_files")
    if not isinstance(flash_files, dict) or set(flash_files.values()) != set(FLASH_OFFSETS):
        raise AuditError("unexpected flash file mapping")
    actual_offsets = {}
    for offset_str, name in flash_files.items():
        if not isinstance(offset_str, str) or not re.fullmatch(r"0x[0-9a-fA-F]+", offset_str):
            raise AuditError("invalid flash offset")
        offset = int(offset_str, 16)
        if offset != FLASH_OFFSETS[name]:
            raise AuditError("unexpected flash offset for " + name)
        actual_offsets[name] = offset
    spans = sorted((off, off + len(files[name]), name) for name, off in actual_offsets.items())
    for start, end, name in spans:
        if end > declared:
            raise AuditError("flash file exceeds declared flash size: " + name)
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            raise AuditError("overlapping flash file ranges")
    if files["iot_dual_sensor_capture.bin"][0] != 0xE9 or files["bootloader/bootloader.bin"][0] != 0xE9:
        raise AuditError("ESP image magic not present")
    partitions = _parse_partitions(files["partition_table/partition-table.bin"])
    if any(p["offset"] + p["size"] > declared for p in partitions):
        raise AuditError("partition extends beyond declared flash capacity")
    factory = [p for p in partitions if p["type"] == 0 and p["subtype"] == 0]
    if len(factory) != 1 or factory[0]["offset"] != FLASH_OFFSETS["iot_dual_sensor_capture.bin"]:
        raise AuditError("factory partition missing or not at app offset")
    if len(files["iot_dual_sensor_capture.bin"]) > factory[0]["size"]:
        raise AuditError("application does not fit factory partition")

    # A rehashed ZIP can still contain a corrupted or wrong-chip ESP image.
    # Check each image's own segment XOR/SHA256 and the partition-table MD5.
    try:
        internal = validate_bundle_internal(files, settings)
    except FirmwareIntegrityError as exc:
        raise AuditError("internal firmware integrity: " + str(exc)) from exc

    try:
        provenance = files["BUILD_PROVENANCE.txt"].decode("ascii")
    except UnicodeError as e:
        raise AuditError("non-ASCII provenance") from e
    lines = provenance.splitlines()
    if any("=" not in line for line in lines):
        raise AuditError("malformed provenance line")
    pairs = [line.split("=", 1) for line in lines]
    prov = _pairs_no_duplicates(pairs)
    if (prov.get("repository") != "Vermicare/Haridas-Satheesh" or
        prov.get("target") != "esp32s3" or
        prov.get("evidence") != "UNFLASHED_CI_BUILD_ONLY" or
        prov.get("physical_sensor_capture") != "NOT_PERFORMED" or
        prov.get("esp_idf_requested") != "v6.1"):
        raise AuditError("unexpected provenance contract")
    for key in ("checked_out_sha", "pr_head_sha"):
        if not re.fullmatch(r"[0-9a-f]{40}", prov.get(key, "")):
            raise AuditError("invalid provenance " + key)
    if expected_pr_head and prov["pr_head_sha"] != expected_pr_head:
        raise AuditError("PR head SHA does not match expected source revision")

    observed = observed_flash_mb * 1024 * 1024 if observed_flash_mb is not None else None
    if observed is not None and observed <= 0:
        raise AuditError("invalid observed flash capacity")
    flags = []
    if observed is None:
        flags.append("DEVICE_FLASH_SIZE_NOT_INDEPENDENTLY_OBSERVED")
    elif observed != declared:
        flags.append("BUILD_DECLARED_FLASH_SIZE_DIFFERS_FROM_DEVICE_REVIEW_REQUIRED")
    return {
        "status": "STATIC_PACKAGE_PASS_FLASH_NOT_AUTHORIZED",
        "flash_authorization": "HOLD_PENDING_OPERATOR_AND_DEVICE_REVIEW",
        "artifact_sha256": archive_hash,
        "pr_head_sha": prov["pr_head_sha"],
        "checked_out_sha": prov["checked_out_sha"],
        "declared_flash_bytes": declared,
        "observed_flash_bytes": observed if observed is not None else "TBD",
        "flash_size_review_flags": flags,
        "flash_file_spans": [{"path": n, "start": s, "end_exclusive": e} for s, e, n in spans],
        "factory_partition_bytes": factory[0]["size"],
        "app_binary_bytes": len(files["iot_dual_sensor_capture.bin"]),
        "verified_sha256": digests,
        "internal_image_integrity": internal,
        "device_identity": "TBD",
        "flashed_binary_identity": "TBD",
        "physical_sensor_measurements": "NONE",
        "limitations": "Static ZIP and layout audit only; no device probe, flash, I2C or calibration.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", help="Downloaded unflashed GitHub Actions ZIP")
    parser.add_argument("--observed-flash-mb", type=int, default=None,
                        help="Actual independently observed physical flash MB (not guessed from board name)")
    parser.add_argument("--expected-pr-head", default=None, help="Expected 40-character Git commit SHA")
    args = parser.parse_args(argv)
    try:
        result = audit_zip(args.zip, args.observed_flash_mb, args.expected_pr_head)
    except (AuditError, OSError, ValueError, IndexError, KeyError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
