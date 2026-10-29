#!/usr/bin/env python3
"""Supplemental sample-span review for pinned SCD4x JSONL; fictional tests only.

Not a device-origin, elapsed-wall-clock, calibration or cooling-performance gate.
Run v2 and v3 independently; no physical provenance is inferred.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from scd40_capture_verify_v2 import verify, CaptureError, _unique_pairs

VERSION = 'scd40-sample-span-review-v4'


def audit(path, *, expected_sha256):
    base = verify(path, expected_sha256=expected_sha256)
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != base['raw_sha256']:
        raise CaptureError('capture changed after v2 verification')
    rows = [json.loads(line, object_pairs_hook=_unique_pairs) for line in raw.decode('utf-8').splitlines()]
    begin, end = rows[0], rows[-1]
    samples = rows[1:-1]
    requested = float(begin['requested_duration_s'])
    poll = float(begin['poll_s'])
    elapsed = float(end['elapsed_monotonic_s'])
    span = float(samples[-1]['elapsed_monotonic_s'] - samples[0]['elapsed_monotonic_s']) if len(samples) >= 2 else 0.0
    # Provisional conservative engineering review tolerance, not SCD40 specification.
    tolerance = max(10.0, 2.0 * poll)
    required_span = max(0.0, max(600.0, requested) - tolerance)
    problems = []
    if not base['recomputed_capture_quality_gate_passed']:
        problems.append('V2_CAPTURE_QUALITY_NOT_MET')
    if elapsed < max(600.0, requested):
        problems.append('ELAPSED_SHORTER_THAN_REQUESTED_OR_600S')
    if span < required_span:
        problems.append('SAMPLE_SPAN_SHORTER_THAN_PROVISIONAL_REVIEW_MINIMUM')
    return {'schema_version': VERSION,
            'status': 'REVIEW_REQUIRED' if problems else 'SAMPLE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED',
            'problems': problems,
            'raw_sha256': base['raw_sha256'],
            'samples': len(samples), 'elapsed_monotonic_s': elapsed,
            'first_sample_monotonic_s': float(samples[0]['elapsed_monotonic_s']) if samples else None,
            'last_sample_monotonic_s': float(samples[-1]['elapsed_monotonic_s']) if samples else None,
            'sample_span_s': span, 'minimum_review_sample_span_s': required_span,
            'review_tolerance_s': tolerance,
            'v2_recomputed_capture_quality_gate_passed': base['recomputed_capture_quality_gate_passed'],
            'physical_origin_authenticated': False, 'wall_clock_attested': False,
            'calibration_verified': False, 'cooling_performance_claim_permitted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture_jsonl')
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args()
    result = audit(args.capture_jsonl, expected_sha256=args.expected_sha256)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(2 if result['status'] == 'REVIEW_REQUIRED' else 0)

if __name__ == '__main__': main()
