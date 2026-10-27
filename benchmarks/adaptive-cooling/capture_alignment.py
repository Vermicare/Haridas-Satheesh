#!/usr/bin/env python3
"""Cross-check cooling capture declarations against the hashed CSV and plan.

Software-only consistency preflight. It does NOT authenticate physical origin,
logger-to-CSV conversion, calibration, cooling performance, or safety.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path

from capture_chain import audit as chain_audit, _no_duplicate_keys, _no_nonfinite
from dry_run_integrity import audit as csv_audit, HEADER

VERSION = 'cooling-capture-alignment-v1'


def _time(value: str) -> datetime:
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError('timezone required')
    return stamp


def audit(bundle_dir: str | Path, *, expected_manifest_sha256: str | None = None) -> dict:
    """Fail closed on byte-chain, CSV integrity, or cross-document contradictions."""
    chain = chain_audit(bundle_dir, expected_manifest_sha256=expected_manifest_sha256)
    problems = list(chain['problems'])
    csv_result = None
    summary = {'run_id': None, 'condition': None, 'rows': None,
               'first_timestamp': None, 'last_timestamp': None}
    if chain['status'] != 'CHAIN_CHECKED_ORIGIN_UNVERIFIED':
        problems.append('CAPTURE_CHAIN_REJECTED')
    else:
        root = Path(bundle_dir).resolve(strict=True)
        try:
            # The chain has already rejected symlinks and traversal. Rehash every
            # subsequently parsed snapshot to detect edits between reads.
            manifest_bytes = (root / 'capture_manifest.json').read_bytes()
            if hashlib.sha256(manifest_bytes).hexdigest() != chain['manifest_sha256']:
                raise ValueError('manifest changed after chain audit')
            manifest = json.loads(manifest_bytes.decode('utf-8-sig'),
                                  object_pairs_hook=_no_duplicate_keys,
                                  parse_constant=_no_nonfinite)
            def snapshot(role):
                record = chain['artifacts'][role]
                content = (root / record['path']).read_bytes()
                if hashlib.sha256(content).hexdigest() != record['sha256']:
                    raise ValueError(role + ' changed after chain audit')
                return content
            csv_bytes = snapshot('measurement_csv')
            plan_bytes = snapshot('run_plan')
            plan = json.loads(plan_bytes.decode('utf-8-sig'),
                              object_pairs_hook=_no_duplicate_keys,
                              parse_constant=_no_nonfinite)
            if not isinstance(plan, dict):
                raise ValueError('run plan must be object')
            with io.StringIO(csv_bytes.decode('utf-8-sig'), newline='') as handle:
                reader = csv.DictReader(handle, strict=True)
                if reader.fieldnames != HEADER:
                    raise ValueError('CSV header mismatch')
                rows = list(reader)
            if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
                raise ValueError('CSV rows malformed')
            csv_path = root / chain['artifacts']['measurement_csv']['path']
            csv_result = csv_audit(csv_path, expected_sha256=chain['artifacts']['measurement_csv']['sha256'])
            if csv_result['status'] == 'REJECTED':
                problems.append('CSV_INTEGRITY_REJECTED')
            if csv_result['raw_sha256'] != hashlib.sha256(csv_bytes).hexdigest():
                problems.append('CSV_CHANGED_DURING_PREFLIGHT')
            ids = {row['run_id'] for row in rows}
            conditions = {row['condition'] for row in rows}
            summary.update(run_id=next(iter(ids)) if len(ids) == 1 else None,
                           condition=next(iter(conditions)) if len(conditions) == 1 else None,
                           rows=len(rows))
            if len(ids) != 1 or summary['run_id'] != manifest['metadata']['run_id']:
                problems.append('RUN_ID_MANIFEST_MISMATCH')
            if not isinstance(plan.get('run_id'), str) or plan['run_id'] != manifest['metadata']['run_id']:
                problems.append('RUN_ID_PLAN_MISMATCH')
            if not isinstance(plan.get('condition'), str) or len(conditions) != 1 or plan['condition'] != summary['condition']:
                problems.append('CONDITION_PLAN_MISMATCH')
            stamps = [_time(row['timestamp']) for row in rows]
            first, last = min(stamps), max(stamps)
            summary['first_timestamp'], summary['last_timestamp'] = first.isoformat(), last.isoformat()
            declared_first = _time(manifest['metadata']['capture_start'])
            declared_last = _time(manifest['metadata']['capture_end'])
            interval = float(manifest['metadata']['sample_interval_s'])
            # The CSV's generic <=60 s gap limit is insufficient when the
            # frozen manifest declares a faster nominal sample cadence.
            # +/-50% is a provisional REVIEW tolerance, not calibrated jitter.
            # Report a contradiction rather than silently accepting sparse
            # records as evidence of the declared capture resolution.
            observed_gaps = [(b - a).total_seconds()
                             for a, b in zip(stamps, stamps[1:])]
            if any(gap < interval * 0.5 - 1e-6 or
                   gap > interval * 1.5 + 1e-6
                   for gap in observed_gaps):
                problems.append('DECLARED_CADENCE_MISMATCH')
            # Declarations must encompass the observed samples and be within
            # one sample interval at each boundary. Never silently stretch a run.
            slack = interval + 1e-6
            if not (0 <= (first - declared_first).total_seconds() <= slack):
                problems.append('CAPTURE_START_MISMATCH')
            if not (0 <= (declared_last - last).total_seconds() <= slack):
                problems.append('CAPTURE_END_MISMATCH')
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, csv.Error, OverflowError):
            problems.append('ALIGNMENT_UNREADABLE_OR_AMBIGUOUS')
    return {
        'schema_version': VERSION,
        'status': 'REJECTED' if problems else 'DECLARATIONS_ALIGNED_ORIGIN_UNVERIFIED',
        'problems': sorted(set(problems)),
        'capture_manifest_sha256': chain['manifest_sha256'],
        'external_manifest_pin_verified': chain['external_manifest_pin_verified'],
        'csv_sha256': chain['artifacts'].get('measurement_csv', {}).get('sha256'),
        'summary': summary,
        'csv_integrity_status': csv_result['status'] if csv_result else 'NOT_RUN',
        'physical_origin_authenticated': False,
        'logger_to_csv_conversion_verified': False,
        'instrument_calibration_verified': False,
        'performance_claim_permitted': False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--expected-manifest-sha256')
    args = parser.parse_args()
    report = audit(args.bundle, expected_manifest_sha256=args.expected_manifest_sha256)
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    raise SystemExit(2 if report['status'] == 'REJECTED' else 0)


if __name__ == '__main__':
    main()
