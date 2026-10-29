#!/usr/bin/env python3
"""Exploratory BNCI2014_001 A01T *training-session only* decoder pilot.

Does not access A01E, fit a drift gate, evaluate clinical safety, or claim a
cross-session EEG benchmark. Raw EEG and labels never leave memory; the only
optional output is aggregate, metadata-only JSON.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import math
import platform
from pathlib import Path
from urllib.request import Request, build_opener

import numpy as np
import scipy
from scipy.io import loadmat
from scipy.signal import butter, sosfiltfilt
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

from bnci2014_001_source_probe import PinnedRedirect, SOURCE_URL, validate_source_url

# Observed twice in hosted source acquisition, not publisher authenticated.
EXPECTED_BYTES = 42_806_453
EXPECTED_SHA256 = '054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325'
MAX_BYTES = 100 * 1024 * 1024
SAMPLE_RATE = 250
EEG_CHANNELS = 22
TOTAL_CHANNELS = 25
EPOCH_START_S = 2.5  # 0.5 s after the cue at trial t=2 seconds
EPOCH_END_S = 4.5
BANDPASS_HZ = (8.0, 30.0)
TRAIN_RUNS = (1, 2, 3)
CAL_RUNS = (4,)
TEST_RUNS = (5, 6)
TARGET_COVERAGES = (0.30, 0.50, 0.70)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fetch_pinned_training_bytes():
    """Allowlisted HTTPS A01T only, bounded in memory, never written to disk."""
    validate_source_url(SOURCE_URL)
    req = Request(SOURCE_URL, headers={
        'User-Agent': 'WBI-A01T-training-only-pilot/0.9',
        'Accept-Encoding': 'identity',
    })
    with build_opener(PinnedRedirect()).open(req, timeout=90) as resp:
        validate_source_url(resp.geturl())
        require(resp.status == 200, 'non-200 source response')
        length = resp.headers.get('Content-Length')
        if length is not None:
            require(length.isascii() and length.isdecimal() and
                    int(length) == EXPECTED_BYTES, 'source Content-Length mismatch')
        chunks, total = [], 0
        while True:
            part = resp.read(1024 * 1024)
            if not part:
                break
            total += len(part)
            require(total <= MAX_BYTES, 'source size bound exceeded')
            chunks.append(part)
    raw = b''.join(chunks)
    verify_source_bytes(raw)
    return raw


def verify_source_bytes(raw):
    require(type(raw) is bytes and len(raw) == EXPECTED_BYTES,
            'A01T source byte length does not match pinned observation')
    require(raw.startswith(b'MATLAB 5.0 MAT-file'), 'unexpected MAT signature')
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256,
            'A01T source digest does not match pinned observation')


def load_training_runs(raw):
    verify_source_bytes(raw)
    obj = loadmat(BytesIO(raw), struct_as_record=False, squeeze_me=True,
                  variable_names=['data'])
    require('data' in obj, 'MAT data structure missing')
    blocks = list(np.asarray(obj['data'], dtype=object).flat)
    require(len(blocks) == 9, 'A01T requires 3 baseline + 6 task blocks')
    return blocks


def extract_run_features(blocks):
    """Returns six task-run (features, labels) pairs; never raw samples.

    Filters each continuous task run separately; no test-run information enters
    training-run preprocessing. EOG columns 23-25 are excluded.
    """
    require(type(blocks) in (list, tuple) and len(blocks) == 9,
            'wrong A01T recording-block count')
    for block in blocks[:3]:
        require(hasattr(block, 'trial') and np.asarray(block.trial).size == 0,
                'baseline blocks must not contain task trials')
    sos = butter(4, BANDPASS_HZ, btype='bandpass', fs=SAMPLE_RATE, output='sos')
    result = []
    for task_idx, block in enumerate(blocks[3:], 1):
        require(all(hasattr(block, field) for field in ('X', 'trial', 'y', 'fs')),
                'missing training-run field')
        fs = np.asarray(block.fs)
        require(fs.size == 1 and float(fs.reshape(-1)[0]) == SAMPLE_RATE,
                'unexpected sampling rate')
        x = np.asarray(block.X)
        require(x.ndim == 2 and x.shape[1] == TOTAL_CHANNELS and
                x.shape[0] > 1000, 'unexpected signal dimensions')
        require(np.isfinite(x[:, :EEG_CHANNELS]).all(), 'nonfinite EEG samples')
        cue = np.asarray(block.trial).reshape(-1)
        labels = np.asarray(block.y).reshape(-1)
        require(len(cue) == 48 and len(labels) == 48, 'unexpected trial count')
        require(np.issubdtype(cue.dtype, np.number) and
                np.isfinite(cue).all() and np.equal(cue, np.floor(cue)).all() and
                np.diff(cue).min() > 0, 'invalid cue indices')
        require(np.issubdtype(labels.dtype, np.number) and
                np.isfinite(labels).all() and np.equal(labels, np.floor(labels)).all() and
                set(labels.tolist()) == {1, 2, 3, 4}, 'invalid four-class labels')
        # Avoid post-hoc artifact exclusions: keep all 48 task trials.
        # One-based trial index is trial t=0, not the t=2-second cue.
        filtered = sosfiltfilt(sos, x[:, :EEG_CHANNELS].astype(np.float64), axis=0)
        feats = []
        for onset in cue.astype(int):
            begin = onset - 1 + round(EPOCH_START_S * SAMPLE_RATE)
            end = onset - 1 + round(EPOCH_END_S * SAMPLE_RATE)
            require(0 <= begin < end <= len(filtered), 'epoch out of bounds')
            epoch = filtered[begin:end]
            feats.append(np.log(np.var(epoch, axis=0) + 1e-12))
        result.append((np.asarray(feats), labels.astype(int)))
    return result


def split_training_session(run_pairs):
    require(len(run_pairs) == 6, 'expected six task runs')
    def combine(run_numbers):
        features = np.vstack([run_pairs[i - 1][0] for i in run_numbers])
        labels = np.concatenate([run_pairs[i - 1][1] for i in run_numbers])
        require(len(features) == 48 * len(run_numbers), 'unexpected split size')
        return features, labels
    return combine(TRAIN_RUNS), combine(CAL_RUNS), combine(TEST_RUNS)


def freeze_on_training_and_calibration(train, calibration):
    """Fit on runs 1-3; thresholds from run-4 confidences only.

    Held-out run 5/6 features or labels are not arguments to this function.
    """
    x_train, y_train = train
    x_cal, _ = calibration
    require(x_train.shape == (144, EEG_CHANNELS) and x_cal.shape == (48, EEG_CHANNELS),
            'wrong train/calibration feature shapes')
    require(set(y_train.tolist()) == {1, 2, 3, 4}, 'missing training class')
    require(np.isfinite(x_train).all() and np.isfinite(x_cal).all(),
            'nonfinite features')
    scaler = StandardScaler().fit(x_train)
    model = LogisticRegression(C=1.0, max_iter=2000, solver='lbfgs', random_state=20261029)
    model.fit(scaler.transform(x_train), y_train)
    require(np.array_equal(model.classes_, [1, 2, 3, 4]), 'unexpected class mapping')
    confidence = model.predict_proba(scaler.transform(x_cal)).max(axis=1)
    sorted_conf = np.sort(confidence)[::-1]
    thresholds = {f'{coverage:.2f}': float(sorted_conf[max(1, math.ceil(48 * coverage)) - 1])
                  for coverage in TARGET_COVERAGES}
    return scaler, model, thresholds


def ece_max_confidence(probabilities, labels):
    confidence = probabilities.max(axis=1)
    correct = (probabilities.argmax(axis=1) + 1 == labels)
    edges = np.linspace(0, 1, 11)
    total = 0.0
    for idx in range(10):
        mask = (confidence >= edges[idx]) & ((confidence < edges[idx + 1]) if idx < 9
                                                 else (confidence <= edges[idx + 1]))
        if mask.any():
            total += float(mask.mean()) * abs(float(correct[mask].mean()) -
                                               float(confidence[mask].mean()))
    return total


def score_frozen(frozen, heldout):
    scaler, model, thresholds = frozen
    x_test, y_test = heldout
    require(x_test.shape == (96, EEG_CHANNELS) and y_test.shape == (96,),
            'unexpected heldout run shape')
    require(set(y_test.tolist()) == {1, 2, 3, 4}, 'missing heldout class')
    probabilities = model.predict_proba(scaler.transform(x_test))
    predictions = model.classes_[probabilities.argmax(axis=1)]
    correct = predictions == y_test
    conf = probabilities.max(axis=1)
    selective = {}
    for key, threshold in thresholds.items():
        acted = conf >= threshold
        n = int(acted.sum())
        correct_acted = int(np.logical_and(acted, correct).sum())
        selective[key] = {
            'calibration_target_coverage': float(key),
            'frozen_confidence_threshold': threshold,
            'heldout_acted_n': n,
            'heldout_coverage': n / len(y_test),
            'heldout_incorrect_action_risk': (n - correct_acted) / n if n else None,
            'heldout_correct_action_retention': (
                correct_acted / int(correct.sum()) if correct.sum() else None),
        }
    onehot = (np.arange(1, 5)[None, :] == y_test[:, None]).astype(float)
    return {
        'heldout_trials': int(len(y_test)),
        'four_class_accuracy': float(correct.mean()),
        'four_class_balanced_accuracy': float(balanced_accuracy_score(y_test, predictions)),
        'multiclass_brier_sum_of_squares': float(np.mean(np.sum((probabilities - onehot)**2, axis=1))),
        'ece_10_equal_width_max_confidence': ece_max_confidence(probabilities, y_test),
        'confidence_only_abstention': selective,
    }


def run_pilot(raw):
    run_pairs = extract_run_features(load_training_runs(raw))
    train, cal, test = split_training_session(run_pairs)
    frozen = freeze_on_training_and_calibration(train, cal)
    scored = score_frozen(frozen, test)
    return {
        'schema': 'wbi-a01t-training-only-exploratory-v0.9',
        'dataset': 'BNCI2014_001', 'file': 'A01T.mat',
        'source_sha256': EXPECTED_SHA256, 'source_bytes': EXPECTED_BYTES,
        'publisher_signature_authenticated': False,
        'license': 'CC BY-ND 4.0 (publisher catalog); raw files not redistributed',
        'split': {'train_runs': list(TRAIN_RUNS), 'calibration_runs': list(CAL_RUNS),
                  'heldout_training_runs': list(TEST_RUNS), 'train_trials': 144,
                  'calibration_trials': 48, 'heldout_trials': 96},
        'features': 'log variance of 22 EEG channels, 8-30 Hz fourth-order Butterworth SOS; no EOG',
        'epoch_seconds_from_trial_start': [EPOCH_START_S, EPOCH_END_S],
        'classifier': 'StandardScaler(train-only) + LogisticRegression(C=1, lbfgs, max_iter=2000)',
        'threshold_rule': 'calibration-only confidence quantiles, no heldout tuning',
        'random_seed': 20261029,
        'python_version': platform.python_version(), 'numpy_version': np.__version__,
        'scipy_version': scipy.__version__, 'sklearn_version': sklearn.__version__,
        'run_utc': datetime.now(timezone.utc).isoformat(),
        'training_class_labels_used': True,
        'session_E_downloaded_or_labels_accessed': False,
        'raw_eeg_or_trial_level_outputs_persisted': False,
        'drift_gate_tested': False, 'clinical_or_real_world_validation': False,
        'maturity': 'Research / Simulation, unchanged',
        'heldout_training_run_exploratory_result': scored,
        'different_day_E_session_metrics': 'TBD',
        'matched_coverage_drift_gate_benefit': 'TBD',
        'independent_subject_replication': 'TBD',
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path,
                   help='new metadata-only JSON path, never raw EEG or trial predictions')
    args = p.parse_args()
    require(not args.output.exists(), 'refusing to overwrite evidence')
    report = run_pilot(fetch_pinned_training_bytes())
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n',
                           encoding='utf-8')
    print(json.dumps({
        'source_sha256': report['source_sha256'],
        'heldout_training_run_exploratory_result': report['heldout_training_run_exploratory_result'],
        'session_E_downloaded_or_labels_accessed': False,
        'drift_gate_tested': False,
    }, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
