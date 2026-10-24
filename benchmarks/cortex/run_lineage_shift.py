#!/usr/bin/env python3
"""Fictional baseline transfer stress; never interpret as real extraction accuracy."""
import json
from pathlib import Path
from baseline import baseline
from evaluator import evaluate
from fixture_integrity_preflight import audit_fixture
from lineage_and_shift import audit_archive

ROOT = Path(__file__).resolve().parent
KINDS = ('decisions','actions','risks','dependencies','conditional_followups')


def report():
    cases = {}
    for label, path in [('frozen', 'fixture.json'),
                        ('independent_fictional', 'independent_scenario_v03.json')]:
        f = json.loads((ROOT / path).read_text(encoding='utf-8'))
        predicted = baseline(f)
        scored = evaluate(f, predicted)
        cases[label] = {
            'fixture': path,
            'benchmark': f['benchmark'],
            'data_origin': 'AUTHOR_CREATED_FICTIONAL_ONLY',
            'predicted_counts': {k: len(predicted[k]) for k in KINDS},
            'ground_truth_counts': {k: len(f['ground_truth'][k]) for k in KINDS},
            'exact_signature_f1': {k: scored['metrics'][k]['f1'] for k in KINDS},
            'legacy_lineage_score': scored['metrics']['decision_reversal_lineage_accuracy'],
            'fixture_preflight_codes': audit_fixture(f),
            'archive_reference_codes': audit_archive(f),
            'archive_authenticity_verified': False,
            'semantic_ground_truth_reviewed_by_humans': False,
            'human_correction_minutes': 'TBD',
        }
    return {'experiment':'cortex-frozen-vs-fictional-shift-20261024',
            'source':'existing public v0.1 baseline and evaluator, plus additive PR #4 preflight',
            'method':'frozen exact-match baseline on original and author-created independent fictional scenario',
            'cases': cases,
            'stage_change': 'NONE',
            'real_workflow_results': 'TBD',
            'interpretation':'Hardcoded frozen-only baseline fails to transfer; no claim about a general CORTEX model.'}


def main():
    out = json.dumps(report(), sort_keys=True, indent=2, ensure_ascii=False) + '\n'
    (ROOT / 'synthetic_lineage_shift_results.json').write_bytes(out.encode('utf-8'))
    print(out, end='')

if __name__ == '__main__':
    main()
