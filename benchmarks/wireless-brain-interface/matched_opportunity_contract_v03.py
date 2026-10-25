#!/usr/bin/env python3
"""Fictional WBI matched-opportunity action safety contract; no EEG decoding.

Additive to v0.2: all three policies must make an explicit act/abstain
choice at each identical timestamp. Annotation labels are evaluation-only.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from rest_exposure_rate_v02 import Recording, Segment, POLICIES, validate as validate_annotations


@dataclass(frozen=True)
class Decision:
    sample: int
    policy: str
    direction: str | None  # None means abstain; T1/T2 means action.


def _integer_sample(x: object, length: int) -> bool:
    return type(x) is int and 0 <= x < length


def evaluate(recording: Recording, segments, opportunities, decisions,
             coverage_tolerance: float = 0.05) -> dict:
    """Compare only policies evaluated at the same declared opportunities.

    The tolerance is predeclared by the caller; no threshold is selected here.
    An unmatched coverage comparison reports no risk delta.
    """
    segments, _, exposure = validate_annotations(recording, segments, ())
    if type(coverage_tolerance) not in (float, int) or not 0 <= coverage_tolerance <= 1:
        raise ValueError("invalid coverage tolerance")
    stamps = tuple(opportunities)
    if not stamps or any(not _integer_sample(s, recording.n_samples) for s in stamps):
        raise ValueError("invalid or missing opportunity samples")
    if any(left >= right for left, right in zip(stamps, stamps[1:])):
        raise ValueError("opportunities must be strictly increasing and unique")
    expected = {(policy, sample) for policy in POLICIES for sample in stamps}
    choices = {}
    for d in decisions:
        if not isinstance(d, Decision) or d.policy not in POLICIES or d.direction not in (None, "T1", "T2"):
            raise ValueError("invalid decision policy or direction")
        if not _integer_sample(d.sample, recording.n_samples):
            raise ValueError("invalid decision sample")
        key = (d.policy, d.sample)
        if key not in expected:
            raise ValueError("decision outside declared opportunity grid")
        if key in choices:
            raise ValueError("duplicate decision for policy and sample")
        choices[key] = d.direction
    if set(choices) != expected:
        raise ValueError("incomplete policy decision grid")

    # A single common evaluation-only label per opportunity; labels are never
    # used to generate or select policy decisions in this function.
    labels = {}
    interval_index = 0
    for sample in stamps:
        while sample >= segments[interval_index].end:
            interval_index += 1
        labels[sample] = segments[interval_index].label
    imagery_total = sum(labels[s] != "T0" for s in stamps)
    rest_total = len(stamps) - imagery_total
    if not imagery_total or not rest_total:
        raise ValueError("opportunity grid must include both rest and imagery")

    results = {}
    for policy in POLICIES:
        acted = [(s, choices[(policy, s)]) for s in stamps if choices[(policy, s)] is not None]
        rest_wrong = sum(labels[s] == "T0" for s, _ in acted)
        imagery_wrong = sum(labels[s] != "T0" and labels[s] != direction for s, direction in acted)
        correct = sum(labels[s] == direction for s, direction in acted)
        imagery_acted = correct + imagery_wrong
        numerator = rest_wrong * recording.sample_rate_hz * 60
        results[policy] = {
            "actions_total": len(acted),
            "rest_false_actions": rest_wrong,
            "imagery_wrong_direction_actions": imagery_wrong,
            "correct_imagery_actions": correct,
            "imagery_opportunities": imagery_total,
            "rest_opportunities": rest_total,
            "imagery_coverage": imagery_acted / imagery_total,
            "correct_action_recall": correct / imagery_total,
            "incorrect_action_risk": (rest_wrong + imagery_wrong) / len(acted) if acted else None,
            "rest_false_actions_per_minute": round(numerator / exposure["T0"], 6),
            "rest_rate_exact_numerator": numerator,
            "rest_rate_exact_denominator": exposure["T0"],
        }
    a, b = results["abstention"], results["gate"]
    gap = abs(a["imagery_coverage"] - b["imagery_coverage"])
    comparable = (gap <= coverage_tolerance and a["actions_total"] > 0 and b["actions_total"] > 0)
    return {
        "evidence_class": "FICTIONAL_MATCHED_OPPORTUNITY_CONTRACT_ONLY",
        "sample_rate_hz": recording.sample_rate_hz,
        "rest_exposure_samples": exposure["T0"],
        "opportunities": len(stamps),
        "policies": results,
        "comparison": {
            "policies": ["abstention", "gate"],
            "imagery_coverage_gap": gap,
            "predeclared_tolerance": coverage_tolerance,
            "comparable": comparable,
            "gate_minus_abstention_incorrect_action_risk": (
                b["incorrect_action_risk"] - a["incorrect_action_risk"] if comparable else None
            ),
        },
        "real_eeg_evaluated": False,
        "decoder_trained": False,
        "limitations": "Fictional decisions and annotations; no EEG classifier, verified event clock, subject uncertainty, or measured safety.",
    }


def demo() -> str:
    rec = Recording(100, 6000)
    segments = (Segment(0, 2000, "T0"), Segment(2000, 4000, "T1"), Segment(4000, 6000, "T0"))
    opportunities = (0, 1000, 2000, 3000, 4000, 5000)
    # All policies see identical six opportunities; intentionally constructed.
    actions = {
        "ungated": ("T1", "T2", "T1", "T2", "T1", "T1"),
        "abstention": (None, None, "T1", "T2", None, None),
        "gate": (None, None, "T1", None, None, None),
    }
    decisions = [Decision(sample, policy, direction)
                 for policy, directions in actions.items()
                 for sample, direction in zip(opportunities, directions)]
    return json.dumps(evaluate(rec, segments, opportunities, decisions),
                      sort_keys=True, indent=2, allow_nan=False) + "\n"


if __name__ == "__main__":
    print(demo(), end="")
