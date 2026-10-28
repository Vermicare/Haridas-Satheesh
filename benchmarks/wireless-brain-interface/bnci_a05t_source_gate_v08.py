#!/usr/bin/env python3
"""A05T public training-file structure gate. Never export EEG or class labels.

A source digest is an observed byte identity, not a publisher signature.
No decoding, matched-coverage risk or clinical claim is produced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

import bnci_a02t_metadata_v03 as base

FILE = 'A05T.mat'
SOURCE = 'https://bnci-horizon-2020.eu/database/data-sets/001-2014/' + FILE
ALLOWED = {
    ('bnci-horizon-2020.eu', '/database/data-sets/001-2014/' + FILE),
    ('lampx.tugraz.at', '/~bci/database/001-2014/' + FILE),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_url(url: str) -> None:
    require(type(url) is str, 'invalid URL')
    parsed = urlparse(url)
    require(parsed.scheme == 'https' and (parsed.hostname, parsed.path) in ALLOWED
            and not parsed.username and not parsed.password and parsed.port is None
            and not parsed.query and not parsed.fragment, 'unapproved source or redirect')


class StrictRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_bytes() -> bytes:
    validate_url(SOURCE)
    opener = build_opener(StrictRedirect())
    request = Request(SOURCE, headers={'Accept-Encoding': 'identity',
                                      'User-Agent': 'WBI-A05T-training-structure/0.8'})
    with opener.open(request, timeout=90) as response:
        validate_url(response.geturl())
        require(response.status == 200, 'unexpected HTTP status')
        declared = response.headers.get('Content-Length')
        if declared is not None:
            require(declared.isascii() and declared.isdecimal() and
                    128 <= int(declared) <= base.MAX_BYTES, 'invalid declared byte count')
        parts, total = [], 0
        while True:
            part = response.read(1024 * 1024)
            if not part:
                break
            total += len(part)
            require(total <= base.MAX_BYTES, 'source exceeds byte bound')
            parts.append(part)
        if declared is not None:
            require(total == int(declared), 'truncated transfer')
    return b''.join(parts)


def validate_report(report: dict, raw: bytes) -> dict:
    """Reject inconsistent label-safe metadata; no publisher authentication."""
    require(type(raw) is bytes and 128 <= len(raw) <= base.MAX_BYTES,
            'invalid raw byte count')
    require(type(report) is dict, 'invalid metadata')
    expected = {
        'dataset': 'BNCI2014_001', 'session': 'T_training',
        'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_bytes': len(raw),
        'sha256_is_provider_authenticated': False,
        'class_label_values_inspected': False,
        'raw_eeg_persisted_or_uploaded': False,
        'evaluation_session_or_labels_accessed': False,
        'decode_accuracy': 'TBD', 'false_action_risk': 'TBD',
        'blocks': 9, 'cue_free_baseline_blocks': 3,
        'cued_task_blocks': 6, 'cues_total': 288,
        'six_task_runs_48_cues_each': True,
    }
    for key, value in expected.items():
        require(type(report.get(key)) is type(value) and report[key] == value,
                'invalid source metadata: ' + key)
    blocks = report.get('block_metadata')
    require(type(blocks) is list and len(blocks) == 9, 'invalid block list')
    for index, block in enumerate(blocks):
        require(type(block) is dict, 'invalid block object')
        require(type(block.get('block_index_zero_based')) is int and
                block['block_index_zero_based'] == index, 'invalid block index')
        require(type(block.get('samples')) is int and block['samples'] > 0,
                'invalid sample count')
        require(type(block.get('channels')) is int and block['channels'] == 25,
                'unexpected channel count')
        require(type(block.get('sampling_rate_hz')) in (int, float) and
                block['sampling_rate_hz'] == 250.0, 'unexpected sampling rate')
        require(type(block.get('cue_count')) is int and
                block['cue_count'] == (0 if index < 3 else 48),
                'baseline/task sequence mismatch')
    return report


def inspect_training_bytes(raw: bytes) -> dict:
    # Existing parser reads structural fields from T only; never export X or labels.
    report = base.inspect_bytes(raw)
    validate_report(report, raw)
    report['file'] = FILE
    report['source_url'] = SOURCE
    report['source_hash_status'] = 'observed, not publisher authenticated'
    report['training_only'] = True
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = Path(args.output)
    if target.exists():
        parser.error('refusing to overwrite an evidence file')
    report = inspect_training_bytes(fetch_bytes())
    target.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n',
                      encoding='utf-8')
    print(json.dumps({k: report[k] for k in (
        'file', 'source_sha256', 'source_bytes', 'blocks',
        'cue_free_baseline_blocks', 'cued_task_blocks', 'cues_total',
        'source_hash_status')}, sort_keys=True))


if __name__ == '__main__':
    main()
