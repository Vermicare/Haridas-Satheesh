#!/usr/bin/env python3
"""Paired subject-level WBI policy comparison (fictional contract, not EEG)."""
from __future__ import annotations
from dataclasses import dataclass
from math import fsum, isfinite
import json
import re
from matched_opportunity_contract_v03 import evaluate


@dataclass(frozen=True)
class SubjectTrial:
    subject_id: str
    recording: object
    segments: object
    opportunities: object
    decisions: object


def aggregate(trials, *, tolerance=0.05, minimum_subjects=3):
    """Require matched coverage for *every* subject; never silently select only winners.

    Inputs are explicitly fictional. Subject-level mean is descriptive only.
    The upstream v0.3 evaluator checks complete common opportunity grids.
    """
    if type(tolerance) not in (int, float) or not isfinite(tolerance) or not 0 <= tolerance <= 1:
        raise ValueError('invalid predeclared coverage tolerance')
    if type(minimum_subjects) is not int or minimum_subjects < 1:
        raise ValueError('invalid minimum subjects')
    trials = tuple(trials)
    if not trials:
        raise ValueError('no subject trials')
    rows = []
    seen = set()
    for trial in trials:
        if not isinstance(trial, SubjectTrial) or not isinstance(trial.subject_id, str) or not re.fullmatch(r'F\d{3}', trial.subject_id):
            raise ValueError('fictional subject identifier required (F###)')
        if trial.subject_id in seen:
            raise ValueError('duplicate subject')
        seen.add(trial.subject_id)
        report = evaluate(trial.recording, trial.segments, trial.opportunities,
                          trial.decisions, coverage_tolerance=tolerance)
        if report.get('real_eeg_evaluated') is not False or report.get('decoder_trained') is not False:
            raise ValueError('unexpected non-fictional evidence claim')
        a, b = report['policies']['abstention'], report['policies']['gate']
        rows.append({
            'subject_id': trial.subject_id,
            'comparable': report['comparison']['comparable'],
            'imagery_coverage_gap': report['comparison']['imagery_coverage_gap'],
            'risk_delta': report['comparison']['gate_minus_abstention_incorrect_action_risk'],
            'rest_rate_delta_per_minute': b['rest_false_actions_per_minute'] - a['rest_false_actions_per_minute'],
            'correct_action_recall_delta': b['correct_action_recall'] - a['correct_action_recall'],
        })
    rows.sort(key=lambda row: row['subject_id'])
    enough = len(rows) >= minimum_subjects
    all_matched = all(row['comparable'] for row in rows)
    mean = fsum(row['risk_delta'] for row in rows) / len(rows) if enough and all_matched else None
    rest_regression = any(row['rest_rate_delta_per_minute'] > 1e-9 for row in rows)
    recall_regression = any(row['correct_action_recall_delta'] < -1e-9 for row in rows)
    status = ('WITHHELD_INSUFFICIENT_SUBJECTS' if not enough else
              'WITHHELD_UNMATCHED_SUBJECT' if not all_matched else
              'DIAGNOSTIC_TRADEOFF' if rest_regression or recall_regression else
              'DIAGNOSTIC_ONLY')
    return {
        'evidence_class': 'FICTIONAL_SUBJECT_LEVEL_CONTRACT_ONLY',
        'subjects': rows, 'subject_count': len(rows),
        'minimum_subjects': minimum_subjects,
        'predeclared_coverage_tolerance': tolerance,
        'all_subjects_comparable': all_matched,
        'incomparable_subjects': sum(not row['comparable'] for row in rows),
        'unweighted_subject_mean_risk_delta': mean,
        'any_rest_false_action_rate_regression': rest_regression,
        'any_correct_action_recall_regression': recall_regression,
        'decision': status,
        'real_eeg_evaluated': False, 'decoder_trained': False,
        'limitations': 'Fictional repeated scenarios, not independent real EEG subjects, confidence intervals, safety or gate efficacy.',
    }


def demo():
    from rest_exposure_rate_v02 import Recording, Segment
    from matched_opportunity_contract_v03 import Decision
    rec = Recording(100, 6000)
    segments = (Segment(0, 2000, 'T0'), Segment(2000, 4000, 'T1'), Segment(4000, 6000, 'T0'))
    stamps = (0, 1000, 2000, 3000, 4000, 5000)
    trials = []
    for n in (1, 2, 3):
        choices = []
        for policy in ('ungated', 'abstention', 'gate'):
            for sample in stamps:
                direction = 'T1' if sample == 2000 else None
                if n == 3 and policy == 'gate':
                    direction = None  # Deliberate zero-action negative control.
                choices.append(Decision(sample, policy, direction))
        trials.append(SubjectTrial(f'F{n:03d}', rec, segments, stamps, tuple(choices)))
    return json.dumps(aggregate(trials), sort_keys=True, indent=2, allow_nan=False) + '\n'


if __name__ == '__main__':
    print(demo(), end='')
