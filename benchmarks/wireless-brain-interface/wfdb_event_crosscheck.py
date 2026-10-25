#!/usr/bin/env python3
"""Checksum-gated, one-record WFDB .event versus EDF+ TAL annotation comparison.

No waveform decoding, model training, held-out access or clinical inference.
WFDB annotation sample times are quantized; auxiliary-note durations are compared.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import operator
from pathlib import Path
import platform
import re

from edf_annotation_contract import validate_and_summarize
from edf_smoke import checksum_from_index

REL_EVENT = 'S001/S001R04.edf.event'
EXPECTED_EDF = '3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d'
EXPECTED_COUNTS = {'T0': 15, 'T1': 8, 'T2': 7}
FS = 160
TOLERANCE_S = 1 / FS + 1e-9


class CrossFormatError(ValueError):
    pass


def verify_event_digest(event_bytes: bytes, index: str) -> str:
    if not 0 < len(event_bytes) <= 65536:
        raise CrossFormatError('empty or oversized companion annotation file')
    expected = checksum_from_index(index, REL_EVENT)
    actual = hashlib.sha256(event_bytes).hexdigest()
    if actual != expected:
        raise CrossFormatError('companion annotation SHA256 mismatch against publisher index')
    return actual


def wfdb_events(annotation: object) -> list[tuple[str, int, float]]:
    """Parse exact publisher WFDB auxiliary-note form: 'T1 duration: 4.1'."""
    samples = list(annotation.sample)
    notes = list(annotation.aux_note)
    symbols = list(annotation.symbol)
    if not samples or not (len(samples) == len(notes) == len(symbols)):
        raise CrossFormatError('invalid WFDB annotation arrays')
    result = []
    for event_index, (sample, note, symbol) in enumerate(zip(samples, notes, symbols)):
        if isinstance(sample, bool):
            raise CrossFormatError('noninteger WFDB sample index')
        try:
            sample = operator.index(sample)
        except TypeError as exc:
            raise CrossFormatError('noninteger WFDB sample index') from exc
        if sample < 0:
            raise CrossFormatError('negative WFDB sample index')
        match = re.fullmatch(r'(T[012]) duration: ([0-9]+(?:\.[0-9]+)?)', note.strip()) if isinstance(note, str) else None
        if match is None:
            raise CrossFormatError(f'unknown or ambiguous WFDB event label/duration at {event_index}: '
                                   f'aux_note={str(note)[:64]!r}, symbol={str(symbol)[:32]!r}')
        label, duration = match.group(1), float(match.group(2))
        if not math.isfinite(duration) or duration <= 0:
            raise CrossFormatError('nonpositive or nonfinite WFDB duration')
        result.append((label, sample, duration))
    if len(result) != len(set(result)) or any(b[1] < a[1] for a, b in zip(result, result[1:])):
        raise CrossFormatError('duplicate or out-of-order WFDB events')
    return result


def compare_tal_to_wfdb(tal: list[dict], events: list[tuple[str, int, float]]) -> dict:
    if len(tal) != len(events):
        raise CrossFormatError(f'event count mismatch: TAL={len(tal)}, WFDB={len(events)}; '
                               f'TAL_counts={dict(Counter(t["label"] for t in tal))}; '
                               f'WFDB_counts={dict(Counter(e[0] for e in events))}; '
                               f'TAL_first_last={(tal[0] if tal else None, tal[-1] if tal else None)}; '
                               f'WFDB_first_last={(events[0] if events else None, events[-1] if events else None)}')
    if len(events) != 30:
        raise CrossFormatError('pinned recording event count differs from 30')
    counts = dict(sorted(Counter(label for label, _, _ in events).items()))
    if counts != EXPECTED_COUNTS:
        raise CrossFormatError(f'WFDB label counts differ: {counts}')
    if dict(sorted(Counter(t['label'] for t in tal).items())) != EXPECTED_COUNTS:
        raise CrossFormatError('TAL label counts differ from frozen training run')
    max_onset, max_duration = 0.0, 0.0
    for i, (source, (label, sample, duration)) in enumerate(zip(tal, events)):
        if source['label'] != label:
            raise CrossFormatError(f'cross-format label mismatch at event {i}')
        onset, tal_duration = source['onset_s'], source['duration_s']
        if any(type(v) not in (float, int) or not math.isfinite(v) or v < 0 for v in (onset, tal_duration)):
            raise CrossFormatError('invalid TAL timing')
        delta = abs(onset - sample / FS)
        if delta > TOLERANCE_S:
            raise CrossFormatError(f'cross-format onset mismatch at event {i}: delta={delta:.9g}s')
        delta_duration = abs(tal_duration - duration)
        if delta_duration > 1e-6:
            raise CrossFormatError(f'cross-format duration mismatch at event {i}: delta={delta_duration:.9g}s')
        max_onset = max(max_onset, delta)
        max_duration = max(max_duration, delta_duration)
    return {'total_events': 30, 'counts': counts, 'max_onset_delta_s': max_onset,
            'max_duration_delta_s': max_duration,
            'onset_tolerance_s': TOLERANCE_S, 'duration_tolerance_s': 1e-6,
            'duration_source': 'WFDB auxiliary-note duration text (encoding discovered in first failed CI run)'}


def review(edf_path: Path, event_path: Path, index_path: Path) -> dict:
    import wfdb
    index = index_path.read_text(encoding='ascii')
    edf = edf_path.read_bytes()
    if hashlib.sha256(edf).hexdigest() != EXPECTED_EDF:
        raise CrossFormatError('EDF differs from pinned training-file SHA256')
    own = validate_and_summarize(edf, index)
    event_sha = verify_event_digest(event_path.read_bytes(), index)
    if event_path.name != 'S001R04.edf.event':
        raise CrossFormatError('companion annotation filename must be S001R04.edf.event')
    # Official WFDB reader parses the binary MIT-format .event file.
    ann = wfdb.rdann(str(event_path.with_suffix('')), 'event', return_label_elements=['symbol'])
    events = wfdb_events(ann)
    agreement = compare_tal_to_wfdb(own['annotations']['events'], events)
    canonical = json.dumps(events, separators=(',', ':')).encode('ascii')
    return {'status': 'PASS_SINGLE_TRAIN_CROSS_FORMAT_ANNOTATION',
            'source': 'PhysioNet EEGMMIDB v1.0.0 S001/S001R04.edf (train only)',
            'edf_sha256': EXPECTED_EDF, 'event_sha256': event_sha,
            'wfdb_version': wfdb.__version__, 'python_version': platform.python_version(),
            'wfdb_event_pairs_sha256': hashlib.sha256(canonical).hexdigest(),
            'agreement': agreement, 'decoder_trained': False, 'held_out_subjects_accessed': False,
            'real_eeg_decoding_accuracy': 'TBD', 'clinical_validation': False,
            'limitations': 'One source recording; WFDB sample onsets versus EDF+ TAL onsets only. Duration text is cross-checked; independent human labels remain unvalidated.'}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--edf', type=Path, required=True)
    p.add_argument('--event', type=Path, required=True)
    p.add_argument('--sha256-index', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    try:
        result = review(a.edf, a.event, a.sha256_index)
    except Exception as exc:
        result = {'status': 'FAIL_CROSS_FORMAT_REVIEW', 'error_type': type(exc).__name__,
                  'reason': str(exc)[:300], 'real_eeg_decoding_accuracy': 'TBD'}
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(result['status'], result.get('agreement', result.get('reason')))
    if result['status'] != 'PASS_SINGLE_TRAIN_CROSS_FORMAT_ANNOTATION':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
