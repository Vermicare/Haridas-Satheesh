"""Cross-check private host serial acquisition against a derived telemetry bundle.

Structural integrity only: operator-controlled files and clocks are NOT proof
of sensor origin, flashed firmware, physical time, or measurement accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MIN_SPAN_SECONDS = 600.0
MIN_DEVICE_SPAN_MS = 600_000
MAX_RAW_BYTES = 10_000_000


class ChainError(ValueError):
    pass


def _regular_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ChainError("missing, nonregular or symlink input: " + path.name)
    if path.stat().st_size > MAX_RAW_BYTES:
        raise ChainError("input exceeds 10 MB: " + path.name)
    return path.read_bytes()


def verify_chain(host_dir, bundle_dir):
    """Fail closed unless acquisition, extraction and byte-chain all agree."""
    from verify_host_capture import verify as verify_host, VerificationError
    from serial_bundle import verify as verify_bundle

    host, bundle = Path(host_dir), Path(bundle_dir)
    if host.is_symlink() or bundle.is_symlink() or not host.is_dir() or not bundle.is_dir():
        raise ChainError("host and bundle must be existing nonsymlink directories")
    if host.resolve() == bundle.resolve():
        raise ChainError("host and bundle must be distinct directories")
    try:
        host_report = verify_host(host)
    except (VerificationError, OSError, ValueError) as exc:
        raise ChainError("host integrity failed: " + str(exc)) from exc
    if host_report.get("status") != "INTEGRITY_PASS_PROVENANCE_UNVERIFIED":
        raise ChainError("host acquisition is incomplete")
    bundle_report = verify_bundle(bundle)
    if bundle_report.get("status") != "STRUCTURAL_PASS_PROVENANCE_UNVERIFIED":
        raise ChainError("bundle preflight failed: " + "; ".join(bundle_report.get("errors", [])))

    host_manifest = json.loads(_regular_bytes(host / "capture_manifest.json"))
    bundle_manifest = json.loads(_regular_bytes(bundle / "manifest.json"))
    raw_host = _regular_bytes(host / "raw_serial.log")
    raw_bundle = _regular_bytes(bundle / "raw_serial.log")
    if raw_host != raw_bundle:
        raise ChainError("host raw bytes differ from derived bundle raw bytes")
    digest = hashlib.sha256(raw_host).hexdigest()
    if (host_manifest.get("raw_sha256") != digest or
            bundle_manifest.get("raw_serial_sha256") != digest or
            host_report.get("raw_sha256") != digest):
        raise ChainError("host/bundle raw SHA-256 chain mismatch")

    elapsed = host_manifest.get("host_monotonic_elapsed_seconds")
    first = host_manifest.get("first_byte_host_offset_seconds")
    last = host_manifest.get("last_byte_host_offset_seconds")
    if (any(type(x) not in (int, float) for x in (elapsed, first, last)) or
            elapsed < MIN_SPAN_SECONDS or last - first < MIN_SPAN_SECONDS):
        raise ChainError("insufficient host elapsed/first-to-last-byte exposure")
    device_span = bundle_report.get("metrics", {}).get("duration_ms")
    if type(device_span) is not int or device_span < MIN_DEVICE_SPAN_MS:
        raise ChainError("insufficient device-monotonic telemetry span")

    return {
        "status": "CHAIN_PASS_PROVENANCE_UNVERIFIED",
        "raw_sha256": digest,
        "host_elapsed_seconds": elapsed,
        "host_byte_exposure_seconds": round(last - first, 6),
        "device_monotonic_span_ms": device_span,
        "extracted_rows": bundle_manifest.get("extracted_rows"),
        "physical_origin_verified": False,
        "flashed_firmware_attested": False,
        "sensor_accuracy_verified": False,
        "limitation": "All files and time sources remain operator controlled; matched hashes do not authenticate physical sensor origin or prevent coordinated forgery.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("host_dir", type=Path)
    p.add_argument("bundle_dir", type=Path)
    a = p.parse_args()
    try:
        result = verify_chain(a.host_dir, a.bundle_dir)
    except (ChainError, OSError, ValueError) as exc:
        p.exit(2, "CHAIN_REJECT_INVALID: " + str(exc) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
