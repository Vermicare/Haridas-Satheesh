#!/usr/bin/env python3
"""Inspect A02T.mat *training-session structure* from BNCI2014_001.

No EEG, labels, trial samples, or individual-level records are emitted. The
SHA-256 is a byte identity of a public upstream response, NOT publisher-signed
authenticity. This is not decoder or clinical evidence.
"""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import math
import platform
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

import numpy as np
import scipy
from scipy.io import loadmat

FILE = 'A02T.mat'
SOURCE = 'https://bnci-horizon-2020.eu/database/data-sets/001-2014/' + FILE
ALLOWED = {
    ('bnci-horizon-2020.eu', '/database/data-sets/001-2014/' + FILE),
    ('lampx.tugraz.at', '/~bci/database/001-2014/' + FILE),
}
MAX_BYTES = 100 * 1024 * 1024


def validate_url(url):
    if not isinstance(url, str):
        raise ValueError('invalid source URL type')
    p = urlparse(url)
    if (p.scheme != 'https' or (p.hostname, p.path) not in ALLOWED or
            p.username or p.password or p.port is not None or p.query or p.fragment):
        raise ValueError('unapproved source or redirect')


class StrictRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def inspect_bytes(raw):
    if type(raw) is not bytes or not (128 <= len(raw) <= MAX_BYTES):
        raise ValueError('invalid source byte length')
    if not raw.startswith(b'MATLAB 5.0 MAT-file'):
        raise ValueError('unexpected MAT signature')
    obj = loadmat(BytesIO(raw), struct_as_record=False, squeeze_me=True, variable_names=['data'])
    if 'data' not in obj:
        raise ValueError('missing data structure')
    container = obj['data']
    runs = list(np.asarray(container, dtype=object).flat) if isinstance(container, np.ndarray) else [container]
    if not 1 <= len(runs) <= 20:
        raise ValueError('invalid number of blocks')
    summaries = []
    for i, run in enumerate(runs):
        if not all(hasattr(run, attr) for attr in ('X', 'fs', 'trial')):
            raise ValueError('missing structural field')
        shape = np.shape(run.X)
        if len(shape) != 2 or shape[0] < 1 or shape[1] < 1:
            raise ValueError('invalid signal shape')
        fs = np.asarray(run.fs)
        if fs.size != 1 or not math.isfinite(float(fs.reshape(-1)[0])) or float(fs.reshape(-1)[0]) <= 0:
            raise ValueError('invalid sample frequency')
        trial = np.asarray(run.trial).reshape(-1)
        if trial.size:
            if (not np.issubdtype(trial.dtype, np.number) or
                    not np.all(np.isfinite(trial)) or
                    not np.all(trial == np.floor(trial)) or
                    not np.all((trial >= 1) & (trial <= shape[0])) or
                    not np.all(np.diff(trial) > 0)):
                raise ValueError('invalid cue sample positions')
        summaries.append({
            'block_index_zero_based': i,
            'samples': int(shape[0]),
            'channels': int(shape[1]),
            'sampling_rate_hz': float(fs.reshape(-1)[0]),
            'cue_count': int(trial.size),
        })
    cued = [r for r in summaries if r['cue_count'] > 0]
    baselines = [r for r in summaries if r['cue_count'] == 0]
    return {
        'dataset': 'BNCI2014_001', 'file': FILE, 'session': 'T_training',
        'source_url': SOURCE,
        'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_bytes': len(raw),
        'sha256_is_provider_authenticated': False,
        'blocks': len(summaries), 'cue_free_baseline_blocks': len(baselines),
        'cued_task_blocks': len(cued), 'cues_total': sum(r['cue_count'] for r in cued),
        'six_task_runs_48_cues_each': len(cued) == 6 and all(r['cue_count'] == 48 for r in cued),
        'block_metadata': summaries,
        'class_label_values_inspected': False, 'raw_eeg_persisted_or_uploaded': False,
        'evaluation_session_or_labels_accessed': False,
        'decode_accuracy': 'TBD', 'false_action_risk': 'TBD',
        'source_authenticity': 'TBD: upstream bytes are not publisher-signed',
        'numpy_version': np.__version__, 'scipy_version': scipy.__version__,
        'python_version': platform.python_version(),
        'maturity': 'Research / Simulation; unchanged',
    }


def fetch_bytes():
    validate_url(SOURCE)
    opener = build_opener(StrictRedirect())
    with opener.open(Request(SOURCE, headers={'Accept-Encoding': 'identity', 'User-Agent': 'WBI-public-MAT-structure/0.3'}), timeout=90) as r:
        validate_url(r.geturl())
        if r.status != 200:
            raise ValueError('source did not return HTTP 200')
        declared = r.headers.get('Content-Length')
        if declared is not None and (not declared.isascii() or not declared.isdecimal() or int(declared) > MAX_BYTES or int(declared) < 128):
            raise ValueError('invalid declared byte count')
        blocks, size = [], 0
        while True:
            block = r.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            if size > MAX_BYTES:
                raise ValueError('upstream source exceeds bound')
            blocks.append(block)
        if declared is not None and size != int(declared):
            raise ValueError('truncated source transfer')
    return b''.join(blocks)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    a = p.parse_args()
    from pathlib import Path
    target = Path(a.output)
    if target.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    report = inspect_bytes(fetch_bytes())
    target.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('file', 'source_sha256', 'source_bytes', 'blocks', 'cue_free_baseline_blocks', 'cued_task_blocks', 'cues_total', 'six_task_runs_48_cues_each')}, sort_keys=True))


if __name__ == '__main__':
    main()
