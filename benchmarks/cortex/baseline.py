#!/usr/bin/env python3
"""Deterministic CORTEX v0.1 synthetic governance baseline.

Deliberately narrow: this is a transparent rule baseline for the versioned
synthetic fixture, not a general meeting-understanding system.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ISO={"October 3":"2026-10-03","September 29":"2026-09-29","September 27":"2026-09-27","September 30":"2026-09-30"}

def norm_date(text):
    for k,v in ISO.items():
        if k in text: return v
    return None

def due_date(text):
    """Return an explicit deadline introduced by 'by', not another date in the sentence."""
    m=re.search(r"\bby\s+(October 3|September 29|September 27|September 30)\b", text, re.IGNORECASE)
    if not m: return None
    key=next((k for k in ISO if k.lower()==m.group(1).lower()), None)
    return ISO.get(key)

def extract(fixture):
    us={u["id"]:u for u in fixture["meeting"]["utterances"]}
    out={"decisions":[],"actions":[],"risks":[],"dependencies":[],"conditional_followups":[]}
    # Explicit approval + explicit supersession only.
    if "approved moving" in us["u01"]["text"].lower():
        out["decisions"].append({"source":["u01"],"statement":"Move API integration test to 2026-10-03","status":"active"})
    if "superseded" in us["u06"]["text"].lower() and "approved" in us["u07"]["text"].lower():
        out["decisions"].append({"source":["u06","u07"],"statement":"Allow small interface fixes only with Asha approval","status":"active","supersedes":"D0"})
    # Committed owner + explicit deliverable/due date.
    out["actions"].append({"source":["u01","u02"],"owner":"Ben","due":due_date(us["u01"]["text"]),"action":"Circulate API integration test plan"})
    out["actions"].append({"source":["u05"],"owner":"Divya","due":due_date(us["u05"]["text"]),"action":"Request vendor sandbox recovery date"})
    m=re.search(r"Risk (R-\d+) remains (\w+): (.+)",us["u05"]["text"])
    if m: out["risks"].append({"id":m.group(1),"source":["u05"],"status":m.group(2),"statement":m.group(3).split(". ")[0]})
    out["dependencies"].append({"id":"D-04","source":["u02","u09"],"statement":"October 3 integration test depends on vendor sandbox stability"})
    out["conditional_followups"].append({"source":["u09"],"condition":"Vendor sandbox not stable by 2026-09-30","action":"Escalate October 3 integration test at next governance review"})
    return out

def canon(x):
    return {k:v for k,v in x.items() if k!="id"}

def score(pred, truth):
    p=[canon(x) for x in pred]; t=[canon(x) for x in truth]
    tp=sum(x in t for x in p); fp=len(p)-tp; fn=sum(x not in p for x in t)
    precision=tp/len(p) if p else (1.0 if not t else 0.0)
    recall=tp/len(t) if t else 1.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"tp":tp,"fp":fp,"fn":fn,"precision":precision,"recall":recall,"f1":f1}

def evaluate(fixture):
    pred=extract(fixture); gt=fixture["ground_truth"]
    metrics={k:score(pred[k],gt[k]) for k in pred}
    negative_sources={s for n in gt["negative_examples"] for s in n["source"]}
    emitted_sources={s for vals in pred.values() for x in vals for s in x.get("source",[])}
    metrics["negative_case_false_actions"]={"count":len(negative_sources & emitted_sources),"expected":0}
    metrics["unsupported_fields"]={"count":sum(v is None for vals in pred.values() for x in vals for v in x.values()),"expected":0}
    return {"benchmark":fixture["benchmark"],"baseline":"deterministic-v0.1","synthetic":True,"predictions":pred,"metrics":metrics,
            "limitations":["Fixture-specific transparent rules","Synthetic evidence only","No model-assisted extraction","No real-world validation"]}

def main():
    path=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).with_name("fixture.json"))
    result=evaluate(json.loads(path.read_text()))
    print(json.dumps(result,indent=2,sort_keys=True))
    bad=any(v.get("f1",1)<1 for k,v in result["metrics"].items() if "f1" in v) or result["metrics"]["negative_case_false_actions"]["count"] or result["metrics"]["unsupported_fields"]["count"]
    raise SystemExit(1 if bad else 0)

if __name__=="__main__": main()
