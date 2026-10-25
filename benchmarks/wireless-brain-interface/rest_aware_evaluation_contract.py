#!/usr/bin/env python3
"""Fictional WBI rest-aware evaluation contract; does not read or decode EEG.

The frozen synthetic evaluator and PhysioNet split generator remain unchanged.
T0 is excluded from imagery-classifier training but retained for action safety.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import math
from eegmmidb_split_contract import generate

CONF_GRID = (0.50, 0.60, 0.70, 0.80, 0.90)
DRIFT_GRID = (0.30, 0.50, 0.70, 1.00)
MIN_IMAGERY_COVERAGE = 0.50

@dataclass(frozen=True)
class Event:
    subject: str
    split: str
    event_id: str
    label: str
    p_left: float
    drift: float

def validate(rows, split):
    if split not in ("calibration", "test"):
        raise ValueError("only calibration or test can be scored")
    allowed = set(generate()["subject_splits"][split])
    items = list(rows)
    if not items:
        raise ValueError("no events")
    seen, labels_by_subject = set(), {}
    for r in items:
        if not isinstance(r, Event):
            raise ValueError("invalid event object")
        if r.split != split or r.subject not in allowed:
            raise ValueError("split mismatch or subject leakage")
        if not isinstance(r.event_id, str) or not r.event_id or len(r.event_id) > 128:
            raise ValueError("invalid event id")
        key = (r.subject, r.event_id)
        if key in seen:
            raise ValueError("duplicate event id")
        seen.add(key)
        if r.label not in ("T0", "T1", "T2"):
            raise ValueError("unknown task label")
        for value in (r.p_left, r.drift):
            if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("nonfinite or out-of-range score")
        labels_by_subject.setdefault(r.subject, set()).add(r.label)
    for subject, labels in labels_by_subject.items():
        if "T0" not in labels or not ({"T1", "T2"} & labels):
            raise ValueError(f"missing rest or imagery denominator for {subject}")
    return items

def acts(r, policy, confidence, drift=1.0):
    conf = max(r.p_left, 1.0 - r.p_left)
    if policy == "ungated":
        return True
    if policy == "abstention":
        return conf >= confidence
    if policy == "gate":
        return conf >= confidence and r.drift <= drift
    raise ValueError("unknown policy")

def score(rows, policy, confidence, drift=1.0):
    """Every act on T0 is incorrect; event rate is not a time-normalized rate."""
    items = list(rows)
    if not items:
        raise ValueError("no events")
    if not all(type(x) in (float, int) and math.isfinite(x) and 0 <= x <= 1
               for x in (confidence, drift)):
        raise ValueError("invalid policy thresholds")
    imagery = [r for r in items if r.label != "T0"]
    rest = [r for r in items if r.label == "T0"]
    if not imagery or not rest:
        raise ValueError("rest and imagery denominators are required")
    acted = [r for r in items if acts(r, policy, confidence, drift)]
    def correct(r):
        return ((r.label == "T1" and r.p_left >= 0.5)
                or (r.label == "T2" and r.p_left < 0.5))
    correct_possible = sum(correct(r) for r in imagery)
    correct_acted = sum(correct(r) for r in acted if r.label != "T0")
    rest_acted = sum(r.label == "T0" for r in acted)
    imagery_acted = sum(r.label != "T0" for r in acted)
    return {
        "imagery_events": len(imagery), "rest_events": len(rest),
        "acted_imagery": imagery_acted, "acted_rest": rest_acted,
        "acted_total": len(acted),
        "imagery_coverage": imagery_acted / len(imagery),
        "rest_false_action_per_event": rest_acted / len(rest),
        "incorrect_action_risk": (len(acted) - correct_acted) / len(acted) if acted else None,
        "correct_action_retention": correct_acted / correct_possible if correct_possible else None,
        "rate_unit": "events (not seconds or continuous EEG windows)",
    }

def choose_thresholds(calibration):
    """Same calibration-only objective and imagery coverage floor for both policies."""
    rows = validate(calibration, "calibration")
    selected = {}
    for policy in ("abstention", "gate"):
        candidates = []
        for c in CONF_GRID:
            for d in (DRIFT_GRID if policy == "gate" else (1.0,)):
                m = score(rows, policy, c, d)
                if m["imagery_coverage"] >= MIN_IMAGERY_COVERAGE and m["acted_total"]:
                    candidates.append((m["rest_false_action_per_event"],
                                       m["incorrect_action_risk"],
                                       -m["imagery_coverage"], c, d))
        if not candidates:
            raise ValueError("no threshold meets imagery coverage floor")
        _, _, _, c, d = min(candidates)
        selected[policy] = {"confidence": c, "drift": d}
    return selected

def evaluate(calibration, test):
    cal = validate(calibration, "calibration")
    holdout = validate(test, "test")
    thresholds = choose_thresholds(cal)
    results = {"ungated": score(holdout, "ungated", 0.5)}
    for policy, t in thresholds.items():
        results[policy] = score(holdout, policy, t["confidence"], t["drift"])
    return {
        "status": "FICTIONAL_CONTRACT_ONLY", "thresholds": thresholds,
        "results": results, "trained_decoder": False,
        "real_eeg_evaluated": False, "clinical_validation": False,
        "limitations": "Fictional event-level scores; no real EEG, continuous idle windows, measured time, or decoder accuracy.",
    }

def fictional_rows(split):
    subjects = generate()["subject_splits"][split][:3]
    rows = []
    for i, subject in enumerate(subjects):
        for j, (label, p, d) in enumerate((("T0", 0.90, 0.85),
                                           ("T1", 0.82, 0.20),
                                           ("T2", 0.21, 0.25),
                                           ("T0", 0.58, 0.45))):
            rows.append(Event(subject, split, f"fictional-{i}-{j}", label, p, d))
    return rows

def demo():
    return json.dumps(evaluate(fictional_rows("calibration"), fictional_rows("test")),
                      indent=2, sort_keys=True, allow_nan=False) + "\n"

if __name__ == "__main__":
    print(demo(), end="")
