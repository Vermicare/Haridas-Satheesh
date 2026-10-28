"""Short, reproducible JSON demo of fictional cross-process SQLite race gates.

Runs the actual test module; no external connector or production authorization.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest


def main():
    path = Path(__file__).with_name("test_atomic_multiprocess_v16.py")
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    suite = unittest.defaultTestLoader.loadTestsFromName(
        "test_atomic_multiprocess_v16")
    start = time.monotonic()
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    report = {
        "experiment": "fictional-cross-process-revocation-v16",
        "synthetic": True,
        "test_file_sha256": source_hash,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success": result.wasSuccessful(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "revocation_dispatch_races": 6,
        "parallel_dispatch_workers": 6,
        "external_actions": 0,
        "real_identity_authenticated": False,
        "physical_power_loss_tested": False,
        "legacy_bypasses_eliminated": False,
        "claim": "same-database fictional process-ordering regression only",
    }
    print(json.dumps(report, sort_keys=True))
    if not result.wasSuccessful():
        print(stream.getvalue(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
