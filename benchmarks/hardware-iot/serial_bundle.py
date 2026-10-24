"""Package operator-supplied ESP32 serial bytes; NEVER certify physical provenance.

Input protocol: each telemetry line starts with 'IOTCSV,' followed by the seven
fields defined in capture_preflight.py. Other serial lines remain in raw.log.
This tool does not read a serial port, authenticate firmware or measure sensors.
"""
import argparse
import csv
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path

from capture_preflight import FIELDS, MODES, SCHEMA, check

MAX_RAW_BYTES = 10_000_000
MARKER = "IOTCSV,"


class BundleError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extract(raw):
    """Deterministically recover CSV records; preserve original serial separately."""
    if not raw or len(raw) > MAX_RAW_BYTES:
        raise BundleError("raw serial must be nonempty and <=10 MB")
    try:
        lines = raw.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise BundleError("raw serial must be UTF-8") from exc
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(FIELDS)
    boot = None
    count = 0
    for n, line in enumerate(lines, 1):
        if MARKER not in line:
            if "IOTCSV" in line:
                raise BundleError(f"line {n}: malformed telemetry marker")
            continue
        if not line.startswith(MARKER):
            raise BundleError(f"line {n}: telemetry must start with IOTCSV, (no monitor prefixes)")
        try:
            row = next(csv.reader([line[len(MARKER):]], strict=True))
        except csv.Error as exc:
            raise BundleError(f"line {n}: invalid CSV") from exc
        if len(row) != len(FIELDS) or any("\n" in v or "\r" in v for v in row):
            raise BundleError(f"line {n}: expected exactly seven fields")
        if boot is None:
            boot = row[0]
        if not boot or row[0] != boot:
            raise BundleError(f"line {n}: empty or mixed boot_id")
        writer.writerow(row)
        count += 1
    if count == 0:
        raise BundleError("no IOTCSV telemetry lines")
    result = output.getvalue().encode("utf-8")
    if len(result) > 5_000_000:
        raise BundleError("extracted CSV exceeds preflight limit")
    return result, boot, count


def utc_stamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError("not UTC")
    except (AttributeError, ValueError, TypeError) as exc:
        raise BundleError("recorded_start_utc must be explicit UTC, not local time") from exc
    return value


def verify(directory):
    directory = Path(directory)
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        raw = (directory / "raw_serial.log").read_bytes()
        csv_bytes = (directory / "samples.csv").read_bytes()
        expected, boot, count = extract(raw)
        if expected != csv_bytes:
            raise BundleError("CSV differs from raw serial extraction")
        if manifest.get("raw_serial_sha256") != digest(raw):
            raise BundleError("raw serial SHA-256 mismatch")
        if manifest.get("boot_id") != boot:
            raise BundleError("manifest boot_id differs from raw serial")
        if manifest.get("extracted_rows") != count:
            raise BundleError("manifest extracted_rows mismatch")
        result = check(directory / "manifest.json", directory / "samples.csv")
        result["raw_serial_integrity"] = "MATCHED_UNAUTHENTICATED"
        return result
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "REJECT_INVALID", "errors": [str(exc)],
                "raw_serial_integrity": "FAILED", "metrics": {}}


def build(raw_path, firmware_path, output_dir, *, device_id, recorded_start_utc,
          capture_origin="synthetic"):
    """Preserve bytes and hash firmware; output is operator-declared, not attested."""
    if capture_origin not in ("physical", "synthetic"):
        raise BundleError("capture_origin must be physical or synthetic")
    if not device_id or device_id == "TBD":
        raise BundleError("device_id must be a nonempty operator declaration")
    utc_stamp(recorded_start_utc)
    raw = Path(raw_path).read_bytes()
    firmware = Path(firmware_path).read_bytes()
    if not firmware:
        raise BundleError("firmware binary must be nonempty")
    csv_bytes, boot, count = extract(raw)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=False)  # refuse to overwrite any prior session
    (out / "raw_serial.log").write_bytes(raw)
    (out / "samples.csv").write_bytes(csv_bytes)
    manifest = {
        "schema_version": SCHEMA, "capture_origin": capture_origin,
        "device_id": device_id, "boot_id": boot,
        "recorded_start_utc": recorded_start_utc,
        "timestamp_source": "device_monotonic_ms", "sensor_modes": MODES,
        "firmware_sha256": digest(firmware), "csv_sha256": digest(csv_bytes),
        "raw_serial_sha256": digest(raw), "extracted_rows": count,
        "instruments": {
            "BH1750": {"model": "TBD", "address": "0x23", "check_status": "TBD"},
            "SCD40": {"model": "TBD", "address": "0x62", "check_status": "TBD"}},
        "origin_limit": "operator declaration only; firmware hash does not prove flashed firmware",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = verify(out)
    (out / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build")
    make.add_argument("--raw", type=Path, required=True)
    make.add_argument("--firmware", type=Path, required=True)
    make.add_argument("--out", type=Path, required=True)
    make.add_argument("--device-id", required=True)
    make.add_argument("--recorded-start-utc", required=True)
    make.add_argument("--capture-origin", choices=["physical", "synthetic"], default="synthetic")
    inspect = sub.add_parser("verify")
    inspect.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        report = (build(args.raw, args.firmware, args.out, device_id=args.device_id,
                        recorded_start_utc=args.recorded_start_utc,
                        capture_origin=args.capture_origin) if args.command == "build"
                  else verify(args.directory))
    except (OSError, BundleError) as exc:
        parser.exit(2, f"REJECT_INVALID: {exc}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"].startswith("STRUCTURAL_PASS") else 2)


if __name__ == "__main__":
    main()
