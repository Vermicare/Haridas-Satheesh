#!/usr/bin/env python3
"""Prospective A01T -> A01E exploratory cross-day confidence-only baseline.

Predeclared in WBI_A01E_DIFFERENT_DAY_BASELINE_V12.md before any E scoring.
No E session data or labels enter training/calibration. No raw/trial-level
EEG, labels or probabilities are persisted. No drift gate or safety claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import math
import os
from pathlib import Path
import platform
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

import numpy as np
from scipy.io import loadmat
from scipy.signal import butter, sosfiltfilt
import scipy
import sklearn
from sklearn.metrics import balanced_accuracy_score

from bnci_a01t_training_run_pilot_v09 import (
    EXPECTED_SHA256 as TRAIN_SHA, fetch_pinned_training_bytes,
    load_training_runs, extract_run_features, split_training_session,
    freeze_on_training_and_calibration, score_frozen,
    EEG_CHANNELS, TOTAL_CHANNELS, SAMPLE_RATE, BANDPASS_HZ,
    EPOCH_START_S, EPOCH_END_S,
)

E_FILE = 'A01E.mat'
E_URL = 'https://bnci-horizon-2020.eu/database/data-sets/001-2014/' + E_FILE
E_ALLOWED = {
    ('bnci-horizon-2020.eu', '/database/data-sets/001-2014/' + E_FILE),
    ('lampx.tugraz.at', '/~bci/database/001-2014/' + E_FILE),
}
MAX_E_BYTES = 100 * 1024 * 1024
FROZEN_T_SOURCE_BLOB = '9293fdeff26b621e966da2cd76ab2da1e3220e7f'
FROZEN_T_CORRECT = 43
FROZEN_T_HELDOUT = 96
TARGETS = ('0.30', '0.50', '0.70')


def require(ok, why):
    if not ok:
        raise ValueError(why)


def validate_e_url(url):
    require(type(url) is str, 'E source URL must be text')
    p = urlparse(url)
    require(p.scheme == 'https' and (p.hostname, p.path) in E_ALLOWED
            and p.port is None and not p.username and not p.password
            and not p.query and not p.fragment, 'unapproved E source URL/redirect')


class ERedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_e_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_e_bytes():
    validate_e_url(E_URL)
    req = Request(E_URL, headers={'Accept-Encoding': 'identity',
                                  'User-Agent': 'WBI-A01E-different-day-baseline/1.2'})
    with build_opener(ERedirect()).open(req, timeout=90) as response:
        validate_e_url(response.geturl())
        require(response.status == 200, 'E source HTTP status not 200')
        declared = response.headers.get('Content-Length')
        if declared is not None:
            require(declared.isascii() and declared.isdecimal() and
                    128 <= int(declared) <= MAX_E_BYTES,
                    'invalid E Content-Length')
        parts, n = [], 0
        while True:
            part = response.read(1024 * 1024)
            if not part:
                break
            n += len(part)
            require(n <= MAX_E_BYTES, 'E source exceeds byte limit')
            parts.append(part)
        if declared is not None:
            require(n == int(declared), 'truncated E source')
    raw = b''.join(parts)
    require(128 <= len(raw) <= MAX_E_BYTES and
            raw.startswith(b'MATLAB 5.0 MAT-file'), 'invalid E MAT response')
    return raw


def check_frozen_training_blob():
    source = Path(__file__).with_name('bnci_a01t_training_run_pilot_v09.py').read_bytes()
    digest = hashlib.sha1(b'blob ' + str(len(source)).encode() + bytes([0]) + source).hexdigest()
    require(digest == FROZEN_T_SOURCE_BLOB, 'frozen T implementation changed')
    return digest


def load_e_blocks(raw):
    require(type(raw) is bytes and 128 <= len(raw) <= MAX_E_BYTES and
            raw.startswith(b'MATLAB 5.0 MAT-file'), 'invalid E source')
    obj = loadmat(BytesIO(raw), struct_as_record=False, squeeze_me=True,
                  variable_names=['data'])
    require('data' in obj, 'E data structure missing')
    blocks = list(np.asarray(obj['data'], dtype=object).flat)
    require(len(blocks) == 9, 'E session expected 3 baseline + 6 task blocks')
    return blocks


def extract_e_features_unlabeled(blocks):
    """Do not access .y, .artifacts or any E evaluation outcome here."""
    require(len(blocks) == 9, 'unexpected E block count')
    for b in blocks[:3]:
        require(hasattr(b, 'trial') and np.asarray(b.trial).size == 0,
                'E baseline blocks contain cues')
    sos = butter(4, BANDPASS_HZ, btype='bandpass', fs=SAMPLE_RATE, output='sos')
    features = []
    for b in blocks[3:]:
        require(all(hasattr(b, field) for field in ('X', 'trial', 'fs')),
                'E task structure incomplete')
        fs = np.asarray(b.fs).reshape(-1)
        require(fs.size == 1 and float(fs[0]) == SAMPLE_RATE, 'E sampling rate changed')
        x = np.asarray(b.X)
        require(x.ndim == 2 and x.shape[1] == TOTAL_CHANNELS and
                x.shape[0] > 1000 and np.isfinite(x[:, :EEG_CHANNELS]).all(),
                'invalid E EEG dimensions/samples')
        cues = np.asarray(b.trial).reshape(-1)
        require(cues.shape == (48,) and np.issubdtype(cues.dtype, np.number)
                and np.isfinite(cues).all() and
                np.equal(cues, np.floor(cues)).all() and
                (cues >= 1).all() and np.all(np.diff(cues) > 0),
                'invalid E cue positions')
        filtered = sosfiltfilt(sos, x[:, :EEG_CHANNELS].astype(np.float64), axis=0)
        for cue in cues.astype(int):
            lo = cue - 1 + round(EPOCH_START_S * SAMPLE_RATE)
            hi = cue - 1 + round(EPOCH_END_S * SAMPLE_RATE)
            require(0 <= lo < hi <= len(filtered), 'E epoch outside recording')
            features.append(np.log(np.var(filtered[lo:hi], axis=0) + 1e-12))
    arr = np.asarray(features)
    require(arr.shape == (288, EEG_CHANNELS) and np.isfinite(arr).all(),
            'invalid E feature matrix')
    return arr


def extract_e_labels_after_prediction(blocks):
    """Access labels only AFTER the frozen model has generated predictions."""
    labels, flags = [], []
    for b in blocks[3:]:
        if not hasattr(b, 'y'):
            return None, None
        y = np.asarray(b.y).reshape(-1)
        require(y.shape == (48,) and np.issubdtype(y.dtype, np.number) and
                np.isfinite(y).all() and np.equal(y, np.floor(y)).all() and
                np.isin(y, [1, 2, 3, 4]).all(), 'invalid E labels')
        labels.extend(y.astype(int).tolist())
        if hasattr(b, 'artifacts'):
            f = np.asarray(b.artifacts).reshape(-1)
            require(f.shape == (48,) and np.issubdtype(f.dtype, np.number) and
                    np.isfinite(f).all() and np.isin(f, [0, 1]).all(),
                    'invalid E artifact flags')
            flags.extend(f.astype(int).tolist())
        else:
            flags = None
    require(len(labels) == 288, 'E label count mismatch')
    return np.asarray(labels, dtype=int), (np.asarray(flags, dtype=int)
            if flags is not None and len(flags) == 288 else None)


def score_e(probabilities, labels, thresholds):
    p = np.asarray(probabilities)
    y = np.asarray(labels)
    require(p.shape == (288, 4) and y.shape == (288,), 'E prediction/label mismatch')
    require(np.isfinite(p).all() and (p >= 0).all() and (p <= 1).all() and
            np.allclose(p.sum(axis=1), 1, atol=1e-7, rtol=0),
            'invalid probability simplex')
    require(np.isin(y, [1, 2, 3, 4]).all() and
            np.issubdtype(y.dtype, np.integer), 'invalid E class labels')
    require(type(thresholds) is dict and set(thresholds) == set(TARGETS),
            'calibration thresholds changed')
    prediction = p.argmax(axis=1) + 1
    correct = prediction == y
    confidence = p.max(axis=1)
    ece = 0.0
    for i in range(10):
        mask = (confidence >= i / 10) & (confidence < (i + 1) / 10 if i < 9
                                          else confidence <= 1)
        if mask.any():
            ece += float(mask.mean()) * abs(float(correct[mask].mean()) -
                                             float(confidence[mask].mean()))
    onehot = (np.arange(1, 5)[None, :] == y[:, None]).astype(float)
    selective = {}
    for key in TARGETS:
        t = thresholds[key]
        require(type(t) in (int, float) and math.isfinite(t) and 0 <= t <= 1,
                'invalid frozen threshold')
        acted = confidence >= t
        n = int(acted.sum())
        incorrect = int(np.logical_and(acted, ~correct).sum())
        selected_correct = n - incorrect
        selective[key] = {
            'threshold_from_A01T_calibration_only': float(t),
            'acted_n': n, 'incorrect_acted_n': incorrect,
            'coverage': n / 288,
            'incorrect_action_risk': incorrect / n if n else None,
            'correct_action_retention': (selected_correct / int(correct.sum())
                                         if correct.sum() else None),
        }
    return {
        'trials': 288, 'correct_n': int(correct.sum()),
        'accuracy': float(correct.mean()),
        'balanced_accuracy': float(balanced_accuracy_score(y, prediction)),
        'multiclass_brier_sum_of_squares':
            float(np.mean(np.sum((p - onehot)**2, axis=1))),
        'ece_10_equal_width_max_confidence': ece,
        'confidence_only_abstention': selective,
    }


def run():
    # Frozen T fitting occurs before E source acquisition or label access.
    source_blob = check_frozen_training_blob()
    t_pairs = extract_run_features(load_training_runs(fetch_pinned_training_bytes()))
    train, cal, heldout = split_training_session(t_pairs)
    frozen = freeze_on_training_and_calibration(train, cal)
    old = score_frozen(frozen, heldout)
    require(old['heldout_trials'] == FROZEN_T_HELDOUT and
            round(old['four_class_accuracy'] * FROZEN_T_HELDOUT) == FROZEN_T_CORRECT,
            'historical A01T v0.9 result changed')
    scaler, model, thresholds = frozen
    require(np.array_equal(model.classes_, [1, 2, 3, 4]), 'class mapping changed')
    raw = fetch_e_bytes()
    e_sha = hashlib.sha256(raw).hexdigest()
    blocks = load_e_blocks(raw)
    features = extract_e_features_unlabeled(blocks)
    probabilities = model.predict_proba(scaler.transform(features))
    require(probabilities.shape == (288, 4), 'E prediction count mismatch')
    # Prediction seal is computed BEFORE reading any E labels, but is not an
    # independent process or immutable external timestamp.
    prediction_sha = hashlib.sha256(
        np.asarray(probabilities, dtype='<f8', order='C').tobytes()).hexdigest()
    labels, flags = extract_e_labels_after_prediction(blocks)
    result = score_e(probabilities, labels, thresholds) if labels is not None else 'TBD'
    return {
        'schema': 'wbi-a01t-to-a01e-exploratory-different-day-v1.2',
        'protocol_frozen_before_E_scoring': 'WBI_A01E_DIFFERENT_DAY_BASELINE_V12.md',
        'run_utc': datetime.now(timezone.utc).isoformat(),
        'github_sha': os.environ.get('GITHUB_SHA', 'TBD'),
        'python_version': platform.python_version(),
        'numpy_version': np.__version__, 'scipy_version': scipy.__version__,
        'scikit_learn_version': sklearn.__version__,
        'source_T_sha256': TRAIN_SHA, 'source_T_code_git_blob': source_blob,
        'source_E_sha256_observed_not_publisher_signed': e_sha,
        'source_E_bytes': len(raw), 'source_E_url': E_URL,
        'prediction_sha256_pre_label_access': prediction_sha,
        'prediction_seal_independently_time_stamped': False,
        'labels_available_in_public_E_MAT': labels is not None,
        'E_artifact_flags_available': flags is not None,
        'E_source_flagged_n': int(flags.sum()) if flags is not None else 'TBD',
        'training_runs': [1, 2, 3], 'calibration_runs': [4],
        'E_task_runs': 6, 'E_trial_opportunities': 288,
        'A01T_frozen_within_day_correct_n': FROZEN_T_CORRECT,
        'A01T_frozen_within_day_total_n': FROZEN_T_HELDOUT,
        'E_different_day_baseline': result,
        'E_data_used_for_training_or_thresholds': False,
        'E_labels_accessed_after_prediction': labels is not None,
        'raw_or_trial_level_outputs_persisted': False,
        'drift_gate_evaluated': False, 'rest_state_false_actions': 'TBD',
        'nine_subject_replication': 'TBD', 'clinical_safety': False,
        'maturity': 'Research / Simulation, unchanged',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'refusing to overwrite evidence')
    report = run()
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(report, f, sort_keys=True, indent=2, allow_nan=False)
        f.write(chr(10))
    print(json.dumps({
        'E_sha256': report['source_E_sha256_observed_not_publisher_signed'],
        'E_bytes': report['source_E_bytes'],
        'E_artifact_flags_available': report['E_artifact_flags_available'],
        'E_different_day_baseline': report['E_different_day_baseline'],
        'E_data_used_for_training_or_thresholds': False,
        'maturity': report['maturity'],
    }, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
