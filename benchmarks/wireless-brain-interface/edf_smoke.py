#!/usr/bin/env python3
"""Read-only, one-file EEGMMIDB EDF+ integrity smoke; no decoding/training.

This tool uses only a predeclared TRAIN subject (S001) and imagery run R04.
A published checksum fetched over HTTPS is a source consistency check, not
cryptographic proof of publisher identity or a clinical validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

BASE = 'https://physionet.org/files/eegmmidb/1.0.0/'
REL = 'S001/S001R04.edf'
MAX_BYTES = 8 * 1024 * 1024
MAX_SUMS_BYTES = 512 * 1024

class SmokeError(ValueError):
    pass


def checksum_from_index(index: str, relative_path: str = REL) -> str:
    matches = []
    for line in index.splitlines():
        m = re.fullmatch(r'([0-9a-fA-F]{64})\s+\*?(\.?/?[^\s]+)', line.strip())
        if m and m.group(2).lstrip('./') == relative_path:
            matches.append(m.group(1).lower())
    if len(matches) != 1:
        raise SmokeError(f'expected exactly one publisher checksum entry for {relative_path}; found {len(matches)}')
    return matches[0]


def _field(b: bytes, start: int, size: int) -> str:
    return b[start:start + size].decode('ascii', errors='strict').strip()


def inspect_edf(blob: bytes) -> dict:
    if len(blob) < 256 or _field(blob, 0, 8) != '0':
        raise SmokeError('invalid EDF fixed header/version')
    try:
        header_bytes = int(_field(blob, 184, 8))
        records = int(_field(blob, 236, 8))
        duration = float(_field(blob, 244, 8))
        signals = int(_field(blob, 252, 4))
    except ValueError as e:
        raise SmokeError('invalid EDF numeric header') from e
    if not (0 < records < 100000 and 0 < duration < 3600 and signals == 65):
        raise SmokeError('invalid record count/duration or expected 64 EEG + 1 annotation signal')
    if header_bytes != 256 * (signals + 1) or len(blob) < header_bytes:
        raise SmokeError('invalid EDF header byte count')
    head = blob[:header_bytes]
    labels = [_field(head, 256 + 16 * i, 16) for i in range(signals)]
    if len(set(labels)) != signals:
        raise SmokeError('duplicate EDF signal labels')
    annotations = [i for i, label in enumerate(labels) if 'annotations' in label.lower()]
    if len(annotations) != 1:
        raise SmokeError('missing or ambiguous EDF+ annotations channel')
    samples_start = 256 + signals * (16 + 80 + 8 + 8 + 8 + 8 + 8 + 80)
    try:
        samples = [int(_field(head, samples_start + i * 8, 8)) for i in range(signals)]
    except ValueError as e:
        raise SmokeError('invalid samples-per-record') from e
    if any(s <= 0 for s in samples):
        raise SmokeError('nonpositive samples-per-record')
    eeg_rates = [samples[i] / duration for i in range(signals) if i not in annotations]
    if len(eeg_rates) != 64 or any(abs(rate - 160.0) > 1e-9 for rate in eeg_rates):
        raise SmokeError('unexpected EEG sampling rate; inspect actual source before processing')
    expected_size = header_bytes + records * sum(samples) * 2
    if len(blob) != expected_size:
        raise SmokeError(f'EDF byte length mismatch: expected {expected_size}, actual {len(blob)}')
    return {'eeg_channels': 64, 'annotation_channels': 1, 'eeg_sampling_hz': 160,
            'data_records': records, 'record_duration_s': duration,
            'header_bytes': header_bytes, 'file_bytes': len(blob)}


def verify(edf: bytes, index: str) -> dict:
    expected = checksum_from_index(index)
    actual = hashlib.sha256(edf).hexdigest()
    if actual != expected:
        raise SmokeError('EDF SHA256 does not match publisher index')
    result = inspect_edf(edf)
    return {'status': 'STRUCTURAL_PREFLIGHT_ONLY', 'dataset': 'EEGMMIDB v1.0.0',
            'source_url': BASE + REL, 'publisher_checksum_index': BASE + 'SHA256SUMS.txt',
            'source_sha256': actual, 'source_checksum_matches_index': True,
            'subject_split': 'train', 'subject': 'S001', 'run': 'R04',
            'imagery_task': 'left/right fist', 'event_labels_decoded': False,
            'decoder_trained': False, 'test_subjects_accessed': False,
            'performance': 'TBD', 'source_origin_independently_attested': False,
            'structure': result}


def fetch(url: str, limit: int) -> bytes:
    request = urllib.request.Request(url, headers={'User-Agent': 'WBI-EDF-structural-smoke/0.1'})
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.geturl().split('/')[2] not in ('physionet.org', 'www.physionet.org'):
            raise SmokeError('unexpected download redirect host')
        data = response.read(limit + 1)
    if len(data) > limit:
        raise SmokeError('source exceeds predeclared size limit')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='download ONE training EDF + publisher SHA256 index')
    parser.add_argument('--edf', type=Path)
    parser.add_argument('--sha256-index', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.fetch == bool(args.edf or args.sha256_index):
        parser.error('use --fetch OR both --edf and --sha256-index')
    if not args.fetch and (not args.edf or not args.sha256_index):
        parser.error('both --edf and --sha256-index required')
    if args.fetch:
        edf = fetch(BASE + REL, MAX_BYTES)
        index = fetch(BASE + 'SHA256SUMS.txt', MAX_SUMS_BYTES).decode('ascii')
    else:
        edf = args.edf.read_bytes()
        index = args.sha256_index.read_text(encoding='ascii')
    report = verify(edf, index)
    payload = json.dumps(report, sort_keys=True, indent=2) + '\n'
    args.out.write_text(payload, encoding='utf-8', newline='\n')
    print(f"STRUCTURAL PREFLIGHT ONLY: {REL} sha256={report['source_sha256']} "
          f"records={report['structure']['data_records']} 64ch/160Hz; NO DECODING")


if __name__ == '__main__':
    main()
