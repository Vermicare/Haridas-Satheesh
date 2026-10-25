"""Deterministic fictional end-to-end receipt -> correction demonstration; no I/O outside temp SQLite."""
import json
import tempfile
from pathlib import Path

from authorization_store_v03 import FictionalDurableStore
from correction_ledger_v05 import FictionalCorrectionLedger
from test_actual_receipt_integration_v06 import fictional_correction, fictional_scenario


def main():
    s = fictional_scenario()
    args = {
        "principal": "fictional-user",
        "now": "2026-10-01T10:30:00Z",
        "trusted_principals": {"fictional-user"},
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fictional.sqlite3"
        store = FictionalDurableStore(path)
        ledger = FictionalCorrectionLedger(path)
        original = store.execute(s, s["authorization"]["scope"], **args)
        correction = ledger.record(original["nonce"], fictional_correction(), **args)
        replay = FictionalCorrectionLedger(path).record(
            original["nonce"], fictional_correction(), **args
        )
        original_replay = FictionalDurableStore(path).execute(
            s, s["authorization"]["scope"], **args
        )
        output = {
            "fictional": True,
            "original_receipt": original,
            "correction_event": correction,
            "correction_replay": replay,
            "original_replay": original_replay,
            "stored_original_receipts": store.receipt_count(),
            "stored_corrections": ledger.correction_count(),
            "real_external_actions": 0,
            "authenticated_identity": "TBD",
            "trusted_clock": "TBD",
            "actual_task_reversal": "TBD",
        }
    print(json.dumps(output, sort_keys=True, indent=2))
    return 0 if (
        not original["idempotent_replay"]
        and not correction["idempotent_replay"]
        and replay["idempotent_replay"]
        and original_replay["idempotent_replay"]
        and output["stored_original_receipts"] == 1
        and output["stored_corrections"] == 1
        and output["real_external_actions"] == 0
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
