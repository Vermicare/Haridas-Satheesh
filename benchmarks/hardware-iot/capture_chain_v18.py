#!/usr/bin/env python3
"""Fail-closed host-capture-to-bundle integrity gate (fictional tests only).

Checks *declared* host capture completion and retained byte identity. Never
certifies physical origin, a flashed firmware binary, sensors or calibration.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path


MAX_RAW_BYTES = 10_000_000


def _unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key: " + key)
        out[key] = value
    return out


def _nonfinite(token):
    raise ValueError("nonfinite JSON number: " + token)


def _json(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"),
                       object_pairs_hook=_unique_pairs, parse_constant=_nonfinite)
    if not isinstance(value, dict):
        raise ValueError("manifest must be an object")
    return value


def _number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(name + " must be finite number (not boolean)")
    return value


def _utc(value):
    if not isinstance(value, str):
        raise ValueError("UTC stamp must be string")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be UTC")
    return d


def check_chain(capture_dir, bundle_dir):
    """Verify an existing raw capture + derived bundle without modifying either."""
    cap, bundle = Path(capture_dir), Path(bundle_dir)
    errors = []
    result = {"status": "REJECT_INVALID", "errors": errors,
              "physical_origin_verified": False, "flashed_firmware_verified": False,
              "limitation": "Host serial bytes and operator assertions are not independent physical attestation."}
    try:
        cm = _json(cap / "capture_manifest.json")
        bm = _json(bundle / "manifest.json")
        raw = (cap / "raw_serial.log").read_bytes()
        bundled_raw = (bundle / "raw_serial.log").read_bytes()
        if not raw or len(raw) > MAX_RAW_BYTES or len(bundled_raw) > MAX_RAW_BYTES:
            raise ValueError("raw capture empty or over 10 MB")
        if cm.get("schema_version") != "iot-host-serial-capture-v1":
            raise ValueError("host capture schema mismatch")
        if cm.get("capture_status") != "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED":
            raise ValueError("host capture is incomplete or interrupted")
        if (cap / "raw_serial.partial").exists():
            raise ValueError("partial raw capture remains; ambiguous completion")
        digest = hashlib.sha256(raw).hexdigest()
        if cm.get("raw_sha256") != digest:
            raise ValueError("host capture raw SHA-256 mismatch")
        if type(cm.get("bytes_captured")) is not int or cm["bytes_captured"] != len(raw):
            raise ValueError("host capture byte count mismatch")
        if raw != bundled_raw:
            raise ValueError("bundle raw bytes differ from host capture")
        if bm.get("raw_serial_sha256") != digest:
            raise ValueError("bundle raw SHA-256 mismatch")
        requested = _number(cm.get("requested_host_duration_seconds"), "requested duration")
        elapsed = _number(cm.get("host_monotonic_elapsed_seconds"), "host elapsed")
        first = _number(cm.get("first_byte_host_offset_seconds"), "first byte offset")
        last = _number(cm.get("last_byte_host_offset_seconds"), "last byte offset")
        if requested < 600 or elapsed < requested or elapsed < 600:
            raise ValueError("host duration does not establish ten-minute completed capture")
        if not 0 <= first <= last <= elapsed + 0.5:
            raise ValueError("host byte offsets inconsistent with monotonic duration")
        if not isinstance(cm.get("port_operator_declared"), str) or not cm["port_operator_declared"].strip():
            raise ValueError("missing host serial port declaration")
        if type(cm.get("baudrate")) is not int or not 9600 <= cm["baudrate"] <= 1_000_000:
            raise ValueError("invalid host baudrate")
        if _utc(cm.get("host_end_utc")) < _utc(cm.get("host_start_utc")):
            raise ValueError("host wall-clock end precedes start")
        csv_bytes = (bundle / "samples.csv").read_bytes()
        if not csv_bytes or len(csv_bytes) > 5_000_000:
            raise ValueError("derived CSV missing or exceeds 5 MB")
        if bm.get("csv_sha256") != hashlib.sha256(csv_bytes).hexdigest():
            raise ValueError("derived CSV SHA-256 mismatch")
        if bm.get("schema_version") != "iot-capture-preflight-v1":
            raise ValueError("bundle schema mismatch")
        if bm.get("capture_origin") not in ("synthetic", "physical"):
            raise ValueError("invalid operator-declared capture origin")
        result.update({"status": "HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD",
                       "host_raw_sha256": digest, "bytes": len(raw),
                       "host_elapsed_seconds": elapsed,
                       "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
                       "errors": [],
                       "required_next_gate": "Run serial_bundle.py verify separately; this chain gate does not parse telemetry, prove 600s device span, or attest physical origin."})
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        errors.append(str(exc))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("capture_dir", type=Path)
    p.add_argument("bundle_dir", type=Path)
    args = p.parse_args()
    report = check_chain(args.capture_dir, args.bundle_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"].startswith("HOST_CHAIN_INTEGRITY_PASS") else 2)


if __name__ == "__main__":
    main()
