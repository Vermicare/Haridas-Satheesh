"""30-60 second fictional revocation demo; all effects remain local SQLite."""
import copy
import json
import tempfile
from pathlib import Path

from authorization_guard_v02 import ContractError
from sandbox_issuer_v10 import FictionalIssuer
from revocable_signed_boundary_v11 import FictionalRevocableBoundary, FictionalRevocableStore

IDENTITY_KEY = b'PUBLIC_TEST_ONLY_IDENTITY_KEY_2026'
APPROVAL_KEY = b'PUBLIC_TEST_ONLY_APPROVAL_KEY_2026'
NOW = '2026-10-01T10:30:00Z'


def main():
    s = json.loads(Path(__file__).with_name('scenario.json').read_text(encoding='utf-8'))
    s['proposed_decision']['scope'] = copy.deepcopy(s['authorization']['scope'])
    s['authorization'].update(issued_at='2026-10-01T10:00:00Z',
                              expires_at='2026-10-01T11:00:00Z', nonce='demo-fictional-revoke-1')
    issuer = FictionalIssuer(IDENTITY_KEY, APPROVAL_KEY)
    identity = issuer.issue_identity('fictional-user', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
    approval = issuer.issue_approval(s)
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / 'demo.sqlite3'
        store = FictionalRevocableStore(db)
        boundary = FictionalRevocableBoundary(store, IDENTITY_KEY, APPROVAL_KEY)
        args = dict(identity_token=identity, approval_token=approval, now=NOW)
        first = boundary.execute(s, s['authorization']['scope'], **args)
        before_revoke_replay = boundary.execute(s, s['authorization']['scope'], **args)
        revocation = boundary.revoke(approval, now=NOW, reason='fictional operator withdrew approval')
        try:
            boundary.execute(s, s['authorization']['scope'], **args)
            post_revoke = 'INCORRECT_ACCEPT'
        except ContractError:
            post_revoke = 'DENIED'
        restarted = FictionalRevocableBoundary(FictionalRevocableStore(db), IDENTITY_KEY, APPROVAL_KEY)
        try:
            restarted.execute(s, s['authorization']['scope'], **args)
            after_restart = 'INCORRECT_ACCEPT'
        except ContractError:
            after_restart = 'DENIED'
        result = {
            'experiment': 'companion-fictional-revocation-v1.1',
            'synthetic': True, 'test_clock': NOW, 'external_actions': 0,
            'first_receipt_simulated': first['result'] == 'simulated-success',
            'pre_revocation_replay_idempotent': before_revoke_replay['idempotent_replay'],
            'new_revocation': revocation['new_revocation'],
            'post_revocation_execution': post_revoke,
            'post_restart_execution': after_restart,
            'preserved_original_receipts': store.receipt_count(),
            'revocation_events': store.revocation_count(),
            'real_identity_or_consent_validated': False,
            'real_connector_used': False,
        }
        assert result['post_revocation_execution'] == result['post_restart_execution'] == 'DENIED'
        assert result['preserved_original_receipts'] == result['revocation_events'] == 1
        print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
