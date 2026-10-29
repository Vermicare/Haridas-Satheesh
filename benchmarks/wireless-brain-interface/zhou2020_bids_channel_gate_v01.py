#!/usr/bin/env python3
"""Read-only channel-provenance gate for NEMAR nm000237 BIDS v1.1.0.

This inspects metadata only. It does not open EEG signals or held-out labels.
The channel-order contract is specific to the corrected NEMAR BIDS export,
not a universal contract for all Zhou2020 distributions.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

COMMON = 'F3 F1 Fz F2 F4 FC5 FC3 FC1 FCz FC2 FC4 FC6 C5 C3 C1 Cz C2 C4 C6 CP5 CP3 CP1 CPz CP2 CP4 CP6'.split()
EXTRA = 'F5 AF3 AF4 P5 P3 P1 Pz P2 P4 P6 PO3 POz PO4 Oz F6'.split()
SUBJECT_RE = re.compile(r'^sub-(\d+)_')


def inspect_text(version_json: str, channels_tsv: str, filename: str):
    """Validate one channels.tsv against declared corrected-export metadata."""
    meta = json.loads(version_json)
    if not isinstance(meta, dict) or meta.get('Version') != '1.1.0':
        raise ValueError('NEMAR dataset Version must equal 1.1.0; reject older/unknown exports')
    if meta.get('DatasetType') != 'derivative':
        raise ValueError('Expected NEMAR BIDS derivative, not original NPZ or other dataset')
    match = SUBJECT_RE.match(Path(filename).name)
    if not match or not filename.endswith('_channels.tsv'):
        raise ValueError('Expected sub-N_..._channels.tsv')
    subject = int(match.group(1))
    if not 1 <= subject <= 20:
        raise ValueError('Subject outside documented cohort 1..20')
    rows = list(csv.DictReader(io.StringIO(channels_tsv), delimiter='\t'))
    if not rows or not {'name', 'type', 'sampling_frequency'} <= set(rows[0]):
        raise ValueError('Missing required BIDS channels.tsv fields')
    if any(not r['name'] or not r['type'] for r in rows):
        raise ValueError('Missing channel name or type')
    names = [r['name'] for r in rows]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate channel name')
    expected = ([(n, 'EEG') for n in COMMON + EXTRA] +
                [('hEOG', 'EOG'), ('vEOG', 'EOG'), ('M1', 'MISC'), ('M2', 'MISC')]
                if subject <= 12 else
                [(n, 'EEG') for n in COMMON] + [('hEOG', 'EOG'), ('vEOG', 'EOG')])
    observed = [(r['name'], r['type']) for r in rows]
    if observed != expected:
        raise ValueError('Channel name/type/order mismatch: reject legacy generic EEG, EOG-as-EEG, or missing electrodes')
    if any(float(r['sampling_frequency']) != 500.0 for r in rows):
        raise ValueError('Unexpected channel sampling frequency')
    return {'subject': subject, 'channels': len(rows), 'eeg': 41 if subject <= 12 else 26,
            'eog': 2, 'misc': 2 if subject <= 12 else 0,
            'sha256_channels_tsv': hashlib.sha256(channels_tsv.encode()).hexdigest(),
            'status': 'METADATA_CONTRACT_PASS_NOT_SIGNAL_VALIDATION'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bids_root', type=Path, help='local NEMAR nm000237 BIDS v1.1.0 root')
    args = parser.parse_args()
    root = args.bids_root
    version_path = root / 'dataset_description.json'
    if not version_path.is_file():
        parser.error('Missing dataset_description.json; fail closed')
    version = version_path.read_text(encoding='utf-8-sig')
    files = sorted(root.glob('sub-*/ses-*/eeg/*_channels.tsv'))
    if not files:
        parser.error('No channels.tsv files; fail closed')
    results = []
    for file in files:
        try:
            results.append(inspect_text(version, file.read_text(encoding='utf-8-sig'), file.name))
        except (ValueError, KeyError, TypeError) as exc:
            parser.error(f'{file.relative_to(root)}: {exc}')
    print(json.dumps({'status': 'PASS_METADATA_ONLY', 'dataset_version': '1.1.0',
                      'files_checked': len(results), 'subjects_seen': sorted({r['subject'] for r in results}),
                      'files': results, 'held_out_labels_accessed': False,
                      'physical_or_clinical_validation': False}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
