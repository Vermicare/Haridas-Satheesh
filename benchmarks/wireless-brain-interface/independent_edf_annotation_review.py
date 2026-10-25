#!/usr/bin/env python3
"""Independent MNE EDF+ annotation agreement gate for ONE checksum-pinned training run.

Uses MNE's EDF+ reader separately from the project's byte-level TAL parser.
Does not load EEG waveforms, train a decoder, or access held-out subjects.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import platform

EXPECTED_EDF_SHA256 = '3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d'
LABELS = frozenset({'T0', 'T1', 'T2'})
EXPECTED_COUNTS = {'T0': 15, 'T1': 8, 'T2': 7}  # Previously observed; not a substitute for independent agreement.
TOLERANCE_S = 0.0001


class AgreementError(ValueError):
    """Independent annotation review failed closed."""


def _normalized(events: list[dict], reader: str) -> list[tuple[str, float, float]]:
    if not isinstance(events, list) or not events:
        raise AgreementError(f'{reader}: empty or invalid event list')
    result = []
    for event in events:
        if not isinstance(event, dict) or set(event) != {'label', 'onset_s', 'duration_s'}:
            raise AgreementError(f'{reader}: malformed event fields')
        label = event['label']
        onset, duration = event['onset_s'], event['duration_s']
        if label not in LABELS:
            raise AgreementError(f'{reader}: unknown event label')
        if type(onset) not in (float, int) or type(duration) not in (float, int):
            raise AgreementError(f'{reader}: nonnumeric event time')
        onset, duration = float(onset), float(duration)
        if not (math.isfinite(onset) and math.isfinite(duration)) or onset < 0 or duration <= 0:
            raise AgreementError(f'{reader}: invalid event timing')
        result.append((label, onset, duration))
    result.sort(key=lambda x: (x[1], x[0], x[2]))
    if len(result) != len(set(result)):
        raise AgreementError(f'{reader}: duplicate event')
    return result


def compare_events(tal_events: list[dict], independent_events: list[dict]) -> dict:
    """Compare every label, onset and duration; never equate matching counts with agreement."""
    a = _normalized(tal_events, 'TAL')
    b = _normalized(independent_events, 'independent reader')
    if len(a) != len(b):
        raise AgreementError(f'event count mismatch: TAL={len(a)} independent={len(b)}')
    ca, cb = dict(sorted(Counter(e[0] for e in a).items())), dict(sorted(Counter(e[0] for e in b).items()))
    if ca != cb:
        raise AgreementError(f'label-count mismatch: TAL={ca} independent={cb}')
    max_onset, max_duration = 0.0, 0.0
    for idx, (left, right) in enumerate(zip(a, b)):
        if left[0] != right[0]:
            raise AgreementError(f'label mismatch at sorted event {idx}')
        delta_onset, delta_duration = abs(left[1] - right[1]), abs(left[2] - right[2])
        if delta_onset > TOLERANCE_S or delta_duration > TOLERANCE_S:
            raise AgreementError(f'timing mismatch at sorted event {idx}: onset_delta={delta_onset:.9g}s duration_delta={delta_duration:.9g}s')
        max_onset = max(max_onset, delta_onset)
        max_duration = max(max_duration, delta_duration)
    canonical = json.dumps(a, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    return {'total_events': len(a), 'counts': ca,
            'max_onset_delta_s': max_onset, 'max_duration_delta_s': max_duration,
            'tolerance_s': TOLERANCE_S, 'tal_event_triples_sha256': hashlib.sha256(canonical).hexdigest()}


def review(edf_path: Path, checksum_index: Path) -> dict:
    from edf_annotation_contract import validate_and_summarize
    import mne

    data = edf_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_EDF_SHA256:
        raise AgreementError('source EDF digest does not match predeclared training-file SHA256')
    own = validate_and_summarize(data, checksum_index.read_text(encoding='ascii'))
    if own['annotations']['event_counts'] != EXPECTED_COUNTS:
        raise AgreementError('TAL count drift relative to previously verified pinned-source run')
    # MNE has an independent EDF+ TAL implementation; preload=False avoids EEG waveform loading.
    raw = mne.io.read_raw_edf(str(edf_path), preload=False, verbose='ERROR')
    if raw.preload:
        raise AgreementError('unexpected waveform preloading')
    if abs(float(raw.info['sfreq']) - 160.0) > 1e-9:
        raise AgreementError('unexpected sampling rate')
    independent = [
        {'label': str(label), 'onset_s': float(onset), 'duration_s': float(duration)}
        for label, onset, duration in zip(raw.annotations.description,
                                          raw.annotations.onset, raw.annotations.duration)
    ]
    matched = compare_events(own['annotations']['events'], independent)
    if matched['counts'] != EXPECTED_COUNTS:
        raise AgreementError('independent label counts differ from frozen preflight')
    return {
        'status': 'PASS_INDEPENDENT_EDF_ANNOTATION_AGREEMENT',
        'source': 'PhysioNet EEGMMIDB v1.0.0 S001/S001R04.edf (training only)',
        'source_sha256': EXPECTED_EDF_SHA256,
        'readers': ['project EDF+ TAL parser', 'MNE-Python independent EDF+ reader'],
        'mne_version': mne.__version__, 'python_version': platform.python_version(),
        'waveform_preloaded': False, 'decoder_trained': False, 'held_out_subjects_accessed': False,
        'real_eeg_decoding_accuracy': 'TBD', 'clinical_validation': False,
        'agreement': matched,
        'limitations': 'Two software parsers agree on one source recording; not independently annotated ground truth or EEG decoder validation.'
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--edf', required=True, type=Path)
    p.add_argument('--sha256-index', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    result = review(args.edf, args.sha256_index)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('INDEPENDENT EDF+ ANNOTATION AGREEMENT PASS:', result['agreement']['counts'],
          '(ONE TRAINING EDF; NO EEG DECODING)')


if __name__ == '__main__':
    main()
