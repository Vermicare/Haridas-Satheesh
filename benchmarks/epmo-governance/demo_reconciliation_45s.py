"""45-second narrated fictional replay/ledger agreement and mismatch demo.

No external action. The generated ledger is a demonstration fixture, not independent proof.
"""
from __future__ import annotations
import json
import tempfile
from pathlib import Path

from durable_receipt_sandbox import initialize, record_simulated_receipt, record_simulated_correction
from governance_demo import evaluate
from reconcile_fictional_replay import ReconciliationError, reconcile


def demonstration(scenario):
    if scenario.get("origin") != "FICTIONAL_SYNTHETIC":
        raise ValueError("fictional fixtures only")
    replay = evaluate(scenario)
    with tempfile.TemporaryDirectory(prefix="fictional-epmo-reconcile-") as folder:
        path = Path(folder) / "ledger.sqlite3"
        initialize(path)
        for event, audit in zip(scenario["events"], replay["audit"]):
            if not audit["accepted"]:
                continue
            payload = event["payload"]
            if event["type"] == "execute":
                record_simulated_receipt(path, request_id=event["request_id"],
                    receipt_id=payload["receipt_id"], approval_id=payload["approval_id"],
                    action=payload["action"], scope=payload["scope"])
            elif event["type"] == "correct":
                record_simulated_correction(path, request_id=event["request_id"],
                    receipt_id=payload["receipt_id"], reason=payload["reason"])
        good = reconcile(scenario, path)
        record_simulated_receipt(path, request_id="fictional-injected-extra",
            receipt_id="fictional-injected-extra", approval_id="fictional-injected-extra",
            action="fictional-extra", scope="fictional-extra")
        try:
            reconcile(scenario, path)
        except ReconciliationError as exc:
            negative = str(exc)
        else:
            raise AssertionError("extra ledger row escaped detection")
        return {"origin": "FICTIONAL_SYNTHETIC", "positive_reconciled": good["reconciled"],
                "accepted_executions": good["accepted_executions"],
                "corrected_receipts": good["corrected_receipts"],
                "negative_control_detected": "extra=" in negative,
                "external_actions": 0, "identity_authenticated": False,
                "durable_policy_enforced": False}


def main():
    scenario = json.loads(Path(__file__).with_name("synthetic_scenario.json").read_text(encoding="utf-8"))
    print(json.dumps(demonstration(scenario), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
