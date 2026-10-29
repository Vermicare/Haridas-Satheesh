#!/usr/bin/env python3
"""Supplemental, fictional-testable clock-consistency diagnostic for SCD40 JSONL.

Run the existing scd40_capture_verify_v2.py independently first. This checks
only whether declared UTC time progresses consistently with declared monotonic
elapsed time; it cannot authenticate a clock, a sensor, or real elapsed time.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

VERSION = 'scd40-clock-concordance-v3'

class ClockAuditError(ValueError):
    pass

def _unique_pairs(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ClockAuditError('duplicate JSON key')
        obj[k] = v
    return obj

def _utc(value):
    if not isinstance(value, str):
        raise ClockAuditError('missing UTC timestamp')
    try:
        d = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ClockAuditError('invalid UTC timestamp') from exc
    if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds() != 0:
        raise ClockAuditError('expected zero-offset UTC timestamp')
    return d.astimezone(timezone.utc)

def _elapsed(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ClockAuditError('invalid monotonic elapsed value')
    return float(value)

def audit(path, expected_sha256, *, tolerance_s=10.0):
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise ClockAuditError('expected SHA-256 must be 64 lowercase hex characters')
    if not math.isfinite(tolerance_s) or tolerance_s <= 0:
        raise ClockAuditError('tolerance must be positive and finite')
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ClockAuditError('SHA-256 mismatch')
    if not raw.endswith(b'\n'):
        raise ClockAuditError('truncated JSONL')
    try:
        rows = [json.loads(line, object_pairs_hook=_unique_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ClockAuditError('nonfinite JSON')))
                for line in raw.decode('utf-8').splitlines()]
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ClockAuditError('invalid UTF-8 JSONL') from exc
    if len(rows) < 2 or any(not isinstance(r, dict) for r in rows):
        raise ClockAuditError('invalid record sequence')
    if rows[0].get('event') != 'begin' or rows[-1].get('event') != 'complete' or any(r.get('event') != 'sample' for r in rows[1:-1]):
        raise ClockAuditError('unexpected record sequence; run v2 structural verifier first')
    start = _utc(rows[0].get('utc'))
    last_utc = start
    last_elapsed = -1.0
    max_skew = 0.0
    regressions = 0
    sample_count = 0
    for row in rows[1:]:
        utc = _utc(row.get('utc'))
        elapsed = _elapsed(row.get('elapsed_monotonic_s'))
        if elapsed <= last_elapsed:
            raise ClockAuditError('non-increasing declared monotonic time')
        if utc < last_utc:
            regressions += 1
        max_skew = max(max_skew, abs((utc-start).total_seconds() - elapsed))
        last_utc, last_elapsed = utc, elapsed
        if row['event'] == 'sample':
            sample_count += 1
    return {'diagnostic_version': VERSION, 'raw_sha256': digest,
            'sample_count': sample_count, 'tolerance_s': tolerance_s,
            'max_utc_monotonic_skew_s': round(max_skew, 6),
            'utc_regressions': regressions,
            'clock_review_required': regressions > 0 or max_skew > tolerance_s,
            'structural_v2_passed': 'NOT_CHECKED',
            'physical_origin_authenticated': False,
            'calibration_verified': False, 'cooling_performance_claim_permitted': False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('capture_jsonl')
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--tolerance-s', type=float, default=10.0)
    args=p.parse_args()
    print(json.dumps(audit(args.capture_jsonl, args.expected_sha256, tolerance_s=args.tolerance_s), sort_keys=True))

if __name__ == '__main__':
    main()
