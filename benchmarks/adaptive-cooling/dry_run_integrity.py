#!/usr/bin/env python3
"""Offline integrity preflight for cooling CSVs. NEVER authenticates physical data."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re

HEADER = ('run_id,timestamp,condition,ambient_temp_c,ambient_rh_pct,'
          'target_temp_c,target_rh_pct,air_velocity_m_s,surface_temp_c,'
          'power_w,energy_wh,condensation_flag,notes').split(',')
NUMERIC = ('ambient_temp_c', 'ambient_rh_pct', 'target_temp_c', 'target_rh_pct',
           'air_velocity_m_s', 'surface_temp_c', 'power_w', 'energy_wh')
CONDITIONS = {'ambient', 'fan_only', 'prototype'}


def audit(path: str | Path, *, min_duration_s: float = 600.0,
          max_gap_s: float = 60.0, energy_abs_tol_wh: float = 0.5,
          energy_rel_tol: float = 0.30,
          expected_sha256: str | None = None) -> dict:
    """Fail-closed structural and coarse energy-consistency check.

    No evidence of sensor authenticity, calibration, physical origin, or efficiency.
    Trapezoidal power integration assumes samples adequately represent intervals.
    """
    problems = []
    records = []
    raw_sha256 = None
    raw_byte_count = None
    try:
        # Parse precisely the bytes whose digest is reported; do not hash one
        # filesystem read and then parse a second potentially changed read.
        snapshot = Path(path).read_bytes()
        raw_sha256 = hashlib.sha256(snapshot).hexdigest()
        raw_byte_count = len(snapshot)
        with io.StringIO(snapshot.decode('utf-8-sig'), newline='') as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != HEADER:
                problems.append('HEADER_MISMATCH')
            else:
                records = list(reader)
    except (OSError, UnicodeError, csv.Error):
        problems.append('CSV_UNREADABLE')
    if expected_sha256 is not None:
        if not isinstance(expected_sha256, str) or not re.fullmatch(
                r'[0-9a-fA-F]{64}', expected_sha256):
            problems.append('INVALID_EXPECTED_SHA256')
        elif raw_sha256 is not None and raw_sha256 != expected_sha256.lower():
            problems.append('RAW_SHA256_MISMATCH')
    if not records:
        problems.append('NO_ROWS')
    parsed = []
    for index, row in enumerate(records, start=2):
        if None in row or any(value is None for value in row.values()):
            problems.append('MALFORMED_ROW')
            continue
        if not row['run_id'].strip():
            problems.append('MISSING_RUN_ID')
        if row['condition'] not in CONDITIONS:
            problems.append('INVALID_CONDITION')
        if row['condensation_flag'].strip().lower() not in {'yes', 'no', 'unknown'}:
            problems.append('INVALID_CONDENSATION_FLAG')
        try:
            timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError('timezone required')
        except (ValueError, OverflowError):
            problems.append('INVALID_TIMESTAMP')
            continue
        try:
            values = {name: float(row[name]) for name in NUMERIC}
            if any(not math.isfinite(value) for value in values.values()):
                raise ValueError('nonfinite')
        except (ValueError, TypeError):
            problems.append('INVALID_NUMERIC')
            continue
        if not (0 <= values['ambient_rh_pct'] <= 100 and
                0 <= values['target_rh_pct'] <= 100):
            problems.append('RH_OUT_OF_RANGE')
        if any(values[name] < 0 for name in ('air_velocity_m_s', 'power_w', 'energy_wh')):
            problems.append('NEGATIVE_PHYSICAL_QUANTITY')
        parsed.append((timestamp, row['run_id'], row['condition'], values))
    duration_s = None
    integrated_wh = None
    counter_wh = None
    if len(parsed) >= 2:
        if len({r[1] for r in parsed}) != 1:
            problems.append('MIXED_RUN_IDS')
        if len({r[2] for r in parsed}) != 1:
            problems.append('MIXED_CONDITIONS')
        elapsed = [(b[0] - a[0]).total_seconds() for a, b in zip(parsed, parsed[1:])]
        if any(dt <= 0 for dt in elapsed):
            problems.append('NONMONOTONIC_TIMESTAMP')
        if any(dt > max_gap_s for dt in elapsed):
            problems.append('SAMPLING_GAP')
        duration_s = (parsed[-1][0] - parsed[0][0]).total_seconds()
        if duration_s < min_duration_s:
            problems.append('INSUFFICIENT_DURATION')
        increments = [b[3]['energy_wh'] - a[3]['energy_wh']
                      for a, b in zip(parsed, parsed[1:])]
        if any(increment < -1e-9 for increment in increments):
            problems.append('ENERGY_COUNTER_DECREASE')
        if all(dt > 0 for dt in elapsed):
            # Half-before-add prevents overflow in (a+b)/2 for large but
            # individually finite inputs. Interval conversion precedes power
            # multiplication; derived results still require a finite check.
            integrated_wh = sum(
                (a[3]['power_w'] / 2 + b[3]['power_w'] / 2) * (dt / 3600)
                for (a, b), dt in zip(zip(parsed, parsed[1:]), elapsed))
            counter_wh = parsed[-1][3]['energy_wh'] - parsed[0][3]['energy_wh']
            if not math.isfinite(integrated_wh) or not math.isfinite(counter_wh):
                problems.append('NONFINITE_DERIVED_ENERGY')
                if not math.isfinite(integrated_wh):
                    integrated_wh = None  # JSON-safe; never emit Infinity/NaN
                if not math.isfinite(counter_wh):
                    counter_wh = None
            else:
                tolerance_wh = energy_abs_tol_wh + energy_rel_tol * integrated_wh
                if not math.isfinite(tolerance_wh):
                    problems.append('NONFINITE_ENERGY_TOLERANCE')
                elif abs(counter_wh - integrated_wh) > tolerance_wh:
                    problems.append('POWER_ENERGY_INCONSISTENCY')
    else:
        problems.append('INSUFFICIENT_SAMPLES')
    return {
        'status': 'REJECTED' if problems else 'STRUCTURE_ONLY_PROVENANCE_UNVERIFIED',
        'problems': sorted(set(problems)), 'rows': len(records),
        'raw_sha256': raw_sha256, 'raw_byte_count': raw_byte_count,
        'duration_s': duration_s,
        'power_integral_estimate_wh': integrated_wh,
        'energy_counter_delta_wh': counter_wh,
        'checks': {'min_duration_s': min_duration_s, 'max_gap_s': max_gap_s,
                   'energy_abs_tol_wh': energy_abs_tol_wh,
                   'energy_rel_tol': energy_rel_tol},
        'physical_origin_authenticated': False, 'performance_claim_permitted': False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', required=True, help='Existing raw CSV; never modified')
    parser.add_argument('--expected-sha256', default=None,
                        help='Optional pinned SHA-256 of the exact raw CSV bytes')
    args = parser.parse_args()
    result = audit(args.raw, expected_sha256=args.expected_sha256)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(2 if result['status'] == 'REJECTED' else 0)


if __name__ == '__main__':
    main()
