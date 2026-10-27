#!/usr/bin/env python3
"""Verify a declared cooling capture bundle's byte integrity, NOT physical origin.

No sensor authentication, logger-to-CSV semantic verification, calibration,
energy/thermal performance, or safety certification is provided.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re

VERSION = 'cooling-capture-chain-v1'
ROLES = ('original_logger', 'measurement_csv', 'instrument_manifest', 'run_plan')
REQUIRED_METADATA = (
    'run_id', 'capture_start', 'capture_end', 'logger_version',
    'firmware_version', 'clock_sync_method', 'sample_interval_s',
    'sensor_geometry', 'energy_boundary', 'heat_rejection_path',
    'thermal_storage_preconditioning', 'recharge_energy_accounting',
    'conversion_command', 'operator_declaration',
)
HEX_SHA256 = re.compile(r'[0-9a-fA-F]{64}\Z')


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _no_nonfinite(value):
    raise ValueError('nonfinite JSON number: ' + value)


def _parse_utc(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a string')
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError('timezone required')
    return stamp


def _path_inside(root: Path, relative: str):
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise ValueError('invalid artifact path')
    p = PurePosixPath(relative)
    if p.is_absolute() or p.as_posix() != relative or any(part in ('', '.', '..') for part in relative.split('/')):
        raise ValueError('artifact path must be normalized and relative')
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlinked artifact path')
    resolved = current.resolve(strict=True)
    if root != resolved and root not in resolved.parents:
        raise ValueError('artifact escapes bundle')
    if not resolved.is_file():
        raise ValueError('artifact is not a file')
    return resolved


def _digest(path: Path):
    h = hashlib.sha256()
    count = 0
    with path.open('rb') as handle:
        while chunk := handle.read(1024 * 1024):
            h.update(chunk)
            count += len(chunk)
    return h.hexdigest(), count


def audit(bundle_dir: str | Path, manifest_name: str = 'capture_manifest.json',
          *, expected_manifest_sha256: str | None = None) -> dict:
    """Check an explicitly declared bundle; never return an authenticity PASS."""
    problems = []
    artifacts_report = {}
    manifest_digest = None
    origin = 'TBD'
    external_pin_verified = False
    try:
        root = Path(bundle_dir).resolve(strict=True)
        if not root.is_dir():
            raise ValueError('bundle root is not a directory')
        manifest_path = _path_inside(root, manifest_name)
        raw_manifest = manifest_path.read_bytes()  # Parse exactly the hashed snapshot.
        manifest_digest = hashlib.sha256(raw_manifest).hexdigest()
        if expected_manifest_sha256 is not None:
            if not isinstance(expected_manifest_sha256, str) or not HEX_SHA256.fullmatch(expected_manifest_sha256):
                problems.append('INVALID_MANIFEST_PIN')
            elif expected_manifest_sha256.lower() != manifest_digest:
                problems.append('MANIFEST_PIN_MISMATCH')
            else:
                external_pin_verified = True
        manifest = json.loads(raw_manifest.decode('utf-8-sig'),
                              object_pairs_hook=_no_duplicate_keys,
                              parse_constant=_no_nonfinite)
        if not isinstance(manifest, dict) or manifest.get('schema_version') != VERSION:
            problems.append('INVALID_SCHEMA_VERSION')
            manifest = manifest if isinstance(manifest, dict) else {}
        origin = manifest.get('origin', 'TBD')
        if origin not in ('fictional_test_only', 'declared_physical_dry_run'):
            problems.append('INVALID_ORIGIN_DECLARATION')
        metadata = manifest.get('metadata')
        if not isinstance(metadata, dict):
            problems.append('INVALID_METADATA')
            metadata = {}
        for key in REQUIRED_METADATA:
            value = metadata.get(key)
            if value is None or isinstance(value, bool) or (isinstance(value, str) and value.strip().upper() in ('', 'TBD')):
                problems.append('MISSING_METADATA_' + key.upper())
            elif key != 'sample_interval_s' and not isinstance(value, str):
                problems.append('INVALID_METADATA_' + key.upper())
        sample_interval = metadata.get('sample_interval_s')
        if type(sample_interval) not in (float, int) or not math.isfinite(sample_interval) or not 0 < sample_interval <= 60:
            problems.append('INVALID_SAMPLE_INTERVAL')
        try:
            start = _parse_utc(metadata.get('capture_start'))
            end = _parse_utc(metadata.get('capture_end'))
            if (end - start).total_seconds() < 600:
                problems.append('DECLARED_CAPTURE_UNDER_600S')
        except (ValueError, OverflowError, TypeError):
            problems.append('INVALID_CAPTURE_TIME_RANGE')
        artifacts = manifest.get('artifacts')
        if not isinstance(artifacts, dict) or set(artifacts) != set(ROLES):
            problems.append('ARTIFACT_ROLES_MISMATCH')
            artifacts = artifacts if isinstance(artifacts, dict) else {}
        used_paths = set()
        for role in ROLES:
            record = artifacts.get(role)
            if not isinstance(record, dict):
                problems.append('MISSING_ARTIFACT_' + role.upper())
                continue
            relative, expected = record.get('path'), record.get('sha256')
            if not isinstance(expected, str) or not HEX_SHA256.fullmatch(expected):
                problems.append('INVALID_SHA256_' + role.upper())
                continue
            if not isinstance(relative, str) or relative in used_paths:
                problems.append('DUPLICATE_OR_INVALID_ARTIFACT_PATH')
                continue
            used_paths.add(relative)
            try:
                path = _path_inside(root, relative)
                actual, size = _digest(path)
                artifacts_report[role] = {'path': relative, 'sha256': actual, 'bytes': size,
                                          'matches_declared_sha256': actual == expected.lower()}
                if not size:
                    problems.append('EMPTY_ARTIFACT_' + role.upper())
                if actual != expected.lower():
                    problems.append('SHA256_MISMATCH_' + role.upper())
            except (OSError, ValueError):
                problems.append('UNREADABLE_OR_UNSAFE_ARTIFACT_' + role.upper())
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        problems.append('MANIFEST_UNREADABLE_OR_AMBIGUOUS')
    return {
        'status': 'REJECTED' if problems else 'CHAIN_CHECKED_ORIGIN_UNVERIFIED',
        'problems': sorted(set(problems)),
        'schema_version': VERSION,
        'declared_origin': origin,
        'manifest_sha256': manifest_digest,
        'external_manifest_pin_verified': external_pin_verified,
        'artifacts': artifacts_report,
        'physical_origin_authenticated': False,
        'logger_to_csv_conversion_verified': False,
        'instrument_calibration_verified': False,
        'performance_claim_permitted': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--manifest', default='capture_manifest.json')
    parser.add_argument('--expected-manifest-sha256', default=None)
    args = parser.parse_args()
    result = audit(args.bundle, args.manifest,
                   expected_manifest_sha256=args.expected_manifest_sha256)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(2 if result['status'] == 'REJECTED' else 0)


if __name__ == '__main__':
    main()
