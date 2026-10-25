"""30-second fictional-only correction lineage demo; zero external actions."""
import json
import sqlite3
from contextlib import closing
import tempfile
from pathlib import Path
from correction_ledger_v05 import FictionalCorrectionLedger
from test_correction_ledger_v05 import ORIGINAL, request


def main():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'fixture.sqlite3'
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('CREATE TABLE receipts (nonce TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, receipt_json TEXT NOT NULL)')
            db.execute('INSERT INTO receipts VALUES (?,?,?)',
                       (ORIGINAL['nonce'], 'fictional-seed-digest', json.dumps(ORIGINAL, sort_keys=True)))
        ledger = FictionalCorrectionLedger(path)
        kwargs = {'principal': 'fictional-user', 'now': '2026-10-01T10:30:00Z',
                  'trusted_principals': {'fictional-user'}}
        first = ledger.record(ORIGINAL['nonce'], request(), **kwargs)
        retry = FictionalCorrectionLedger(path).record(ORIGINAL['nonce'], request(), **kwargs)
        with closing(sqlite3.connect(path)) as db, db:
            original_unchanged = json.loads(db.execute('SELECT receipt_json FROM receipts').fetchone()[0]) == ORIGINAL
        result = {'synthetic': True, 'first': first, 'retry_after_restart': retry,
                  'correction_events': ledger.correction_count(),
                  'original_receipt_unchanged': original_unchanged,
                  'real_external_actions': 0, 'identity_authentication': 'TBD',
                  'trusted_clock': 'TBD', 'reviewer_burden': 'TBD'}
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if not first['idempotent_replay'] and retry['idempotent_replay'] and original_unchanged else 1


if __name__ == '__main__':
    raise SystemExit(main())
