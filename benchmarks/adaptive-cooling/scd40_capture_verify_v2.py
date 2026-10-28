#!/usr/bin/env python3
"""Independent structural verifier for an SCD40 JSONL logger receipt.

Does not authenticate sensor hardware, UTC synchronization, calibration, or cooling.
Require an independently recorded, preexisting SHA-256 to assert byte identity.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

VERSION = "scd40-capture-structural-verifier-v2"
LOGGER_VERSION = "scd40-physical-dry-run-logger-v1"


class CaptureError(ValueError):
    pass


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CaptureError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _number(value, name, *, minimum=None):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise CaptureError(f"{name} must be a finite number")
    if minimum is not None and value < minimum:
        raise CaptureError(f"{name} below minimum")
    return float(value)


def _utc(value):
    if not isinstance(value, str):
        raise CaptureError("missing UTC timestamp")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise CaptureError("invalid UTC timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise CaptureError("UTC timestamp must include zero offset")


def verify(path, *, expected_sha256=None):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is None:
        raise CaptureError("preexisting expected SHA-256 required for byte-identity gate")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise CaptureError("expected SHA-256 must be 64 lowercase hex characters")
    if digest != expected_sha256:
        raise CaptureError("raw capture SHA-256 mismatch")
    if not raw or not raw.endswith(b'\n'):
        raise CaptureError("empty or truncated JSONL")
    try:
        rows = [json.loads(line, object_pairs_hook=_unique_pairs,
                           parse_constant=lambda x: (_ for _ in ()).throw(CaptureError("nonfinite JSON")))
                for line in raw.decode('utf-8').splitlines()]
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CaptureError("invalid UTF-8 JSONL") from exc
    if len(rows) < 2 or not all(isinstance(x, dict) for x in rows):
        raise CaptureError("invalid record sequence")
    begin, complete = rows[0], rows[-1]
    if begin.get('event') != 'begin' or complete.get('event') != 'complete':
        raise CaptureError("missing begin or terminal complete; partial/failed capture")
    if begin.get('schema_version') != LOGGER_VERSION:
        raise CaptureError("unexpected logger schema")
    if begin.get('declared_origin') != 'physical_device_logger':
        raise CaptureError("unexpected origin declaration")
    if any(begin.get(k) is not False for k in ('physical_origin_authenticated', 'calibration_verified', 'cooling_performance_claim_permitted')):
        raise CaptureError("unsupported physical/calibration/performance claim")
    if any(complete.get(k) is not False for k in ('physical_origin_authenticated', 'cooling_performance_claim_permitted')):
        raise CaptureError("unsupported completion claim")
    for key in ('run_id', 'placement'):
        if not isinstance(begin.get(key), str) or not begin[key].strip():
            raise CaptureError(f"missing {key}")
    _utc(begin.get('utc'))
    _utc(complete.get('utc'))
    requested = _number(begin.get('requested_duration_s'), 'requested duration', minimum=0)
    poll = _number(begin.get('poll_s'), 'poll interval', minimum=0)
    if requested == 0 or poll == 0 or poll > 5:
        raise CaptureError("invalid run parameters")
    elapsed = _number(complete.get('elapsed_monotonic_s'), 'elapsed', minimum=0)
    samples = rows[1:-1]
    prev = None
    for i, row in enumerate(samples):
        if row.get('event') != 'sample' or type(row.get('index')) is not int or row['index'] != i:
            raise CaptureError("missing/extra/out-of-order sample or failure record")
        _utc(row.get('utc'))
        t = _number(row.get('elapsed_monotonic_s'), 'sample elapsed', minimum=0)
        if prev is not None and t <= prev:
            raise CaptureError("non-increasing sample monotonic time")
        if t > elapsed:
            raise CaptureError("sample time exceeds completed duration")
        prev = t
        temp = _number(row.get('scd4x_temperature_c'), 'temperature')
        rh = _number(row.get('scd4x_relative_humidity_pct'), 'humidity')
        co2 = _number(row.get('scd4x_co2_ppm'), 'CO2')
        if not (-10 <= temp <= 60 and 0 <= rh <= 100 and 0 <= co2 <= 40000):
            raise CaptureError("sensor reading outside logger acceptance bounds")
    times = [float(x['elapsed_monotonic_s']) for x in samples]
    gap = max((b-a for a,b in zip(times, times[1:])), default=None)
    count = len(samples)
    quality = bool(elapsed >= 600 and count >= 2 and gap <= 60
                   and times[0] <= 60 and elapsed - times[-1] <= 60)
    if type(complete.get('samples')) is not int or complete['samples'] != count:
        raise CaptureError("completion sample count mismatch")
    declared_gap = complete.get('max_sample_gap_s')
    if gap is None:
        if declared_gap is not None:
            raise CaptureError("gap must be null for fewer than two samples")
    elif abs(_number(declared_gap, 'max gap', minimum=0)-gap) > 1e-7:
        raise CaptureError("maximum gap mismatch")
    if complete.get('minimum_600_s_observed') is not (elapsed >= 600):
        raise CaptureError("duration flag mismatch")
    if complete.get('capture_quality_gate_passed') is not quality:
        raise CaptureError("quality gate declaration disagrees with raw samples")
    return {'verifier_version': VERSION, 'logger_version': LOGGER_VERSION,
            'raw_sha256': digest, 'byte_identity_matches_supplied_hash': True,
            'record_structure_valid': True, 'samples': count,
            'elapsed_monotonic_s': elapsed, 'max_sample_gap_s': gap,
            'recomputed_capture_quality_gate_passed': quality,
            'physical_origin_authenticated': False, 'calibration_verified': False,
            'cooling_performance_claim_permitted': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('capture_jsonl')
    p.add_argument('--expected-sha256', required=True,
                   help='SHA-256 pinned separately before independent verification')
    args = p.parse_args()
    print(json.dumps(verify(args.capture_jsonl, expected_sha256=args.expected_sha256),
                     sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
