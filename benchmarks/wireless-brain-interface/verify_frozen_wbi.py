#!/usr/bin/env python3
"""Verify frozen synthetic WBI artifacts and deterministic execution; NOT real EEG validation."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

EXPECTED_SOURCE_GIT_BLOB = '2becec81a8002cc5ff2f445889b7617baf9937b9'
EXPECTED_CSV_SHA256 = '65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a'
EXPECTED_THRESHOLDS = (0.75, 0.70, 0.70)
EXPECTED_POLICIES = {
    'ungated': (1.0000, 0.3292, 1.0000, 0.1865, 0.1099),
    'confidence_abstention': (0.5125, 0.1301, 0.6646, 0.1865, 0.1099),
    'authorization_gate': (0.5833, 0.1571, 0.7329, 0.1865, 0.1099),
}
METRIC_NAMES = ('coverage', 'incorrect_action_risk', 'correct_action_retention', 'brier', 'ece')
THRESHOLD_RE = re.compile(r'^frozen thresholds: abstention_conf=([0-9.]+); gate_conf=([0-9.]+); gate_drift=([0-9.]+)$', re.M)

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_sources(source: Path, reference_csv: Path) -> dict:
    blob = git_blob_sha(source.read_bytes())
    digest = sha256(reference_csv.read_bytes())
    if blob != EXPECTED_SOURCE_GIT_BLOB:
        raise ValueError(f'FROZEN SOURCE CHANGED: {blob} != {EXPECTED_SOURCE_GIT_BLOB}')
    if digest != EXPECTED_CSV_SHA256:
        raise ValueError(f'PUBLISHED CSV CHANGED: {digest} != {EXPECTED_CSV_SHA256}')
    return {'source_git_blob': blob, 'reference_csv_sha256': digest}

def parse_stdout(output: str) -> dict:
    if 'SYNTHETIC ONLY — not EEG/clinical validation' not in output:
        raise ValueError('Missing synthetic-only warning')
    match = THRESHOLD_RE.search(output)
    if not match:
        raise ValueError('Missing frozen thresholds')
    thresholds = tuple(float(x) for x in match.groups())
    if thresholds != EXPECTED_THRESHOLDS:
        raise ValueError(f'Threshold drift: {thresholds}')
    policy_metrics = {}
    for line in output.splitlines():
        parts = line.split()
        if not parts or parts[0] not in EXPECTED_POLICIES:
            continue
        name = parts[0]
        values = {}
        for token in parts[1:]:
            k, v = token.split('=', 1)
            values[k] = float(v)
        if tuple(values) != METRIC_NAMES:
            raise ValueError(f'Metric set/order changed: {name} {tuple(values)}')
        actual = tuple(values[k] for k in METRIC_NAMES)
        if actual != EXPECTED_POLICIES[name]:
            raise ValueError(f'Synthetic reference metrics changed: {name} {actual}')
        policy_metrics[name] = values
    if set(policy_metrics) != set(EXPECTED_POLICIES):
        raise ValueError('Missing or extra policy results')
    return {'thresholds': thresholds, 'policies': policy_metrics}

def run_twice(source: Path) -> dict:
    outputs = []
    for _ in range(2):
        with tempfile.TemporaryDirectory(prefix='wbi_frozen_ci_') as td:
            target = Path(td) / 'synthetic_evaluator.py'
            shutil.copyfile(source, target)
            env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
            result = subprocess.run([sys.executable, '-B', str(target)], cwd=td, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=30, check=True)
            csv_path = Path(td) / 'synthetic_risk_coverage.csv'
            if not csv_path.is_file():
                raise ValueError('Evaluator did not emit CSV')
            csv_data = csv_path.read_bytes()
            if sha256(csv_data) != EXPECTED_CSV_SHA256:
                raise ValueError('Generated synthetic CSV differs from published reference')
            out = result.stdout.decode('utf-8')
            parsed = parse_stdout(out)
            outputs.append((result.stdout, csv_data, parsed))
    if outputs[0][:2] != outputs[1][:2]:
        raise ValueError('Two clean executions differ')
    return {'runs': 2, 'deterministic_stdout': True, 'deterministic_csv': True,
            'generated_csv_sha256': sha256(outputs[0][1]), **outputs[0][2]}

def verify(source: Path, reference_csv: Path) -> dict:
    return {'scope': 'SYNTHETIC REPRODUCIBILITY ONLY',
            'runtime': {'python': platform.python_version(), 'os': platform.system(),
                        'implementation': platform.python_implementation()},
            'integrity': validate_sources(source, reference_csv),
            'reproduction': run_twice(source),
            'real_eeg': 'TBD', 'cross_environment_ci': 'TBD until GitHub CI completes',
            'matched_coverage_gate_superiority': 'NOT ESTABLISHED'}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--json-out', type=Path, help='Optional output path outside the source directory')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    report = verify(folder/'synthetic_evaluator.py', folder/'synthetic_risk_coverage.csv')
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(encoded, encoding='utf-8')
    print('PASS: frozen synthetic source, published CSV, two clean deterministic runs')
    print('Python:', report['runtime']['python'], 'OS:', report['runtime']['os'])
    print('CSV SHA-256:', report['reproduction']['generated_csv_sha256'])
    print('No real EEG / clinical / performance superiority claim')

if __name__ == '__main__':
    main()
