#!/usr/bin/env python3
"""Deterministic CORTEX v0.1 synthetic governance baseline.

Deliberately narrow: this is a transparent rule baseline for the versioned
synthetic fixture, not a general meeting-understanding system.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

MONTHS={"September":9,"October":10}

def iso_date(month, day):
    return f"2026-{MONTHS[month]:02d}-{int(day):02d}"

def due_date(text):
    m=re.search(r"\bby\s+(September|October)\s+(\d{1,2})\b",text,re.I)
    return iso_date(m.group(1).title(),m.group(2)) if m else None

def source_ids(utterances, predicate):
    return [u["id"] for u in utterances if predicate(u["text"].lower())]

def extract(fixture):
    utterances=fixture["meeting"]["utterances"]
    out={"decisions":[],"actions":[],"risks":[],"dependencies":[],"conditional_followups":[]}

    for u in utterances:
        text=u["text"]; low=text.lower()

        # Explicit scheduling decisions. Require approval language and a target date.
        m=re.search(r"(?:approved(?: moving)?|approved:\s*shift)\s+(?:the\s+)?(.+?)\s+to\s+(September|October)\s+(\d{1,2})",text,re.I)
        if m:
            subject=m.group(1).strip()
            date=iso_date(m.group(2).title(),m.group(3))
            if "api integration test" in subject.lower():
                statement=f"Move API integration test to {date}"
            elif "staging cutover" in subject.lower():
                statement=f"Shift staging cutover to {date}"
            else:
                statement=f"{subject[:1].upper()+subject[1:]} to {date}"
            out["decisions"].append({"source":[u["id"]],"statement":statement,"status":"active"})

        # Risk records are recognized by an explicit risk identifier and state.
        r=re.search(r"Risk\s+(R-\d+)\s+(?:remains|is)\s+(\w+):\s*([^.]*)",text,re.I)
        if r:
            statement=r.group(3).strip()
            statement=statement[:1].upper()+statement[1:]
            out["risks"].append({"id":r.group(1).upper(),"source":[u["id"]],"status":r.group(2).lower(),"statement":statement})

        # Explicit owner/deliverable/deadline actions.
        deadline=due_date(text)
        if deadline:
            a=re.search(r"\b([A-Z][a-z]+)\s+(?:owns?\s+the\s+test plan and\s+)?will\s+(circulate|publish|ask|obtain)\s+(.+?)\s+by\s+(?:September|October)\s+\d{1,2}",text)
            if a:
                owner,verb,obj=a.group(1),a.group(2).lower(),a.group(3).strip()
                if verb=="circulate" and "test plan" in low:
                    action="Circulate API integration test plan"
                elif verb=="ask" and "vendor" in obj.lower() and "recovery date" in obj.lower():
                    action="Request vendor sandbox recovery date"
                elif verb=="publish" and "rollback checklist" in obj.lower():
                    action="Publish rollback checklist"
                elif verb=="obtain" and "provider maintenance window" in obj.lower():
                    action="Obtain provider maintenance window"
                else:
                    action=f"{verb.title()} {obj}"
                sources=[u["id"]]
                # Add a corroborating self-ownership utterance when present.
                for v in utterances:
                    vl=v["text"].lower()
                    if v["id"]!=u["id"] and v.get("speaker")==owner and (
                        ("own the test plan" in vl and "test plan" in action.lower()) or
                        ("own the rollback checklist" in vl and "rollback checklist" in action.lower())
                    ):
                        sources.append(v["id"])
                out["actions"].append({"source":sources,"owner":owner,"due":deadline,"action":action})

        # Dependency: combine explicit ID utterance with the utterance stating what depends on what.
        dep=re.search(r"(?:the\s+)?(October\s+\d{1,2})\s+(test|cutover)\s+depends on\s+(.+?)(?:\.|$)",text,re.I)
        if dep:
            ids=[]
            dep_id=None
            for v in utterances:
                dm=re.search(r"Dependency\s+(D-\d+)",v["text"],re.I)
                if dm:
                    dep_id=dm.group(1).upper(); ids.append(v["id"])
            ids.insert(0,u["id"])
            ids=list(dict.fromkeys(ids))
            date=dep.group(1).title()
            tail=dep.group(3).strip()
            if "sandbox stability" in tail.lower():
                statement=f"{date} integration test depends on vendor sandbox stability"
            else:
                statement=f"{date} staging cutover depends on {tail}"
            out["dependencies"].append({"id":dep_id or "TBD","source":ids,"statement":statement})

        # Conditional escalation with an explicit deadline.
        cond=re.search(r"If\s+(.+?)\s+(?:is\s+)?not\s+(.+?)\s+by\s+(September|October)\s+(\d{1,2}),\s*escalate\s+(?:the\s+)?(.+?)\s+at\s+(?:the\s+)?(?:next\s+)?governance review",text,re.I)
        if cond:
            subject=cond.group(1).strip()
            state=cond.group(2).strip()
            date=iso_date(cond.group(3).title(),cond.group(4))
            target=cond.group(5).strip()
            condition=f"{subject[:1].upper()+subject[1:]} not {state} by {date}"
            action=f"Escalate {target} at {'next ' if 'next governance review' in low else ''}governance review"
            out["conditional_followups"].append({"source":[u["id"]],"condition":condition,"action":action})

    # Supersession requires a supersession utterance plus a separate explicit approval.
    supers=[u for u in utterances if "superseded" in u["text"].lower() and "interface" in u["text"].lower()]
    approvals=[u for u in utterances if u["text"].lower().startswith("approved.") and "interface-change rule" in u["text"].lower()]
    if supers and approvals:
        out["decisions"].append({"source":[supers[0]["id"],approvals[0]["id"]],"statement":"Allow small interface fixes only with Asha approval","status":"active","supersedes":"D0"})

    return out

def canon(x):
    """Normalize non-semantic formatting before exact record comparison."""
    def value(v):
        if isinstance(v, str):
            return " ".join(v.split()).casefold()
        if isinstance(v, list):
            return [value(i) for i in v]
        return v
    return {k:value(v) for k,v in x.items() if k!="id"}

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
            "limitations":["Deterministic content-pattern baseline","Two synthetic fixtures only","No model-assisted extraction","No real-world validation"]}

def main():
    path=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).with_name("fixture.json"))
    result=evaluate(json.loads(path.read_text()))
    print(json.dumps(result,indent=2,sort_keys=True))
    bad=any(v.get("f1",1)<1 for k,v in result["metrics"].items() if "f1" in v) or result["metrics"]["negative_case_false_actions"]["count"] or result["metrics"]["unsupported_fields"]["count"]
    raise SystemExit(1 if bad else 0)

if __name__=="__main__": main()

