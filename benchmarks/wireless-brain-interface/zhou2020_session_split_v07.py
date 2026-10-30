"""Deterministic metadata-only candidate session split from pinned Zhou2020 v0.5 census.

Does not access EEG recordings, event TSV contents, trial labels or predictions.
Session *index* is used for ordering; acquisition chronology is NOT verified.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

PINNED_CENSUS_SHA256 = 'b891a3edfd8b1c535bc50032f7d46717de4f45d0eddbfd500f06430e757ec6b1'
PINNED_REF = 'a291ed8a2afab3f93b85a540134dceb98092fcaf'
PATH = re.compile(r'^sub-(?P<subject>\d+)/ses-(?P<session>\d+)/eeg/sub-(?P=subject)_ses-(?P=session)_task-imagery_run-(?P<run>\d+)_events\.tsv$')


def assign(records):
    """Allocate by session index ONLY; counts, trial labels and model scores unused."""
    if not isinstance(records, list) or not records:
        raise ValueError('missing_records')
    groups = defaultdict(list)
    seen = set()
    for rec in records:
        if not isinstance(rec, dict):
            raise ValueError('invalid_record')
        s, ses, path = rec.get('subject'), rec.get('session'), rec.get('path')
        if type(s) is not int or not 1 <= s <= 20 or type(ses) is not int or not 0 <= ses <= 6 or not isinstance(path, str):
            raise ValueError('invalid_subject_session_path')
        match = PATH.fullmatch(path)
        if match is None or (int(match['subject']), int(match['session'])) != (s, ses):
            raise ValueError('path_metadata_mismatch')
        run = int(match['run'])
        key = (s, ses, run)
        if key in seen:
            raise ValueError('duplicate_subject_session_run')
        seen.add(key)
        blob = rec.get('git_blob_sha1')
        if not isinstance(blob, str) or not re.fullmatch('[0-9a-f]{40}', blob):
            raise ValueError('invalid_source_blob')
        groups[s].append((ses, run, path, blob))
    if set(groups) != set(range(1,21)):
        raise ValueError('missing_subject')
    result = []
    allocations = {}
    for subject in sorted(groups):
        sessions = sorted({ses for ses, *_ in groups[subject]})
        if len(sessions) < 3:
            raise ValueError('insufficient_sessions')
        calibration, test = sessions[-2:]
        allocations[str(subject)] = {'train_session_indices': sessions[:-2],
                                     'calibration_session_index': calibration,
                                     'candidate_test_session_index': test}
        for ses, run, path, blob in groups[subject]:
            role = 'test_candidate' if ses == test else ('calibration' if ses == calibration else 'train')
            result.append({'subject': subject, 'session_index': ses, 'run_index': run,
                           'role': role, 'event_tsv_path': path, 'event_tsv_git_blob_sha1': blob})
    result.sort(key=lambda r:(r['subject'],r['session_index'],r['run_index']))
    return result, allocations


def build(census):
    if not isinstance(census, dict) or census.get('schema') != 'ZHOU2020_EVENT_ROW_CENSUS_V05' or census.get('pinned_source_ref') != PINNED_REF:
        raise ValueError('source_schema_or_ref_mismatch')
    from zhou2020_event_concentration_v06 import analyze
    checked = analyze(census)
    entries, allocations = assign(census['file_provenance'])
    if len(entries) != 833 or checked['structural_event_rows'] != 33534:
        raise ValueError('unexpected_source_census')
    counts = Counter(x['role'] for x in entries)
    if counts['train'] + counts['calibration'] + counts['test_candidate'] != 833:
        raise ValueError('split_count_mismatch')
    return {'schema':'ZHOU2020_SESSION_INDEX_SPLIT_CANDIDATE_V07',
            'input_census_sha256': PINNED_CENSUS_SHA256,
            'upstream_git_ref': PINNED_REF,
            'selection_basis':'subject and session index only; last available session index test candidate, preceding calibration, earlier train',
            'chronological_acquisition_dates_verified':False,
            'original_npz_bytes_verified':False,
            'event_to_npz_pairing_verified':False,
            'earlier_exploratory_event_label_preview_disclosed':True,
            'heldout_outcomes_accessed_by_this_program':False,
            'candidate_not_confirmatory':True,
            'role_file_counts':dict(sorted(counts.items())),
            'subject_allocations':allocations,
            'entries':entries,
            'maturity_advanced':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census_json',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    raw=args.census_json.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINNED_CENSUS_SHA256:
        raise SystemExit('FAIL: v0.5 source JSON byte hash mismatch')
    result=build(json.loads(raw))
    payload=(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
    if args.output:
        args.output.write_bytes(payload)
    else:
        print(payload.decode(),end='')

if __name__=='__main__':main()
