"""Reproducible fictional revocation-first 30-second demonstration; no network."""
import copy
import json
import tempfile
from pathlib import Path

from atomic_revocation_delivery_v14 import AtomicFictionalDelivery, FictionalDeliveryError
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore
from sandbox_issuer_v10 import FictionalIssuer
from test_revocable_signed_boundary_v11 import APPROVAL_KEY, IDENTITY_KEY, NOW, fixture


def main():
    with tempfile.TemporaryDirectory() as folder:
        store = FictionalRevocableStore(Path(folder) / 'fictional.sqlite3')
        boundary = FictionalRevocableBoundary(store, IDENTITY_KEY, APPROVAL_KEY)
        adapter = AtomicFictionalDelivery(boundary)
        scenario = fixture()
        scope = copy.deepcopy(scenario['authorization']['scope'])
        issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
        identity = issuer.issue_identity('fictional-user',
                                         '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
        approval = issuer.issue_approval(scenario)
        nonce = adapter.stage(scenario, scope, identity_token=identity,
                              approval_token=approval, now=NOW)['nonce']
        boundary.revoke(approval, now=NOW, reason='fictional stop')
        denied = False
        try:
            adapter.dispatch(nonce)
        except FictionalDeliveryError:
            denied = True
        result = {'experiment': 'v1.4-fictional-same-db-revocation-first',
                  'revocation_precedes_dispatch': True,
                  'dispatch_denied': denied,
                  'counts': adapter.counts(nonce),
                  'legacy_bypass_fixed': False,
                  'real_identity_verified': False,
                  'physical_power_loss_tested': False,
                  'external_actions': 0}
        if not denied or result['counts']['fictional_sink_rows'] != 0:
            raise AssertionError('fictional cancellation expectation failed')
        print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
