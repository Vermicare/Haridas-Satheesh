"""Adversarial equivalence tests; fictional fixtures only."""
import datetime as dt
import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path
from retail_gate import EvidenceError, benchmark
from retail_sqlite import benchmark_sqlite


def fake(i, store=1, product=2, start=dt.date(2024, 1, 1)):
    flags = [0]*24
    if i % 5 == 0:
        flags[11] = 1
    sales = [0.0]*24
    sales[8] = float(1 + (i % 7))
    return {"store_id": store, "product_id": product,
            "dt": (start + dt.timedelta(days=i)).isoformat(),
            "hours_sale": sales, "hours_stock_status": flags,
            "stock_hour6_22_cnt": sum(flags[6:22])}


class DiskBackedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fictional.jsonl"

    def write(self, rows):
        self.path.write_text("".join(json.dumps(x, sort_keys=True)+"\n" for x in rows), encoding="utf-8")

    def test_identical_frozen_report_on_shuffled_multi_series(self):
        rows = [fake(i, store=s, product=p) for s,p in [(3,1),(1,2),(1,10)] for i in range(84)]
        random.Random(813).shuffle(rows)
        self.write(rows)
        self.assertEqual(benchmark(self.path, synthetic=True), benchmark_sqlite(self.path, synthetic=True))

    def test_two_runs_byte_identical(self):
        self.write([fake(i) for i in range(84)])
        a = json.dumps(benchmark_sqlite(self.path, synthetic=True), sort_keys=True).encode()
        b = json.dumps(benchmark_sqlite(self.path, synthetic=True), sort_keys=True).encode()
        self.assertEqual(hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())

    def test_duplicate_rejected_even_when_far_apart(self):
        self.write([fake(i) for i in range(84)] + [fake(0)])
        with self.assertRaisesRegex(EvidenceError, "duplicate"):
            benchmark_sqlite(self.path, synthetic=True)

    def test_future_gap_does_not_select_next_cohort(self):
        rows = [fake(i, store=1) for i in range(84) if i != 60]
        rows += [fake(i, store=9) for i in range(84)]
        self.write(rows)
        with self.assertRaisesRegex(EvidenceError, "preselected cohort"):
            benchmark_sqlite(self.path, synthetic=True)

    def test_empty_and_corrupt_rejected(self):
        self.path.write_text("")
        with self.assertRaisesRegex(EvidenceError, "empty"):
            benchmark_sqlite(self.path, synthetic=True)
        self.path.write_text("{bad}\n")
        with self.assertRaisesRegex(EvidenceError, "malformed"):
            benchmark_sqlite(self.path, synthetic=True)

    def test_external_provenance_and_hash_gate(self):
        self.write([fake(i) for i in range(84)])
        with self.assertRaisesRegex(EvidenceError, "requires"):
            benchmark_sqlite(self.path)
        with self.assertRaisesRegex(EvidenceError, "checksum"):
            benchmark_sqlite(self.path, "0"*64, "https://example.org")
        hash_value = hashlib.sha256(self.path.read_bytes()).hexdigest()
        report = benchmark_sqlite(self.path, hash_value, "https://example.org")
        self.assertEqual(report["data_kind"], "EXTERNAL_SNAPSHOT_ORIGIN_NOT_INDEPENDENTLY_ATTESTED")

    def test_1000_series_smoke_identical(self):
        rows = [fake(i, store=s, product=2) for s in range(1000) for i in range(77)]
        random.Random(11).shuffle(rows)
        self.write(rows)
        self.assertEqual(benchmark(self.path, synthetic=True),
                         benchmark_sqlite(self.path, synthetic=True))


if __name__ == "__main__":
    unittest.main()
