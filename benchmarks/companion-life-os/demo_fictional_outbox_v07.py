"""Reproducible fictional 45-second presentation: crash-window retry, no real action."""
import json
import tempfile
from pathlib import Path

from authorization_store_v03 import FictionalDurableStore
from fictional_outbox_v07 import FictionalOutbox, FictionalIdempotentSink
from test_actual_receipt_integration_v06 import fictional_scenario


def main():
    with tempfile.TemporaryDirectory() as directory:
        receipt_db = Path(directory) / 'receipt.sqlite3'
        sink_db = Path(directory) / 'sink.sqlite3'
        scenario = fictional_scenario()
        receipt = FictionalDurableStore(receipt_db).execute(
            scenario, scenario['authorization']['scope'],
            principal='fictional-user', now='2026-10-01T10:30:00Z',
            trusted_principals={'fictional-user'})
        outbox = FictionalOutbox(receipt_db)
        sink = FictionalIdempotentSink(sink_db)
        outbox.stage(receipt['nonce'])
        try:
            outbox.dispatch(receipt['nonce'], sink, failure_point='after_sink_before_ack')
        except RuntimeError as exc:
            assert 'after sink before outbox ack' in str(exc)
        before = {'outbox_status': outbox.status(receipt['nonce']),
                  'simulated_sink_rows': sink.count()}
        replay = FictionalOutbox(receipt_db).dispatch(
            receipt['nonce'], FictionalIdempotentSink(sink_db))
        after = {'outbox_status': outbox.status(receipt['nonce']),
                 'simulated_sink_rows': sink.count(),
                 'sink_idempotent_replay': replay['sink_replay']}
        result = {'synthetic': True, 'external_actions': 0,
                  'source': 'v0.3-generated fictional authorization receipt',
                  'crash_window': 'after sink commit, before outbox ack',
                  'before_retry': before, 'after_retry': after,
                  'not_proven': ['external exactly-once', 'authenticated consent',
                                 'real task update', 'reversal', 'tamper resistance']}
        assert before == {'outbox_status': 'pending', 'simulated_sink_rows': 1}
        assert after == {'outbox_status': 'acked', 'simulated_sink_rows': 1,
                         'sink_idempotent_replay': True}
        print(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
