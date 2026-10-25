"""Short side-effect-free demonstration of fictional v0.6 ledger auditing."""
import json
import sqlite3
from contextlib import closing
import tempfile
from pathlib import Path

from approval_consumption_v05 import (initialize, seed_fictional_approval,
                                      consume_fictional_approval)
from verify_approval_ledger_v06 import LedgerIntegrityError, verify


def run():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fictional.sqlite3"
        initialize(path)
        approval = dict(approval_id="fictional-demo-ap", actor_id="fictional-demo-actor",
                        action="fictional-demo-action", scope="fictional-demo-scope",
                        nonce="fictional-demo-nonce", expires_at=200)
        seed_fictional_approval(path, **approval)
        request = {k: v for k, v in approval.items() if k != "expires_at"}
        request.update(request_id="fictional-demo-req", receipt_id="fictional-demo-rc", now=100)
        outcome = consume_fictional_approval(path, **request)["outcome"]
        before = verify(path)
        with closing(sqlite3.connect(path)) as db:
            with db:
                db.execute("UPDATE consumption_receipts SET scope='fictional-forged-scope'")
        try:
            verify(path)
        except LedgerIntegrityError as exc:
            detected = str(exc)
        else:
            raise AssertionError("injected mismatch was not detected")
        return {"origin": "FICTIONAL_SYNTHETIC", "consumption": outcome,
                "consistent_before_injection": before["structurally_consistent"],
                "injected_mismatch_detected": detected,
                "external_actions": 0, "identity_authenticated": False,
                "trusted_clock": False, "tamper_proof": False}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
