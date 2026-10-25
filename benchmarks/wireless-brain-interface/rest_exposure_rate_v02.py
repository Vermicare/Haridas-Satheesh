#!/usr/bin/env python3
"""Fictional WBI rest-exposure accounting, not EEG decoding or safety validation.

All intervals and action timestamps are in integer sample coordinates, and
segments partition a single recording exactly. No event segmentation heuristic
is used as the denominator. This deliberately does not infer missing labels.
"""
from __future__ import annotations
from dataclasses import dataclass
import json

LABELS = frozenset(("T0", "T1", "T2"))
POLICIES = ("ungated", "abstention", "gate")

@dataclass(frozen=True)
class Recording:
    sample_rate_hz: int
    n_samples: int

@dataclass(frozen=True)
class Segment:
    start: int
    end: int  # exclusive
    label: str

@dataclass(frozen=True)
class Action:
    sample: int
    policy: str
    direction: str


def _positive_int(x):
    return type(x) is int and x > 0


def _nonnegative_int(x):
    return type(x) is int and x >= 0


def validate(recording: Recording, segments, actions):
    if not isinstance(recording, Recording) or not _positive_int(recording.sample_rate_hz) or not _positive_int(recording.n_samples):
        raise ValueError("invalid recording metadata")
    segments = tuple(segments)
    actions = tuple(actions)
    if not segments:
        raise ValueError("missing annotation segments")
    expected = 0
    counts = {label: 0 for label in LABELS}
    for s in segments:
        if not isinstance(s, Segment) or not _nonnegative_int(s.start) or not _positive_int(s.end) or s.end <= s.start:
            raise ValueError("invalid segment interval")
        if s.label not in LABELS:
            raise ValueError("unknown annotation label")
        if s.start != expected:
            raise ValueError("annotation gap, overlap or unordered interval")
        expected = s.end
        counts[s.label] += s.end - s.start
    if expected != recording.n_samples:
        raise ValueError("annotation coverage does not match recording length")
    if counts["T0"] == 0 or counts["T1"] + counts["T2"] == 0:
        raise ValueError("missing rest or imagery exposure")
    seen = set()
    for a in actions:
        if not isinstance(a, Action) or not _nonnegative_int(a.sample) or a.sample >= recording.n_samples:
            raise ValueError("invalid action sample")
        if a.policy not in POLICIES or a.direction not in ("T1", "T2"):
            raise ValueError("invalid action policy or direction")
        key = (a.policy, a.sample)
        if key in seen:
            raise ValueError("duplicate policy action at sample")
        seen.add(key)
    return segments, actions, counts


def evaluate(recording: Recording, segments, actions):
    segments, actions, counts = validate(recording, segments, actions)
    # One annotation interval lookup per action. All intervals are half-open.
    action_labels = []
    for a in actions:
        label = next(s.label for s in segments if s.start <= a.sample < s.end)
        action_labels.append((a, label))
    result = {}
    for policy in POLICIES:
        selected = [(a, label) for a, label in action_labels if a.policy == policy]
        rest_actions = sum(label == "T0" for _, label in selected)
        imagery_actions = len(selected) - rest_actions
        # Exact numerator/denominator are preserved to prevent hidden rounding.
        numerator = rest_actions * recording.sample_rate_hz * 60
        denominator = counts["T0"]
        result[policy] = {
            "rest_actions": rest_actions,
            "imagery_actions": imagery_actions,
            "rest_exposure_samples": denominator,
            "rest_actions_per_minute": round(numerator / denominator, 6),
            "rest_rate_exact_numerator": numerator,
            "rest_rate_exact_denominator": denominator,
        }
    return {
        "evidence_class": "FICTIONAL_TIMESTAMP_CONTRACT_ONLY",
        "sample_rate_hz": recording.sample_rate_hz,
        "n_samples": recording.n_samples,
        "rest_samples": counts["T0"],
        "imagery_samples": counts["T1"] + counts["T2"],
        "policies": result,
        "real_eeg_evaluated": False,
        "decoder_trained": False,
        "limitations": "Fictional action timestamps; no actual EEG decoding, continuous detector, matched coverage, or measured safety.",
    }


def demo():
    rec = Recording(sample_rate_hz=100, n_samples=6000)
    seg = (Segment(0, 2000, "T0"), Segment(2000, 4000, "T1"), Segment(4000, 6000, "T0"))
    acts = (Action(0, "ungated", "T1"), Action(1999, "ungated", "T2"),
            Action(2000, "ungated", "T1"), Action(5999, "ungated", "T1"),
            Action(2000, "abstention", "T1"), Action(3999, "gate", "T2"))
    return json.dumps(evaluate(rec, seg, acts), sort_keys=True, indent=2, allow_nan=False) + "\n"


if __name__ == "__main__":
    print(demo(), end="")
