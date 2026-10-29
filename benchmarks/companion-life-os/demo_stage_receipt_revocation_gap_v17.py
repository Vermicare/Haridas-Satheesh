"""Machine-readable v1.7 fictional negative-control demonstration."""
import hashlib
import io
import json
import time
import unittest
from pathlib import Path

from test_stage_receipt_revocation_gap_v17 import StageReceiptRevocationGapTests


def main():
    start = time.monotonic()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StageReceiptRevocationGapTests)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    source = Path(__file__).with_name("test_stage_receipt_revocation_gap_v17.py").read_bytes()
    normalized = source.replace(b"\r\n", b"\n")
    output = {
        "experiment": "companion-stage-receipt-revocation-gap-v1.7",
        "fictional_only": True,
        "external_actions": 0,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success": result.wasSuccessful() and result.testsRun == 4,
        "negative_control": "stranded receipt can be dispatched through legacy fake outbox",
        "not_proven": [
            "real identity or consent", "production revocation",
            "safe public execution entry point", "external service idempotency"
        ],
        "test_source_sha256_lf_normalized": hashlib.sha256(normalized).hexdigest(),
        "elapsed_seconds": round(time.monotonic() - start, 3)
    }
    print(json.dumps(output, sort_keys=True))
    if not output["success"]:
        raise SystemExit(stream.getvalue())


if __name__ == "__main__":
    main()
