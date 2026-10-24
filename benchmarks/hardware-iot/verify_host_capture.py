"""Fail-closed integrity checks for *operator-declared* host serial captures.

Checks bytes and manifest consistency only. Neither sensor authenticity nor
firmware identity, device clock, or physical origin can be inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

COMPLETE = "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED"
FAILED = "FAILED_OR_INTERRUPTED"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class VerificationError(ValueError):
    pass


def _unique_pairs(pairs):
    d = {}
    for key, value in pairs:
        if key in d:
            raise VerificationError("duplicate manifest key: " + key)
        d[key] = value
    return d


def _regular_file(path):
    if path.is_symlink() or not path.is_file():
        raise VerificationError("missing, nonregular, or symlink file: " + path.name)
    return path.read_bytes()


def verify(directory):
    """Return structural result; raise on inconsistency. Never attest hardware."""
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise VerificationError("capture directory is absent or a symlink")
    try:
        manifest = json.loads(_regular_file(root / "capture_manifest.json"),
                              object_pairs_hook=_unique_pairs)
    except (ValueError, UnicodeDecodeError) as exc:
        raise VerificationError("invalid capture manifest: " + str(exc)) from exc
    if not isinstance(manifest, dict):
        raise VerificationError("manifest must be a JSON object")
    if manifest.get("schema_version") != "iot-host-serial-capture-v1":
        raise VerificationError("unexpected manifest schema")
    status = manifest.get("capture_status")
    if status not in (COMPLETE, FAILED):
        raise VerificationError("unknown capture status")
    raw = root / ("raw_serial.log" if status == COMPLETE else "raw_serial.partial")
    other = root / ("raw_serial.partial" if status == COMPLETE else "raw_serial.log")
    if other.exists() or other.is_symlink():
        raise VerificationError("conflicting raw capture file")
    data = _regular_file(raw)
    count = manifest.get("bytes_captured")
    if type(count) is not int or count != len(data):
        raise VerificationError("raw byte count mismatch")
    actual_sha = hashlib.sha256(data).hexdigest()
    if count:
        if not isinstance(manifest.get("raw_sha256"), str) or not SHA256.fullmatch(manifest["raw_sha256"]):
            raise VerificationError("invalid raw checksum declaration")
        if actual_sha != manifest["raw_sha256"]:
            raise VerificationError("raw SHA-256 mismatch")
    elif manifest.get("raw_sha256") != "TBD":
        raise VerificationError("empty raw capture must declare checksum TBD")
    requested = manifest.get("requested_host_duration_seconds")
    elapsed = manifest.get("host_monotonic_elapsed_seconds")
    if type(requested) not in (int, float) or not 0 < requested <= 3600:
        raise VerificationError("invalid requested duration")
    if status == COMPLETE:
        if not count:
            raise VerificationError("completed capture has zero bytes")
        if type(elapsed) not in (int, float) or elapsed < requested:
            raise VerificationError("completed capture lacks required host elapsed duration")
        first = manifest.get("first_byte_host_offset_seconds")
        last = manifest.get("last_byte_host_offset_seconds")
        if (type(first) not in (int, float) or type(last) not in (int, float)
                or first < 0 or last < first or last > elapsed):
            raise VerificationError("invalid first/last host byte offsets")
    return {
        "status": "INTEGRITY_PASS_PROVENANCE_UNVERIFIED" if status == COMPLETE else "INCOMPLETE_CAPTURE_PRESERVED",
        "capture_status": status,
        "bytes_verified": count,
        "raw_sha256": actual_sha if count else "TBD",
        "physical_sensor_origin_verified": False,
        "firmware_attested": False,
        "device_monotonic_span_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.directory)
    except (OSError, VerificationError) as exc:
        parser.exit(2, "INTEGRITY_FAIL: " + str(exc) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
