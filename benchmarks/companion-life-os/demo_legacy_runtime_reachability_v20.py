"""30-second, fictional-only dynamic reachability demonstration (v2.0)."""
import io
import json
import unittest

from test_legacy_runtime_reachability_v20 import LegacyRuntimeReachabilityV20


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        LegacyRuntimeReachabilityV20
    )
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(suite)
    report = {
        "schema": "companion-legacy-runtime-reachability-v2.0",
        "fixture": "disposable-local-sqlite-fictional-only",
        "tests_run": result.testsRun,
        "passed": result.wasSuccessful(),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "legacy_routes_demonstrated": [
            "FictionalDurableStore.execute",
            "FictionalOutbox.stage",
            "FictionalOutbox.dispatch",
            "FictionalIdempotentSink.apply",
        ],
        "interpretation": (
            "Four legacy fictional entry points can write disposable SQLite "
            "state without invoking the signed/revocable boundary. "
            "This does not establish production reachability or real harm."
        ),
        "real_external_actions": 0,
        "authenticated_human_consent": "TBD",
        "production_reachability": "TBD",
        "independent_security_review": "TBD",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if not result.wasSuccessful() or result.testsRun != 6:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
