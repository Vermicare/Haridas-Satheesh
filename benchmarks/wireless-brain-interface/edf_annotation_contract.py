#!/usr/bin/env python3
"""Metadata-only EDF+ TAL annotation preflight for one TRAIN imagery recording.

No EEG samples are decoded, no model is trained, and no held-out subjects are read.
Source integrity is delegated to the pinned edf_smoke.py verifier.
"""
from __future__ import annotations
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from edf_smoke import BASE, REL, MAX_BYTES, MAX_SUMS_BYTES, SmokeError, fetch, inspect_edf, verify

_NUMBER = re.compile(rb'[+-](?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?\Z')
_DURATION = re.compile(rb'(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?\Z')
_LABELS = {'T0': 'rest', 'T1': 'imagined_left_fist', 'T2': 'imagined_right_fist'}


def _number(raw: bytes, pattern: re.Pattern, field: str) -> float:
    raw = raw.strip()
    if not pattern.fullmatch(raw):
        raise SmokeError(f'invalid EDF+ {field}')
    value = float(raw)
    if not math.isfinite(value):
        raise SmokeError(f'nonfinite EDF+ {field}')
    return value


def parse_tal(chunk: bytes) -> tuple[float, float | None, list[str]]:
    """Parse one EDF+ time-stamped annotation list, not an EEG event classifier."""
    if b'\x14' not in chunk:
        raise SmokeError('TAL missing annotation separator')
    head, *texts = chunk.split(b'\x14')
    if b'\x15' in head:
        if head.count(b'\x15') != 1:
            raise SmokeError('TAL has ambiguous duration')
        onset_raw, duration_raw = head.split(b'\x15')
        duration = _number(duration_raw, _DURATION, 'duration')
        if duration <= 0:
            raise SmokeError('nonpositive EDF+ event duration')
    else:
        onset_raw, duration = head, None
    onset = _number(onset_raw, _NUMBER, 'onset')
    if onset < 0:
        raise SmokeError('negative EDF+ onset')
    if texts[-1] != b'':
        raise SmokeError('TAL missing final separator')
    labels = []
    for t in texts[:-1]:
        if not t:
            continue
        try:
            labels.append(t.decode('ascii', 'strict'))
        except UnicodeDecodeError as e:
            raise SmokeError('non-ASCII EDF+ annotation text') from e
    return onset, duration, labels


def extract_annotations(edf: bytes) -> dict:
    """Read only the EDF+ annotation channel; EEG samples remain opaque bytes."""
    meta = inspect_edf(edf)
    signals = 65
    header_bytes = meta['header_bytes']
    duration = meta['record_duration_s']
    records = meta['data_records']
    head = edf[:header_bytes]
    labels = [head[256 + 16 * i:256 + 16 * (i + 1)].decode('ascii').strip() for i in range(signals)]
    ann_indexes = [i for i, name in enumerate(labels) if 'annotations' in name.lower()]
    if len(ann_indexes) != 1:
        raise SmokeError('missing or ambiguous EDF+ annotations channel')
    ann = ann_indexes[0]
    sample_start = 256 + signals * (16 + 80 + 8 + 8 + 8 + 8 + 8 + 80)
    samples = [int(head[sample_start + i*8:sample_start + (i+1)*8].decode('ascii').strip()) for i in range(signals)]
    bytes_per_record = 2 * sum(samples)
    offset = 2 * sum(samples[:ann])
    annotation_size = 2 * samples[ann]
    events = []
    timekeeping_records = 0
    for record in range(records):
        begin = header_bytes + record * bytes_per_record + offset
        pair_bytes = edf[begin:begin + annotation_size]
        if len(pair_bytes) != annotation_size:
            raise SmokeError('truncated EDF+ annotation channel')
        if any(pair_bytes[i] != 0 for i in range(1, len(pair_bytes), 2)):
            raise SmokeError('unexpected EDF+ annotation high bytes')
        tal_bytes = pair_bytes[::2]
        found_clock = False
        for chunk in tal_bytes.split(b'\x00'):
            if not chunk:
                continue
            onset, event_duration, texts = parse_tal(chunk)
            if not texts:
                found_clock = True
                continue
            for label in texts:
                if label not in _LABELS:
                    raise SmokeError(f'unknown EDF+ task label {label!r}; stop rather than silently remap')
                if event_duration is None:
                    raise SmokeError('task event missing duration')
                if onset + event_duration > records * duration + 1e-6:
                    raise SmokeError('task event exceeds recording duration')
                events.append({'label': label, 'onset_s': onset, 'duration_s': event_duration})
        if found_clock:
            timekeeping_records += 1
    if not events:
        raise SmokeError('no task events found')
    if any(events[i]['onset_s'] < events[i-1]['onset_s'] for i in range(1,len(events))):
        raise SmokeError('task events not ordered by onset')
    counts = dict(sorted(Counter(x['label'] for x in events).items()))
    return {'event_counts': counts, 'total_events': len(events), 'timekeeping_records': timekeeping_records,
            'task_map': _LABELS, 'recording_duration_s': records * duration,
            'events': events, 'raw_eeg_samples_decoded': False}


def validate_and_summarize(edf: bytes, checksum_index: str) -> dict:
    base = verify(edf, checksum_index)
    if (base['subject'], base['run'], base['subject_split']) != ('S001', 'R04', 'train'):
        raise SmokeError('not pinned training file')
    ann = extract_annotations(edf)
    return {'status': 'REAL_EDF_ANNOTATION_PREFLIGHT_ONLY', 'source_sha256': base['source_sha256'],
            'source_url': BASE + REL, 'publisher_checksum_matches': True,
            'split': 'train', 'run': 'R04', 'mapping_applies_only_to_runs': ['R04', 'R08', 'R12'],
            'annotations': ann, 'decoder_trained': False, 'test_subjects_accessed': False,
            'accuracy': 'TBD', 'drift_validation': 'TBD', 'clinical_validation': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fetch', action='store_true')
    p.add_argument('--edf', type=Path)
    p.add_argument('--sha256-index', type=Path)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.fetch and (a.edf or a.sha256_index):
        p.error('use --fetch OR --edf plus --sha256-index')
    if not a.fetch and (not a.edf or not a.sha256_index):
        p.error('both local paths are required without --fetch')
    if a.fetch:
        edf = fetch(BASE + REL, MAX_BYTES)
        index = fetch(BASE + 'SHA256SUMS.txt', MAX_SUMS_BYTES).decode('ascii')
    else:
        edf = a.edf.read_bytes()
        index = a.sha256_index.read_text(encoding='ascii')
    result = validate_and_summarize(edf, index)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print('EDF+ TRAIN ANNOTATION PREFLIGHT ONLY:', result['annotations']['event_counts'],
          'NO EEG DECODING / NO HELD-OUT ACCESS')


if __name__ == '__main__':
    main()
