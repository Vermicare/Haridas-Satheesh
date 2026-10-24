"""Offline ESP32 BH1750/SCD40 capture preflight; NEVER authenticates physical origin."""
import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SCHEMA = "iot-capture-preflight-v1"
FIELDS = ["boot_id", "sensor", "seq", "elapsed_ms", "value", "unit", "ready"]
UNITS = {"BH1750": "lux", "SCD40": "ppm"}
MODES = {"BH1750": "continuous_high_res", "SCD40": "periodic_5s"}
MAX_BYTES = 5_000_000
MAX_BOUNDARY_GAP_MS = 15000  # permitted sensor startup/shutdown skew, not proof of continuity


def check(manifest_path, csv_path):
    """Return machine-readable diagnostics, never a physical-validation certificate."""
    errors, warnings = [], []
    metrics = {}
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be a JSON object")
        raw = Path(csv_path).read_bytes()
        if not raw or len(raw) > MAX_BYTES:
            raise ValueError("CSV must be nonempty and <= 5 MB")
        decoded = raw.decode("utf-8-sig")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "REJECT_INVALID", "errors": ["unreadable input: " + str(exc)], "warnings": [], "metrics": {}}

    digest = hashlib.sha256(raw).hexdigest()
    metrics["csv_sha256"] = digest
    if manifest.get("schema_version") != SCHEMA:
        errors.append("schema_version mismatch")
    if manifest.get("csv_sha256") != digest:
        errors.append("CSV SHA-256 mismatch")
    origin = manifest.get("capture_origin")
    if origin not in ("physical", "synthetic"):
        errors.append("capture_origin must be physical or synthetic")
    if not isinstance(manifest.get("device_id"), str) or not manifest["device_id"].strip() or manifest["device_id"] == "TBD":
        errors.append("device_id missing")
    fw = manifest.get("firmware_sha256")
    if not isinstance(fw, str) or len(fw) != 64 or any(c not in "0123456789abcdef" for c in fw):
        errors.append("firmware_sha256 must be 64 lowercase hex characters")
    boot = manifest.get("boot_id")
    if not isinstance(boot, str) or not boot.strip() or boot == "TBD":
        errors.append("boot_id missing")
    if manifest.get("timestamp_source") != "device_monotonic_ms":
        errors.append("timestamp_source must be device_monotonic_ms")
    if manifest.get("sensor_modes") != MODES:
        errors.append("sensor_modes mismatch; SCD40 periodic_5s required")
    try:
        start = datetime.fromisoformat(manifest["recorded_start_utc"].replace("Z", "+00:00"))
        if start.tzinfo is None or start.utcoffset().total_seconds() != 0:
            raise ValueError("not UTC")
    except (KeyError, AttributeError, ValueError, TypeError):
        errors.append("recorded_start_utc must be timezone-aware UTC")

    reader = csv.DictReader(io.StringIO(decoded, newline=""))
    if reader.fieldnames != FIELDS:
        errors.append("CSV header mismatch")
        return {"status": "REJECT_INVALID", "errors": sorted(set(errors)), "warnings": warnings, "metrics": metrics}
    count = defaultdict(int)
    last_seq, last_time, first_time, gaps = {}, {}, {}, defaultdict(list)
    first, last, previous_global = None, None, None
    for index, row in enumerate(reader, start=2):
        if index > 10002:
            errors.append("more than 10000 samples")
            break
        if None in row:
            errors.append(f"line {index}: extra CSV fields")
            continue
        if any(value is None for value in row.values()):
            errors.append(f"line {index}: missing CSV fields")
            continue
        sensor = row["sensor"]
        if sensor not in UNITS:
            errors.append(f"line {index}: unknown sensor")
            continue
        try:
            seq = int(row["seq"])
            elapsed = int(row["elapsed_ms"])
            value = float(row["value"])
        except (TypeError, ValueError):
            errors.append(f"line {index}: nonnumeric field")
            continue
        if seq < 0 or elapsed < 0 or not math.isfinite(value):
            errors.append(f"line {index}: negative counter/time or nonfinite value")
        if row["boot_id"] != boot:
            errors.append(f"line {index}: boot mismatch")
        if row["unit"] != UNITS[sensor]:
            errors.append(f"line {index}: wrong unit")
        if row["ready"] != "1":
            errors.append(f"line {index}: sensor data not ready")
        if value < 0 or value > (40000 if sensor == "SCD40" else 200000):
            errors.append(f"line {index}: value outside plausibility bound")
        if sensor == "SCD40" and not (400 <= value <= 2000):
            warnings.append("SCD40 value outside specified 400–2000 ppm accuracy range")
        if previous_global is not None and elapsed < previous_global:
            errors.append(f"line {index}: global elapsed time decreased")
        previous_global = elapsed
        if sensor in last_seq:
            if seq != last_seq[sensor] + 1:
                errors.append(f"line {index}: nonconsecutive {sensor} sequence")
            delta = elapsed - last_time[sensor]
            if delta <= 0:
                errors.append(f"line {index}: repeated or reversed {sensor} timestamp")
            elif sensor == "SCD40" and delta < 4000:
                errors.append(f"line {index}: SCD40 interval below 4 seconds")
            gaps[sensor].append(delta)
        first_time.setdefault(sensor, elapsed)
        last_seq[sensor], last_time[sensor] = seq, elapsed
        count[sensor] += 1
        first = elapsed if first is None else min(first, elapsed)
        last = elapsed if last is None else max(last, elapsed)
    duration = (last - first) if first is not None else 0
    metrics.update({"duration_ms": duration, "sample_counts": dict(count),
                    "max_gap_ms": {s: max(gaps[s], default=0) for s in UNITS},
                    "sensor_span_ms": {s: last_time[s] - first_time[s] for s in UNITS if s in first_time},
                    "boundary_gap_ms": {s: {"leading": first_time[s] - first,
                                             "trailing": last - last_time[s]}
                                        for s in UNITS if s in first_time}})
    if duration < 600000:
        errors.append("less than ten minutes of device-monotonic span")
    for sensor in UNITS:
        if count[sensor] < 100:
            errors.append(f"{sensor}: fewer than 100 samples")
        if max(gaps[sensor], default=0) > 15000:
            errors.append(f"{sensor}: gap exceeds 15 seconds")
        if sensor in first_time:
            if first_time[sensor] - first > MAX_BOUNDARY_GAP_MS:
                errors.append(f"{sensor}: leading coverage gap exceeds 15 seconds")
            if last - last_time[sensor] > MAX_BOUNDARY_GAP_MS:
                errors.append(f"{sensor}: trailing coverage gap exceeds 15 seconds")
    for sensor in UNITS:
        details = manifest.get("instruments", {}).get(sensor, {}) if isinstance(manifest.get("instruments"), dict) else {}
        if not isinstance(details, dict) or not details.get("model") or not details.get("address"):
            warnings.append(f"{sensor}: instrument model/address not documented")
        if not isinstance(details, dict) or details.get("check_status") in (None, "", "TBD"):
            warnings.append(f"{sensor}: independent check status TBD")
    if origin == "synthetic":
        errors.append("explicit synthetic origin: cannot be physical capture evidence")
    status = "REJECT_INVALID" if errors else "STRUCTURAL_PASS_PROVENANCE_UNVERIFIED"
    return {"status": status, "errors": sorted(set(errors)), "warnings": sorted(set(warnings)), "metrics": metrics,
            "limitation": "CSV hashes, monotonic counters and declarations do not authenticate a sensor, firmware, operator or physical measurement."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    result = check(args.manifest, args.csv)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"].startswith("STRUCTURAL_PASS") else 2)


if __name__ == "__main__":
    main()
