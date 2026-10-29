"""Machine-readable, fictional-only v1.8 negative-control demonstration."""
import json
import unittest
from io import StringIO
from test_dispatch_expiry_gap_v18 import DispatchExpiryGapTests

suite = unittest.defaultTestLoader.loadTestsFromTestCase(DispatchExpiryGapTests)
result = unittest.TextTestRunner(stream=StringIO(), verbosity=1).run(suite)
print(json.dumps({
    "schema": "companion-dispatch-expiry-gap-v1.8",
    "fictional": True,
    "success": result.wasSuccessful(),
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "negative_control": "v1.4 staged work can reach fake sink without dispatch-time expiry check",
    "revocation_contrast": "v1.4 revocation still cancels pending work",
    "real_external_actions": 0,
    "clock_at_dispatch": "not supplied to legacy adapter",
    "authenticated_human": False,
    "physical_or_production_validation": False
}, sort_keys=True, allow_nan=False))
if not result.wasSuccessful() or result.testsRun != 4:
    raise SystemExit(1)
