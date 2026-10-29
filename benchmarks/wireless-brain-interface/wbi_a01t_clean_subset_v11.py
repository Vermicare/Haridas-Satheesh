#!/usr/bin/env python3
"""A01T v1.1: predeclared descriptive clean-trial sensitivity; no E-session access.

Reuses the frozen v0.9 model, split and thresholds. Source artifact flags are
not used for fitting, threshold selection, or changing the primary all-trial
score. Never persists per-trial EEG, flags, labels, or predictions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import platform
from pathlib import Path

import numpy as np

SOURCE_SHA256 = '054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325'
EXPECTED_ALL_CORRECT = 43
EXPECTED_ALL_N = 96
EXPECTED_FLAGGED_N = 5
EXPECTED_SELECTIVE = {'0.30': (19, 6), '0.50': (38, 15), '0.70': (55, 24)}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def score_clean_subset(probabilities, labels, flags, frozen_thresholds):
    """Score a fixed model's predictions with *source* flags; no refitting.

    All inputs remain in memory. Only aggregate counts/rates are returned.
    """
    p = np.asarray(probabilities)
    y = np.asarray(labels)
    f = np.asarray(flags)
    require(p.ndim == 2 and p.shape[1] == 4 and p.shape[0] > 0,
            'expected nonempty four-class probabilities')
    n = p.shape[0]
    require(y.shape == (n,) and f.shape == (n,), 'trial alignment mismatch')
    require(np.issubdtype(p.dtype, np.number) and np.isfinite(p).all() and
            (p >= 0).all() and (p <= 1).all() and
            np.allclose(p.sum(axis=1), 1.0, rtol=0, atol=1e-7),
            'invalid probability simplex')
    require(np.issubdtype(y.dtype, np.number) and np.isfinite(y).all() and
            np.isin(y, [1, 2, 3, 4]).all(), 'invalid labels')
    require(np.issubdtype(f.dtype, np.number) and np.isfinite(f).all() and
            np.isin(f, [0, 1]).all(), 'invalid source flags')
    require(type(frozen_thresholds) is dict and frozen_thresholds,
            'frozen thresholds required')
    for key, value in frozen_thresholds.items():
        require(type(key) is str and type(value) in (float, int) and
                np.isfinite(value) and 0 <= value <= 1,
                'invalid frozen threshold')
    clean = f == 0
    predictions = p.argmax(axis=1) + 1
    correct = predictions == y
    confidence = p.max(axis=1)
    clean_n = int(clean.sum())
    correct_clean = int(np.logical_and(correct, clean).sum())
    result = {
        'all_trials_n': n,
        'all_trials_correct_n': int(correct.sum()),
        'all_trials_accuracy': float(correct.mean()),
        'source_flagged_n': int((~clean).sum()),
        'source_unflagged_n': clean_n,
        'source_unflagged_correct_n': correct_clean,
        'source_unflagged_accuracy_observed': correct_clean / clean_n if clean_n else None,
        'frozen_confidence_only': {},
    }
    for key, threshold in sorted(frozen_thresholds.items()):
        acted = confidence >= threshold
        acted_clean = np.logical_and(acted, clean)
        n_all = int(acted.sum())
        n_clean = int(acted_clean.sum())
        errors_all = int(np.logical_and(acted, ~correct).sum())
        errors_clean = int(np.logical_and(acted_clean, ~correct).sum())
        result['frozen_confidence_only'][key] = {
            'threshold_from_calibration_only': float(threshold),
            'all_acted_n': n_all,
            'all_incorrect_acted_n': errors_all,
            'unflagged_acted_n': n_clean,
            'unflagged_incorrect_acted_n': errors_clean,
            'unflagged_coverage': n_clean / clean_n if clean_n else None,
            'unflagged_incorrect_action_risk': errors_clean / n_clean if n_clean else None,
        }
    return result


def require_frozen_v09_and_v10_match(scored):
    """Fail closed if the source or frozen original result has drifted."""
    require(scored['all_trials_n'] == EXPECTED_ALL_N and
            scored['all_trials_correct_n'] == EXPECTED_ALL_CORRECT,
            'frozen v0.9 all-trial result mismatch')
    require(scored['source_flagged_n'] == EXPECTED_FLAGGED_N,
            'frozen v1.0 source-flag count mismatch')
    require(set(scored['frozen_confidence_only']) == set(EXPECTED_SELECTIVE),
            'frozen v0.9 threshold keys mismatch')
    for key, (acted, errors) in EXPECTED_SELECTIVE.items():
        row = scored['frozen_confidence_only'][key]
        require((row['all_acted_n'], row['all_incorrect_acted_n']) == (acted, errors),
                'frozen v0.9 selective result mismatch at ' + key)


def run_source_audit():
    # Imports occur only when executing the real-data path, not in fictional tests.
    from bnci_a01t_training_run_pilot_v09 import (
        EXPECTED_SHA256, fetch_pinned_training_bytes, load_training_runs,
        extract_run_features, split_training_session, freeze_on_training_and_calibration,
        score_frozen,
    )
    from bnci_a01t_artifact_audit_v10 import audit_flags
    require(EXPECTED_SHA256 == SOURCE_SHA256, 'source fingerprint changed')
    blocks = load_training_runs(fetch_pinned_training_bytes())
    per_run, splits = audit_flags(blocks)
    require([r['artifact_flagged'] for r in per_run] == [2, 4, 3, 1, 2, 3],
            'v1.0 source run counts mismatch')
    flags = np.concatenate([
        np.asarray(block.artifacts).reshape(-1) for block in blocks[7:9]
    ])
    pairs = extract_run_features(blocks)
    train, calibration, heldout = split_training_session(pairs)
    frozen = freeze_on_training_and_calibration(train, calibration)
    old = score_frozen(frozen, heldout)
    scaler, model, thresholds = frozen
    require(np.array_equal(model.classes_, [1, 2, 3, 4]),
            'frozen class order mismatch')
    probabilities = model.predict_proba(scaler.transform(heldout[0]))
    scored = score_clean_subset(probabilities, heldout[1], flags, thresholds)
    require_frozen_v09_and_v10_match(scored)
    require(abs(old['four_class_accuracy'] - scored['all_trials_accuracy']) < 1e-12,
            'original v0.9 scorer disagrees')
    require(splits['heldout_within_day']['artifact_flagged'] == scored['source_flagged_n'],
            'v1.0 heldout source flags disagree')
    # No per-trial arrays are returned or persisted.
    return {
        'schema': 'wbi-a01t-clean-subset-sensitivity-v1.1',
        'source': 'BNCI2014_001/A01T.mat',
        'source_sha256_observed_not_publisher_signed': SOURCE_SHA256,
        'source_bytes': 42806453,
        'analysis': 'post-hoc descriptive sensitivity using pre-frozen v0.9 model and thresholds',
        'train_runs': [1, 2, 3], 'calibration_runs': [4],
        'within_day_heldout_runs': [5, 6],
        'run_utc': datetime.now(timezone.utc).isoformat(),
        'git_sha': os.environ.get('GITHUB_SHA', 'TBD'),
        'python_version': platform.python_version(),
        'numpy_version': np.__version__,
        'scikit_learn_version': __import__('sklearn').__version__,
        'scipy_version': __import__('scipy').__version__,
        'results': scored,
        'original_v09_primary_result_replaced': False,
        'A01E_accessed': False,
        'raw_or_trial_level_data_persisted': False,
        'independent_subject_or_day_validation': 'TBD',
        'drift_gate_benefit': 'TBD',
        'clinical_safety_validation': False,
        'maturity': 'Research / Simulation, unchanged',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run_source_audit()
    # Exclusive creation also protects against overwrite races.
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
    print(json.dumps({'source_sha256': SOURCE_SHA256, 'results': report['results'],
                      'A01E_accessed': False}, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
