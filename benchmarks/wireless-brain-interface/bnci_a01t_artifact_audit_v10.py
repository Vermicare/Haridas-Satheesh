#!/usr/bin/env python3
"""Read-only A01T trial-artifact audit; no labels, E session, or decoding.

The reported accuracy bounds are mathematical identification bounds, NOT
observed artifact-free accuracy or a confidence interval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

import numpy as np

from bnci_a01t_training_run_pilot_v09 import (
    EXPECTED_BYTES, EXPECTED_SHA256, fetch_pinned_training_bytes,
    load_training_runs,
)

TOTAL_HELDOUT = 96
FROZEN_CORRECT = 43  # From independently reproduced v0.9; do not recompute labels.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit_flags(blocks):
    """Inspect task-run flags only, preserving original trial denominators."""
    require(len(blocks) == 9, 'expected three baseline and six task blocks')
    per_run = []
    for run_no, block in enumerate(blocks[3:], 1):
        require(hasattr(block, 'trial') and hasattr(block, 'artifacts'),
                'trial positions or source artifact flags missing')
        trials = np.asarray(block.trial).reshape(-1)
        flags = np.asarray(block.artifacts).reshape(-1)
        require(trials.shape == (48,) and flags.shape == (48,),
                'expected exactly 48 trial positions and artifact flags per run')
        require(np.issubdtype(trials.dtype, np.number) and
                np.isfinite(trials).all() and np.equal(trials, np.floor(trials)).all() and
                (trials >= 1).all() and np.all(np.diff(trials) > 0),
                'invalid one-based trial positions')
        require(np.issubdtype(flags.dtype, np.number) and
                np.isfinite(flags).all() and np.isin(flags, (0, 1)).all(),
                'artifact flags must be binary 0/1')
        flagged = int(np.count_nonzero(flags))
        per_run.append({'task_run': run_no, 'total_trials': 48,
                        'artifact_flagged': flagged, 'unflagged': 48 - flagged})
    groups = {'training': (1, 2, 3), 'calibration': (4,), 'heldout_within_day': (5, 6)}
    splits = {}
    for name, runs in groups.items():
        flagged = sum(per_run[i - 1]['artifact_flagged'] for i in runs)
        total = 48 * len(runs)
        splits[name] = {'task_runs': list(runs), 'total_trials': total,
                        'artifact_flagged': flagged, 'unflagged': total - flagged}
    return per_run, splits


def accuracy_identification_bounds(total, correct, flagged):
    """Sharp worst/best unflagged accuracy given only all-trial correct count.

    Does not inspect trial labels or predictions; not a statistical CI.
    """
    require(all(type(x) is int for x in (total, correct, flagged)), 'integer counts required')
    require(total > 0 and 0 <= correct <= total and 0 <= flagged <= total,
            'invalid trial/correct/flag counts')
    clean = total - flagged
    if clean == 0:
        return {'unflagged_n': 0, 'possible_unflagged_correct_min': 0,
                'possible_unflagged_correct_max': 0,
                'possible_unflagged_accuracy_min': None,
                'possible_unflagged_accuracy_max': None}
    low = max(0, correct - flagged)
    high = min(correct, clean)
    return {'unflagged_n': clean, 'possible_unflagged_correct_min': low,
            'possible_unflagged_correct_max': high,
            'possible_unflagged_accuracy_min': low / clean,
            'possible_unflagged_accuracy_max': high / clean}


def build_report(blocks):
    per_run, splits = audit_flags(blocks)
    flagged = splits['heldout_within_day']['artifact_flagged']
    return {
        'schema': 'wbi-a01t-artifact-flags-audit-v1.0',
        'source_file': 'A01T.mat', 'source_bytes': EXPECTED_BYTES,
        'source_sha256_observed_not_publisher_signed': EXPECTED_SHA256,
        'run_utc': datetime.now(timezone.utc).isoformat(),
        'github_sha': os.environ.get('GITHUB_SHA', 'TBD'),
        'numpy_version': np.__version__,
        'flag_semantics': 'source per-trial artifacts: 0=unflagged, 1=flagged',
        'task_runs': per_run, 'splits': splits,
        'frozen_v09_heldout_correct_all_trials': FROZEN_CORRECT,
        'frozen_v09_heldout_total_all_trials': TOTAL_HELDOUT,
        'unflagged_accuracy_identification_bounds_not_observed':
            accuracy_identification_bounds(TOTAL_HELDOUT, FROZEN_CORRECT, flagged),
        'v09_primary_all_trial_result_unchanged': True,
        'actual_artifact_free_decoder_score': 'TBD',
        'session_E_downloaded_or_labels_accessed': False,
        'trial_level_flags_or_labels_persisted': False,
        'clinical_or_safety_validation': False,
        'maturity': 'Research / Simulation, unchanged',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'refusing to overwrite existing evidence')
    report = build_report(load_training_runs(fetch_pinned_training_bytes()))
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n',
                           encoding='utf-8')
    print(json.dumps({'source_file': report['source_file'],
                      'splits': report['splits'],
                      'unflagged_accuracy_identification_bounds_not_observed':
                          report['unflagged_accuracy_identification_bounds_not_observed'],
                      'session_E_downloaded_or_labels_accessed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
