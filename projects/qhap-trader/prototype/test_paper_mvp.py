"""Invariant tests with synthetic bars; do not treat test P&L as market evidence."""
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_mvp import Bar, parse_bars, run_replay


def synthetic_bars(cause_signal=False, omit_1500=False, gap=False):
    t = datetime(2026, 11, 2, 9, 15, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    out = []
    for n in range(346):  # 09:15 to 15:00 inclusive
        ts = t + timedelta(minutes=n)
        if omit_1500 and ts.hour == 15: break
        if gap and n == 13: continue
        close = 100.0 + (1 if cause_signal and n == 11 else 0)
        volume = 5000 if cause_signal and n == 11 else 100
        out.append(Bar(ts, "TEST", 100, max(100.5, close), 99.8, close, volume))
    return out


class InvariantTests(unittest.TestCase):
    def test_never_places_live_orders_and_no_signal(self):
        result = run_replay(synthetic_bars())
        self.assertEqual(result["mode"], "OFFLINE_PAPER_ONLY")
        self.assertEqual(result["status"], "SIMULATED_COMPLETE")
        self.assertFalse([e for e in result["journal"] if e["event"] == "PAPER_ENTRY"])

    def test_next_bar_entry_only(self):
        result = run_replay(synthetic_bars(cause_signal=True))
        signals = [e for e in result["journal"] if e["event"] == "CANDIDATE"]
        entries = [e for e in result["journal"] if e["event"] == "PAPER_ENTRY"]
        self.assertTrue(signals)
        self.assertTrue(entries)
        self.assertGreater(entries[0]["time"], signals[0]["time"])
        self.assertEqual(result["status"], "SIMULATED_COMPLETE")

    def test_gap_halts_entries(self):
        result = run_replay(synthetic_bars(cause_signal=True, gap=True))
        self.assertEqual(result["status"], "INCOMPLETE_OR_FAILED")
        self.assertTrue(any(e["event"] == "HALT" for e in result["journal"]))

    def test_missing_close_never_certifies_complete(self):
        result = run_replay(synthetic_bars(omit_1500=True))
        self.assertEqual(result["status"], "INCOMPLETE_OR_FAILED")

    def test_reject_naive_timestamps(self):
        with TemporaryDirectory() as d:
            path = Path(d) / "bars.csv"
            path.write_text("timestamp,symbol,open,high,low,close,volume\n"
                            "2026-11-02T09:15:00,TEST,100,101,99,100,100\n")
            with self.assertRaises(ValueError): parse_bars(path)


if __name__ == "__main__":
    unittest.main()
