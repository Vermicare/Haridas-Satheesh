"""Short, deterministic fictional demo: durable local receipt, restart and replay."""
import json
import tempfile
from pathlib import Path

from authorization_store_v03 import FictionalDurableStore
from test_authorization_store_v03 import scenario


def main():
    s = scenario()
    scope = s['authorization']['scope']
    args = dict(principal='fictional-user', now='2026-10-01T10:30:00Z',
                trusted_principals={'fictional-user'})
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'fictional.sqlite3'
        first = FictionalDurableStore(path).execute(s, scope, **args)
        restarted = FictionalDurableStore(path)
        second = restarted.execute(s, scope, **args)
        out = {'synthetic': True, 'first_receipt': first,
               'after_restart': second, 'stored_receipts': restarted.receipt_count(),
               'real_external_actions': 0,
               'identity_authentication': 'TBD', 'real_connector_idempotency': 'TBD'}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if not first['idempotent_replay'] and second['idempotent_replay'] and out['stored_receipts'] == 1 else 1


if __name__ == '__main__':
    raise SystemExit(main())
