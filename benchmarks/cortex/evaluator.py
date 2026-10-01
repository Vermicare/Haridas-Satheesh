#!/usr/bin/env python3
"""Dependency-free evaluator for the CORTEX synthetic governance benchmark.

Usage:
  python evaluator.py fixture.json candidate.json
Candidate JSON must contain decisions/actions/risks/dependencies/conditional_followups arrays.
This scorer never extracts facts; it only evaluates supplied machine-readable output.
"""
import json, sys
from pathlib import Path

KINDS = ("decisions","actions","risks","dependencies","conditional_followups")
FIELDS = {
    "decisions": ("statement","status","supersedes"),
    "actions": ("owner","due","action"),
    "risks": ("status","statement"),
    "dependencies": ("statement",),
    "conditional_followups": ("condition","action"),
}

def norm(v):
    if v is None: return None
    return " ".join(str(v).strip().lower().split())

def signature(kind, obj):
    return tuple(norm(obj.get(k)) for k in FIELDS[kind])

def prf(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    f = 2*p*r/(p+r) if p+r else 0.0
    return {"precision":round(p,6),"recall":round(r,6),"f1":round(f,6)}

def evaluate(fixture, candidate):
    gt = fixture["ground_truth"]
    out = {"benchmark":fixture.get("benchmark"),"synthetic":True,"metrics":{},"failures":[]}
    total_pred = total_tp = unsupported = trace_ok = 0
    for kind in KINDS:
        gold = gt.get(kind, [])
        pred = candidate.get(kind, [])
        gold_by_sig = {signature(kind,x):x for x in gold}
        matched=set()
        tp=0
        for i,p in enumerate(pred):
            total_pred += 1
            sig=signature(kind,p)
            g=gold_by_sig.get(sig)
            if g is None or sig in matched:
                out["failures"].append({"kind":kind,"index":i,"reason":"unsupported_or_duplicate","object":p})
                unsupported += 1
                continue
            matched.add(sig); tp += 1; total_tp += 1
            ps=set(p.get("source",[])); gs=set(g.get("source",[]))
            if ps and ps.issubset(gs): trace_ok += 1
            else: out["failures"].append({"kind":kind,"index":i,"reason":"source_trace_mismatch","expected":sorted(gs),"observed":sorted(ps)})
        fp=len(pred)-tp; fn=len(gold)-tp
        out["metrics"][kind]=dict(prf(tp,fp,fn),tp=tp,fp=fp,fn=fn)
    out["metrics"]["unsupported_field_rate"] = round(unsupported/total_pred,6) if total_pred else 0.0
    out["metrics"]["source_span_traceability"] = round(trace_ok/total_tp,6) if total_tp else 0.0

    # Negative-case protection: candidate may optionally expose source IDs used for any object.
    neg_sources={s for n in gt.get("negative_examples",[]) for s in n.get("source",[])}
    used_sources={s for k in KINDS for o in candidate.get(k,[]) for s in o.get("source",[])}
    violations=sorted(neg_sources & used_sources)
    out["metrics"]["negative_case_violations"]=len(violations)
    if violations: out["failures"].append({"kind":"negative_examples","reason":"negative_source_promoted","sources":violations})

    # Lineage is scored only where ground truth declares supersedes.
    lineage_gold=[g for g in gt.get("decisions",[]) if g.get("supersedes")]
    lineage_ok=0
    pred_dec={signature("decisions",p):p for p in candidate.get("decisions",[])}
    for g in lineage_gold:
        p=pred_dec.get(signature("decisions",g))
        if p and norm(p.get("supersedes"))==norm(g.get("supersedes")): lineage_ok += 1
    out["metrics"]["decision_reversal_lineage_accuracy"] = round(lineage_ok/len(lineage_gold),6) if lineage_gold else None
    return out

def main():
    if len(sys.argv)!=3:
        raise SystemExit("usage: evaluator.py fixture.json candidate.json")
    fixture=json.loads(Path(sys.argv[1]).read_text())
    candidate=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate(fixture,candidate),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
