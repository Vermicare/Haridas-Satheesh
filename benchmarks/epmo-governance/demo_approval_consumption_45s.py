"""Short fictional-only approval consumption demo. No external actions."""
import json
import tempfile
from pathlib import Path
from approval_consumption_v05 import (initialize, seed_fictional_approval,
                                      consume_fictional_approval, snapshot)


def demonstration():
    with tempfile.TemporaryDirectory(prefix="epmo-v05-fictional-") as folder:
        path = Path(folder) / "fictional.sqlite3"
        initialize(path)
        approval = dict(approval_id="ap-fictional", actor_id="actor-fictional",
                        action="update-fictional", scope="project-fictional",
                        nonce="nonce-fictional", expires_at=200)
        seed_fictional_approval(path, **approval)
        request = {k: v for k, v in approval.items() if k != "expires_at"}
        request.update(request_id="request-fictional", receipt_id="receipt-fictional", now=100)
        first = consume_fictional_approval(path, **request)
        retry = consume_fictional_approval(path, **request)
        changed = consume_fictional_approval(path, **{**request, "scope": "wrong"})
        state = snapshot(path)
        return {"origin": "FICTIONAL_SYNTHETIC",
                "outcomes": [first["outcome"], retry["outcome"], changed["outcome"]],
                "changed_reason": changed["reason"],
                "receipts": len(state["receipts"]),
                "external_actions": 0, "identity_authenticated": False,
                "trusted_clock": False}


if __name__ == "__main__":
    print(json.dumps(demonstration(), sort_keys=True, indent=2))
