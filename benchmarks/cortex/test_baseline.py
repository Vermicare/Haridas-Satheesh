#!/usr/bin/env python3
import copy, json
from pathlib import Path
from baseline import evaluate, extract

fixture=json.loads(Path(__file__).with_name("fixture.json").read_text())
heldout=json.loads(Path(__file__).with_name("heldout_fixture.json").read_text())

def test_reference_fixture():
    r=evaluate(fixture)
    for name,m in r["metrics"].items():
        if "f1" in m: assert m["f1"] == 1.0, (name,m)
    assert r["metrics"]["negative_case_false_actions"]["count"] == 0
    assert r["metrics"]["unsupported_fields"]["count"] == 0

def test_heldout_generalization():
    r=evaluate(heldout)
    for name,m in r["metrics"].items():
        if "f1" in m:
            assert m["f1"] == 1.0, (name,m)
    assert r["metrics"]["negative_case_false_actions"]["count"] == 0
    assert r["metrics"]["unsupported_fields"]["count"] == 0

def test_multidate_action_uses_explicit_deadline():
    p=extract(fixture)
    a1=next(a for a in p["actions"] if a["owner"]=="Ben")
    assert a1["due"]=="2026-09-29", a1
    assert a1["due"]!="2026-10-03", a1

def test_risk_statement_matches_canonical_ground_truth():
    p=extract(fixture)
    r17=next(r for r in p["risks"] if r["id"]=="R-17")
    assert r17["statement"]=="Sandbox instability may delay integration testing", r17

def test_ambiguous_proposal_not_promoted():
    p=extract(fixture)
    text=json.dumps(p)
    assert "replace the reporting tool" not in text
    assert "clean up the dashboard" not in text

def test_missing_approval_fails_closed():
    x=copy.deepcopy(fixture)
    x["meeting"]["utterances"][6]["text"]="Let's discuss that next time."
    p=extract(x)
    assert not any(d.get("supersedes")=="D0" for d in p["decisions"])

if __name__=="__main__":
    test_reference_fixture()
    test_heldout_generalization()
    test_multidate_action_uses_explicit_deadline()
    test_risk_statement_matches_canonical_ground_truth()
    test_ambiguous_proposal_not_promoted()
    test_missing_approval_fails_closed()
    print("6 tests passed")
