#!/usr/bin/env python3
"""Deterministic baseline for CORTEX synthetic governance benchmark v0.1.

This intentionally narrow baseline supports only the frozen synthetic fixture.
It exists to prove the reproducible extraction -> candidate JSON -> evaluator path,
not to claim general meeting understanding.
"""
import json, sys
from pathlib import Path

def baseline(fixture):
    utt={u["id"]:u["text"] for u in fixture["meeting"]["utterances"]}
    out={k:[] for k in ("decisions","actions","risks","dependencies","conditional_followups")}
    # Explicit high-confidence patterns only. Ambiguous u03/u04 and u08 are abstained.
    if "approved moving the API integration test to October 3" in utt.get("u01",""):
        out["decisions"].append({"source":["u01"],"statement":"Move API integration test to 2026-10-03","status":"active"})
    if "Ben owns the test plan" in utt.get("u01","") and "own the test plan" in utt.get("u02",""):
        out["actions"].append({"source":["u01","u02"],"owner":"Ben","due":"2026-09-29","action":"Circulate API integration test plan"})
    if "Risk R-17 remains open" in utt.get("u05",""):
        out["risks"].append({"source":["u05"],"status":"open","statement":"Sandbox instability may delay integration testing"})
        out["actions"].append({"source":["u05"],"owner":"Divya","due":"2026-09-27","action":"Request vendor sandbox recovery date"})
    if "depends on sandbox stability" in utt.get("u02","") and "Dependency D-04 is the vendor sandbox" in utt.get("u09",""):
        out["dependencies"].append({"source":["u02","u09"],"statement":"October 3 integration test depends on vendor sandbox stability"})
    if "earlier decision to freeze interface changes is superseded" in utt.get("u06","") and "Approved." in utt.get("u07",""):
        out["decisions"].append({"source":["u06","u07"],"statement":"Allow small interface fixes only with Asha approval","status":"active","supersedes":"D0"})
    if "not stable by September 30" in utt.get("u09",""):
        out["conditional_followups"].append({"source":["u09"],"condition":"Vendor sandbox not stable by 2026-09-30","action":"Escalate October 3 integration test at next governance review"})
    return out

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: baseline.py fixture.json")
    fixture=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(baseline(fixture),indent=2,sort_keys=True))

if __name__=="__main__": main()
