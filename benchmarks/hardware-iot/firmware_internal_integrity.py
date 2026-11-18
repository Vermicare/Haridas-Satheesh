"""Fail-closed internal ESP32-S3 image/partition checks for UNFLASHED research artifacts.

Does not authenticate provenance, attest a flashed device, or authorize flashing.
Only accepts this project's expected ESP-IDF v6.1-style hashed image format.
"""
import hashlib
import struct


class FirmwareIntegrityError(ValueError):
    pass


_FLASH_SIZE_CODES = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32, 6: 64, 7: 128}
_FLASH_MODES = {"qio": 0, "qout": 1, "dio": 2, "dout": 3}
_FLASH_FREQ_CODES = {"40m": 0, "26m": 1, "20m": 2, "80m": 15}


def validate_image(data, label, flash_settings):
    """Check segment boundaries, ESP32-S3 target, flash header, XOR and embedded SHA256."""
    if len(data) < 24 + 8 + 1 + 32 or data[0] != 0xE9:
        raise FirmwareIntegrityError(label + ": invalid/truncated ESP image")
    count = data[1]
    if not 1 <= count <= 16:
        raise FirmwareIntegrityError(label + ": invalid segment count")
    mode = flash_settings.get("flash_mode")
    freq = flash_settings.get("flash_freq")
    size = flash_settings.get("flash_size")
    if mode not in _FLASH_MODES or freq not in _FLASH_FREQ_CODES:
        raise FirmwareIntegrityError(label + ": unsupported flash setting")
    if data[2] != _FLASH_MODES[mode]:
        raise FirmwareIntegrityError(label + ": image header flash mode mismatch")
    size_code = data[3] >> 4
    expected_size = _FLASH_SIZE_CODES.get(size_code)
    if expected_size is None or f"{expected_size}MB" != size:
        raise FirmwareIntegrityError(label + ": image header flash size mismatch")
    if (data[3] & 15) != _FLASH_FREQ_CODES[freq]:
        raise FirmwareIntegrityError(label + ": image header flash frequency mismatch")
    chip_id = struct.unpack_from("<H", data, 12)[0]
    if chip_id != 9:
        raise FirmwareIntegrityError(label + ": ESP32-S3 chip id mismatch")
    if data[23] != 1:
        raise FirmwareIntegrityError(label + ": embedded SHA256 flag missing")
    pos, checksum, segments = 24, 0xEF, []
    for _ in range(count):
        if pos + 8 > len(data):
            raise FirmwareIntegrityError(label + ": truncated segment header")
        address, length = struct.unpack_from("<II", data, pos)
        pos += 8
        if length == 0 or length > len(data) - pos:
            raise FirmwareIntegrityError(label + ": segment length out of bounds")
        for byte in data[pos:pos + length]:
            checksum ^= byte
        segments.append({"address": f"0x{address:08x}", "bytes": length})
        pos += length
    checksum_offset = pos + ((15 - pos) % 16)
    if checksum_offset + 33 != len(data):
        raise FirmwareIntegrityError(label + ": unexpected padding/digest/trailing bytes")
    if any(data[pos:checksum_offset]):
        raise FirmwareIntegrityError(label + ": nonzero image padding")
    if data[checksum_offset] != checksum:
        raise FirmwareIntegrityError(label + ": segment XOR checksum mismatch")
    if hashlib.sha256(data[:checksum_offset + 1]).digest() != data[checksum_offset + 1:]:
        raise FirmwareIntegrityError(label + ": embedded image SHA256 mismatch")
    return {
        "chip_id": chip_id, "segment_count": count, "flash_size_mb": expected_size,
        "flash_mode": mode, "flash_frequency": freq,
        "embedded_sha256": data[checksum_offset + 1:].hex(),
        "segments": segments,
    }


def validate_partition_md5(data):
    """Validate the ESP-IDF partition-table MD5 trailer, not only ZIP-level SHA sums."""
    if len(data) < 64 or len(data) % 32:
        raise FirmwareIntegrityError("partition table: invalid size")
    for offset in range(0, len(data), 32):
        entry = data[offset:offset + 32]
        if entry[:2] == b"\xeb\xeb":
            if entry[2:16] != b"\xff" * 14:
                raise FirmwareIntegrityError("partition table: malformed MD5 marker")
            if hashlib.md5(data[:offset]).digest() != entry[16:32]:
                raise FirmwareIntegrityError("partition table: MD5 mismatch")
            if any(byte != 0xFF for byte in data[offset + 32:]):
                raise FirmwareIntegrityError("partition table: unexpected bytes after MD5")
            return {"partition_count": offset // 32, "md5": entry[16:32].hex()}
        if entry[:2] != b"\xaa\x50":
            raise FirmwareIntegrityError("partition table: missing MD5 or invalid entry")
    raise FirmwareIntegrityError("partition table: missing MD5 trailer")


def validate_bundle_internal(files, settings):
    return {
        "bootloader": validate_image(files["bootloader/bootloader.bin"], "bootloader", settings),
        "application": validate_image(files["iot_dual_sensor_capture.bin"], "application", settings),
        "partition_table": validate_partition_md5(files["partition_table/partition-table.bin"]),
        "physical_validation": "NOT_PERFORMED",
    }
