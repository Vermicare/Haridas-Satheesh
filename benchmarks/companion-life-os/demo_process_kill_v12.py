"""Short, entirely fictional crash-window demonstration (JSON to stdout)."""
import io
import json
import platform
import sqlite3
import sys
import unittest

from test_process_kill_v12 import FictionalProcessKillTests

suite = unittest.defaultTestLoader.loadTestsFromTestCase(FictionalProcessKillTests)
result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
summary = {
    "benchmark": "companion-fictional-sqlite-process-kill-v1.2",
    "synthetic": True,
    "physical_power_loss_tested": False,
    "external_actions": 0,
    "real_identity_or_consent": False,
    "python_version": platform.python_version(),
    "sqlite_version": sqlite3.sqlite_version,
    "operating_system": platform.system(),
    "test_count": result.testsRun,
    "passed": result.wasSuccessful(),
    "failures": len(result.failures),
    "errors": len(result.errors),
    "scope": "local SQLite commit-window child termination and restart only",
    "real_connector_effects": "TBD",
    "independent_review": "TBD"
}
print(json.dumps(summary, sort_keys=True))
if not result.wasSuccessful():
    sys.exit(1)
