#!/usr/bin/env python3
"""Independently reacquire the public A04T *training* source; metadata only.

Checks the exact previously observed response fingerprint before parsing. It
never persists EEG samples or class labels, and is not publisher attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_BYTES = 37_150_377
EXPECTED_SHA256 = '15850d81b95fc88cc8b9589eb9b713d49fa071e28adaf32d675b3eaa30591d6e'


class ReacquisitionError(ValueError):
    pass


def verify_reacquisition(raw: bytes, inspect, *, expected_size=EXPECTED_BYTES,
                         expected_sha256=EXPECTED_SHA256) -> dict:
    """Check independently acquired bytes, then the existing label-safe inspector.

    expected_* parameters support tiny fictional regression fixtures only; the
    command-line entrypoint does not expose them.
    """
    if type(raw) is not bytes or len(raw) != expected_size:
        raise ReacquisitionError('training source byte count differs from pinned observation')
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ReacquisitionError('training source SHA-256 differs from pinned observation')
    report = inspect(raw)
    if type(report) is not dict:
        raise ReacquisitionError('inspector returned invalid report')
    expected = {
        'file': 'A04T.mat', 'source_sha256': digest, 'source_bytes': len(raw),
        'blocks': 7, 'cue_free_baseline_blocks': 1, 'cued_task_blocks': 6,
        'cues_total': 288, 'sha256_is_provider_authenticated': False,
        'class_label_values_inspected': False, 'raw_eeg_persisted_or_uploaded': False,
        'evaluation_session_or_labels_accessed': False,
        'a04t_eog_exception_allowed': True,
        'decode_accuracy': 'TBD', 'false_action_risk': 'TBD',
    }
    for key, value in expected.items():
        if type(report.get(key)) is not type(value) or report[key] != value:
            raise ReacquisitionError('inspector metadata mismatch: ' + key)
    return {
        'schema_version': 'wbi-a04t-independent-reacquisition-v06',
        'file': 'A04T.mat', 'training_only': True,
        'source_bytes': len(raw), 'source_sha256': digest,
        'previous_observation_sha256_matched': True,
        'blocks': 7, 'cue_free_baseline_blocks': 1,
        'cued_task_blocks': 6, 'cues_total': 288,
        'raw_eeg_persisted_or_uploaded': False,
        'class_label_values_inspected': False,
        'evaluation_session_or_labels_accessed': False,
        'publisher_signature_authenticated': False,
        'decoder_or_authorization_performance': 'TBD',
        'maturity_advanced': False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, help='new metadata-only JSON file')
    args = p.parse_args()
    target = Path(args.output)
    if target.exists():
        p.error('refusing to overwrite an evidence file')
    # Import only after validating CLI; existing inspector handles allowlisted
    # HTTPS redirects and a strict bounded-size source download.
    from bnci_a04t_exception_v05 import fetch_bytes, inspect_training_bytes
    result = verify_reacquisition(fetch_bytes(), inspect_training_bytes)
    target.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n',
                      encoding='utf-8')
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
