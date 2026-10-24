"""Capture raw serial bytes without claiming physical sensor provenance.

CLI requires pyserial; injectable capture core uses Python standard library.
Output is private operator data: inspect for credentials before sharing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

MAX_RAW_BYTES = 10_000_000


class CaptureError(ValueError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def outside_git_tree(path):
    """Reject storing raw hardware output under any existing .git worktree."""
    resolved = Path(path).resolve()
    if any((parent / ".git").exists() for parent in (resolved, *resolved.parents)):
        raise CaptureError("raw serial output must be outside a Git worktree")


def capture(open_serial, output_dir, *, port, baudrate=115200, seconds=610,
            monotonic=time.monotonic, now=utc_now, max_bytes=MAX_RAW_BYTES,
            reader_version="TBD"):
    """Preserve bytes exactly; complete only after host monotonic duration.

    open_serial is a callable with pyserial's port/baudrate/timeout signature.
    A completed host capture is NOT a valid sensor/firmware attestation.
    """
    if not isinstance(port, str) or not port.strip():
        raise CaptureError("port must be nonempty")
    if type(baudrate) is not int or not 9600 <= baudrate <= 1_000_000:
        raise CaptureError("invalid baudrate")
    if type(seconds) not in (int, float) or not 0 < seconds <= 3600:
        raise CaptureError("duration must be 0 < seconds <= 3600")
    if type(max_bytes) is not int or max_bytes < 1 or max_bytes > MAX_RAW_BYTES:
        raise CaptureError("invalid maximum raw size")
    outside_git_tree(output_dir)
    out = Path(output_dir)
    out.mkdir(parents=False, exist_ok=False)
    partial = out / "raw_serial.partial"
    final = out / "raw_serial.log"
    meta = {
        "schema_version": "iot-host-serial-capture-v1",
        "port_operator_declared": port,
        "baudrate": baudrate,
        "requested_host_duration_seconds": seconds,
        "host_start_utc": now(),
        "host_end_utc": "TBD",
        "host_monotonic_elapsed_seconds": "TBD",
        "first_byte_host_offset_seconds": "TBD",
        "last_byte_host_offset_seconds": "TBD",
        "bytes_captured": 0,
        "raw_sha256": "TBD",
        "capture_status": "FAILED_OR_INTERRUPTED",
        "serial_reader_version": reader_version,
        "firmware_sha256": "TBD",
        "physical_sensor_origin_verified": False,
        "device_monotonic_span_verified": False,
        "notes": "Operator-controlled host serial capture only; not a sensor or flashed-firmware attestation. Review raw bytes for secrets before sharing.",
    }
    serial = None
    start = None
    digest = hashlib.sha256()
    count = 0
    error = None
    try:
        with partial.open("xb") as stream:
            serial = open_serial(port=port, baudrate=baudrate, timeout=0.25)
            start = monotonic()
            while True:
                elapsed = monotonic() - start
                if elapsed < 0:
                    raise CaptureError("host monotonic clock reversed")
                if elapsed >= seconds:
                    break
                block = serial.read(4096)
                if not isinstance(block, bytes):
                    raise CaptureError("serial reader returned non-bytes")
                if not block:
                    continue
                if count + len(block) > max_bytes:
                    raise CaptureError("raw serial size limit reached; incomplete capture")
                offset = monotonic() - start
                if offset < 0:
                    raise CaptureError("host monotonic clock reversed")
                if count == 0:
                    meta["first_byte_host_offset_seconds"] = round(offset, 6)
                meta["last_byte_host_offset_seconds"] = round(offset, 6)
                stream.write(block)
                digest.update(block)
                count += len(block)
            stream.flush()
            os.fsync(stream.fileno())
        if count == 0:
            raise CaptureError("no bytes received during requested host capture")
        partial.rename(final)
        meta["capture_status"] = "HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED"
    except BaseException as exc:
        error = exc
        meta["error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        if serial is not None:
            try:
                serial.close()
            except Exception as exc:
                meta["close_warning"] = type(exc).__name__
        meta["host_end_utc"] = now()
        if start is not None:
            delta = monotonic() - start
            meta["host_monotonic_elapsed_seconds"] = round(delta, 6) if delta >= 0 else "INVALID"
        meta["bytes_captured"] = count
        meta["raw_sha256"] = digest.hexdigest() if count else "TBD"
        (out / "capture_manifest.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if error is not None:
        raise CaptureError("capture failed; preserve partial and manifest: " + str(error)) from error
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", required=True, help="e.g. COM7 or /dev/ttyUSB0")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--seconds", type=int, default=610)
    p.add_argument("--out", type=Path, required=True, help="new directory OUTSIDE any Git worktree")
    a = p.parse_args()
    try:
        import serial
    except ImportError:
        p.exit(2, "pyserial required for physical port access; pip install pyserial\n")
    try:
        result = capture(serial.Serial, a.out, port=a.port, baudrate=a.baud,
                         seconds=a.seconds, reader_version=serial.__version__)
    except (OSError, CaptureError) as exc:
        p.exit(2, f"HOST_CAPTURE_FAILED: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
