"""Short fictional-only dispatch-time authorization demonstration (v2.1)."""
import io
import json
import unittest
from test_expiry_checked_delivery_v21 import ExpiryCheckedDispatchV21Tests


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ExpiryCheckedDispatchV21Tests)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=1).run(suite)
    report = {
        'schema': 'companion-expiry-checked-dispatch-v2.1',
        'fixture': 'disposable-local-sqlite-fictional-only',
        'tests_run': result.testsRun,
        'passed': result.wasSuccessful(),
        'failures': len(result.failures),
        'errors': len(result.errors),
        'real_external_actions': 0,
        'clock_trust': 'caller-supplied-test-only',
        'human_authentication': 'TBD',
        'legacy_bypass_routes': 'remain-open',
        'production_security': 'TBD',
        'meaning': ('Candidate checks signed fictional identity, approval and '
                    'expiry at fake dispatch; original legacy routes remain.'),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if not result.wasSuccessful() or result.testsRun != 14:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
