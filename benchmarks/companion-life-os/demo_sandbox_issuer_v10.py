"""One-command 30–60 second fictional identity/approval and SQLite receipt demo."""
import copy
import json
import tempfile
from pathlib import Path

from authorization_guard_v02 import ContractError
from authorization_store_v03 import FictionalDurableStore
from sandbox_issuer_v10 import FictionalIssuer, FictionalSignedBoundary


def main():
    s = json.loads(Path(__file__).with_name('scenario.json').read_text(encoding='utf-8'))
    s['proposed_decision']['scope'] = copy.deepcopy(s['authorization']['scope'])
    s['authorization'].update(issued_at='2026-10-01T10:00:00Z',
                              expires_at='2026-10-01T11:00:00Z', nonce='demo-signed-fictional-1')
    identity_key = b'PUBLIC_TEST_ONLY_IDENTITY_KEY_2026'
    approval_key = b'PUBLIC_TEST_ONLY_APPROVAL_KEY_2026'
    issuer = FictionalIssuer(identity_key, approval_key)
    gate = FictionalSignedBoundary(identity_key, approval_key)
    identity = issuer.issue_identity('fictional-user', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z')
    approval = issuer.issue_approval(s)
    now = '2026-10-01T10:30:00Z'
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'fictional.sqlite3'
        first = gate.execute(FictionalDurableStore(path), s, s['authorization']['scope'],
                             identity_token=identity, approval_token=approval, now=now)
        retry = gate.execute(FictionalDurableStore(path), s, s['authorization']['scope'],
                             identity_token=identity, approval_token=approval, now=now)
        denied = []
        cases = [('unsigned identity', 'fictional-user', approval, now),
                 ('expired approval', identity, approval, '2026-10-01T11:00:00Z'),
                 ('wrong identity', issuer.issue_identity('fictional-attacker', '2026-10-01T09:00:00Z', '2026-10-01T12:00:00Z'), approval, now)]
        for label, identity_token, approval_token, clock in cases:
            try:
                gate.execute(FictionalDurableStore(path), s, s['authorization']['scope'],
                             identity_token=identity_token, approval_token=approval_token, now=clock)
            except ContractError:
                denied.append(label)
            else:
                raise AssertionError('negative control unexpectedly passed: ' + label)
        print(json.dumps({'synthetic': True, 'identity_proof': 'fictional issuer only',
                          'trusted_clock': False, 'first_receipt': first['result'],
                          'retry_idempotent': retry['idempotent_replay'],
                          'stored_receipts': FictionalDurableStore(path).receipt_count(),
                          'rejected_cases': denied, 'external_actions': 0,
                          'real_human_consent': 'TBD'}, sort_keys=True))


if __name__ == '__main__':
    main()
