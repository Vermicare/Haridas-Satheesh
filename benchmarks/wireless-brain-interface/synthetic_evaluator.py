#!/usr/bin/env python3
"""Deterministic synthetic evaluator for WBI Issue #3.

Synthetic only: this is a contract test for evaluation logic, not EEG evidence.
Standard-library only. Thresholds are selected on calibration rows and frozen
before held-out test evaluation.
"""
from __future__ import annotations
import csv, math, random
from dataclasses import dataclass
from pathlib import Path

SEED_CAL, SEED_TEST = 19062000, 28092026
MIN_COVERAGE = 0.50
CONF_THRESHOLDS = [round(0.50 + 0.05*i, 2) for i in range(10)]
DRIFT_THRESHOLDS = [0.25, 0.40, 0.55, 0.70, 0.85]

@dataclass(frozen=True)
class Row:
    y: int
    p1: float
    drift: float
    segment: str

def fixture(seed: int, n: int = 240) -> list[Row]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        drifted = (i // 40) % 3 == 2
        y = rng.randint(0, 1)
        skill = 0.68 if not drifted else 0.54
        pred_correct = rng.random() < skill
        pred = y if pred_correct else 1-y
        confidence = min(0.99, max(0.50, rng.gauss(0.79 if pred_correct else 0.66, 0.10)))
        if drifted:
            confidence = min(0.99, confidence + rng.uniform(-0.04, 0.08))
        p1 = confidence if pred == 1 else 1-confidence
        drift = min(1.0, max(0.0, rng.gauss(0.28 if not drifted else 0.72, 0.13)))
        out.append(Row(y, p1, drift, "drift" if drifted else "nominal"))
    return out

def pred_conf(r: Row):
    pred = int(r.p1 >= 0.5)
    return pred, max(r.p1, 1-r.p1)

def metrics(rows: list[Row], acted: list[bool]) -> dict[str, float]:
    preds = [pred_conf(r)[0] for r in rows]
    acted_n = sum(acted)
    incorrect = sum(a and p != r.y for r, p, a in zip(rows, preds, acted))
    correct_total = sum(p == r.y for r, p in zip(rows, preds))
    correct_acted = sum(a and p == r.y for r, p, a in zip(rows, preds, acted))
    brier = sum((r.p1-r.y)**2 for r in rows)/len(rows)
    bins = [[] for _ in range(10)]
    for r, p in zip(rows, preds):
        c = pred_conf(r)[1]
        bins[min(9, int(c*10))].append((c, float(p == r.y)))
    ece = sum(len(b)/len(rows)*abs(sum(x for x,_ in b)/len(b)-sum(y for _,y in b)/len(b)) for b in bins if b)
    return {
        "coverage": acted_n/len(rows),
        "incorrect_action_risk": incorrect/acted_n if acted_n else math.nan,
        "correct_action_retention": correct_acted/correct_total if correct_total else math.nan,
        "brier": brier, "ece": ece,
    }

def confidence_policy(rows, threshold):
    return [pred_conf(r)[1] >= threshold for r in rows]

def gate_policy(rows, conf_t, drift_t):
    return [pred_conf(r)[1] >= conf_t and r.drift <= drift_t for r in rows]

def choose_conf(cal):
    candidates=[]
    for c in CONF_THRESHOLDS:
        m=metrics(cal, confidence_policy(cal,c))
        if m["coverage"] >= MIN_COVERAGE:
            candidates.append((m["incorrect_action_risk"], -m["coverage"], c))
    return min(candidates)[2]

def choose_gate(cal):
    candidates=[]
    for c in CONF_THRESHOLDS:
        for d in DRIFT_THRESHOLDS:
            m=metrics(cal, gate_policy(cal,c,d))
            if m["coverage"] >= MIN_COVERAGE:
                candidates.append((m["incorrect_action_risk"], -m["coverage"], c, d))
    _,_,c,d=min(candidates)
    return c,d

def contract_tests():
    toy=[Row(1,.9,.1,"nominal"),Row(0,.2,.2,"nominal"),Row(1,.4,.8,"drift"),Row(0,.7,.7,"drift")]
    m=metrics(toy,[True,True,False,False])
    assert abs(m["coverage"]-.5)<1e-12
    assert abs(m["incorrect_action_risk"])<1e-12
    assert abs(m["correct_action_retention"]-1.0)<1e-12
    a=fixture(SEED_CAL,20); b=fixture(SEED_CAL,20)
    assert a==b

def main():
    contract_tests()
    cal, test = fixture(SEED_CAL), fixture(SEED_TEST)
    conf_t=choose_conf(cal)
    gate_conf_t, gate_drift_t=choose_gate(cal)
    policies={
        "ungated":[True]*len(test),
        "confidence_abstention":confidence_policy(test,conf_t),
        "authorization_gate":gate_policy(test,gate_conf_t,gate_drift_t),
    }
    print("SYNTHETIC ONLY — not EEG/clinical validation")
    print(f"frozen thresholds: abstention_conf={conf_t:.2f}; gate_conf={gate_conf_t:.2f}; gate_drift={gate_drift_t:.2f}")
    for name, acted in policies.items():
        m=metrics(test,acted)
        print(name, " ".join(f"{k}={v:.4f}" for k,v in m.items()))
        for seg in ("nominal","drift"):
            idx=[i for i,r in enumerate(test) if r.segment==seg]
            sm=metrics([test[i] for i in idx],[acted[i] for i in idx])
            print(" ",seg," ".join(f"{k}={v:.4f}" for k,v in sm.items()))
    out=Path(__file__).with_name("synthetic_risk_coverage.csv")
    with out.open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["confidence_threshold","coverage","incorrect_action_risk","correct_action_retention"])
        for c in CONF_THRESHOLDS:
            m=metrics(test,confidence_policy(test,c))
            w.writerow([c,m["coverage"],m["incorrect_action_risk"],m["correct_action_retention"]])
    print(f"wrote {out.name}")

if __name__=="__main__":
    main()
