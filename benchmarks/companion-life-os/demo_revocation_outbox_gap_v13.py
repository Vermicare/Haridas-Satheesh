"""30-second fictional negative-control demo. Zero external side effects."""
import copy
import json
import tempfile
from pathlib import Path

from authorization_guard_v02 import ContractError
from fictional_outbox_v07 import FictionalIdempotentSink, FictionalOutbox
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture


def main():
    scenario = fixture()
    scope = copy.deepcopy(scenario["authorization"]["scope"])
    issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
    identity = issuer.issue_identity(
        "fictional-user", "2026-10-01T09:00:00Z", "2026-10-01T12:00:00Z"
    )
    approval = issuer.issue_approval(scenario)
    with tempfile.TemporaryDirectory() as directory:
        db = Path(directory) / "receipts.sqlite3"
        sink_db = Path(directory) / "fake-sink.sqlite3"
        store = FictionalRevocableStore(db)
        boundary = FictionalRevocableBoundary(store, IDENTITY_KEY, APPROVAL_KEY)
        args = dict(identity_token=identity, approval_token=approval, now=NOW)
        receipt = boundary.execute(scenario, scope, **args)
        outbox = FictionalOutbox(db)
        outbox.stage(receipt["nonce"])
        boundary.revoke(approval, now=NOW, reason="fictional withdrawal")
        try:
            boundary.execute(scenario, scope, **args)
            signed_path = "INCORRECT_ACCEPT"
        except ContractError:
            signed_path = "DENIED"
        sink = FictionalIdempotentSink(sink_db)
        ack = outbox.dispatch(receipt["nonce"], sink)
        result = {
            "experiment": "companion-revocation-outbox-gap-v1.3",
            "fictional": True,
            "test_clock": NOW,
            "signed_execution_after_revocation": signed_path,
            "legacy_outbox_after_revocation": "SIMULATED_DELIVERY",
            "fake_sink_rows": sink.count(),
            "revocation_rows": store.revocation_count(),
            "original_receipt_rows": store.receipt_count(),
            "external_actions": ack["external_actions"],
            "simulated_actions": ack["simulated_actions"],
            "safety_claim": "NEGATIVE_CONTROL_ONLY",
            "real_identity_or_consent": False,
        }
        assert signed_path == "DENIED"
        assert result["fake_sink_rows"] == result["revocation_rows"] == 1
        assert result["external_actions"] == 0
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
