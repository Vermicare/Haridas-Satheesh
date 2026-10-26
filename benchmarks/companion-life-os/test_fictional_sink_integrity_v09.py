"""v0.9 negative controls for the independent fictional SQLite sink.

No network, real identity, private account, or external side effect.
The source implementation is intentionally unchanged for the red run.
"""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from fictional_outbox_v07 import FictionalIdempotentSink, OutboxContractError


class SinkIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fictional-sink.sqlite3"
        self.sink = FictionalIdempotentSink(self.path)
        self.valid = {"nonce": "fictional-n1", "decision": "D1",
                      "action": "update-fictional-due-date", "synthetic": True}

    def test_valid_sink_effect_and_idempotent_replay(self):
        first = self.sink.apply(self.valid)
        second = FictionalIdempotentSink(self.path).apply(self.valid)
        self.assertFalse(first["sink_replay"])
        self.assertTrue(second["sink_replay"])
        self.assertEqual(self.sink.count(), 1)

    def test_sink_rejects_missing_action_without_recording_effect(self):
        invalid = dict(self.valid)
        del invalid["action"]
        with self.assertRaises(OutboxContractError):
            self.sink.apply(invalid)
        self.assertEqual(self.sink.count(), 0)

    def test_sink_rejects_blank_decision_without_recording_effect(self):
        invalid = dict(self.valid, decision="   ")
        with self.assertRaises(OutboxContractError):
            self.sink.apply(invalid)
        self.assertEqual(self.sink.count(), 0)

    def test_sink_rejects_corrupt_persisted_ack_on_replay(self):
        self.sink.apply(self.valid)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE simulated_deliveries SET ack_json=? WHERE nonce=?", (
                json.dumps({"nonce": self.valid["nonce"], "digest": "wrong",
                            "synthetic": True, "simulated_actions": 1,
                            "external_actions": 0}), self.valid["nonce"]))
        with self.assertRaises(OutboxContractError):
            FictionalIdempotentSink(self.path).apply(self.valid)
        self.assertEqual(self.sink.count(), 1)


if __name__ == "__main__":
    unittest.main()
