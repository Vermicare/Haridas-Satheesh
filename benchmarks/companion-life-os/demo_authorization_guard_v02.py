"""One-minute synthetic demo: allow once; block replay, spoof, expiry."""
import json
from test_authorization_guard_v02 import scenario
from authorization_guard_v02 import ContractError, simulate_once


def run():
    s = scenario()
    scope = s['authorization']['scope']
    consumed = set()
    args = dict(principal='fictional-user', now='2026-10-01T10:30:00Z',
                consumed=consumed, trusted_principals={'fictional-user'})
    receipt = simulate_once(s, scope, **args)
    cases = []
    for name, mutate, overrides in [
        ('replay', lambda x: None, {}),
        ('spoofed_approval_actor', lambda x: x['authorization'].update(approved_by='fictional-attacker'), {'consumed': set()}),
        ('expired_approval', lambda x: None, {'consumed': set(), 'now': '2026-10-01T11:00:00Z'}),
    ]:
        candidate = scenario()
        mutate(candidate)
        try:
            simulate_once(candidate, scope, **(args | overrides))
            cases.append({'case': name, 'blocked': False})
        except ContractError as exc:
            cases.append({'case': name, 'blocked': True, 'reason': str(exc)})
    out = {'synthetic': True, 'receipt': receipt, 'negative_controls': cases,
           'blocked': sum(c['blocked'] for c in cases), 'total': len(cases),
           'real_identity_authentication': 'TBD', 'durable_replay_protection': 'TBD'}
    print(json.dumps(out, sort_keys=True, indent=2))
    return 0 if out['blocked'] == out['total'] and receipt['external_actions'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(run())
