"""Fictional-only negative controls for input mutation between hashing and ingestion.

A checksum computed before ingestion is not sufficient to bind a report to
bytes actually read. These tests never access the publisher's Parquet dataset.
"""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import retail_gate
import retail_sqlite


def fictional_row(i):
    flags = [0] * 24
    if i % 5 == 0:
        flags[11] = 1
    sales = [0.0] * 24
    sales[8] = float(1 + i % 7)
    return {"store_id": 1, "product_id": 2,
            "dt": (dt.date(2024, 1, 1) + dt.timedelta(days=i)).isoformat(),
            "hours_sale": sales, "hours_stock_status": flags,
            "stock_hour6_22_cnt": sum(flags[6:22])}


class SourceIntegrityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "FICTIONAL.jsonl"
        self.path.write_text("".join(json.dumps(fictional_row(i), sort_keys=True) + "\n"
                                     for i in range(84)), encoding="utf-8")

    def mutate_after_hash(self):
        rows = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()]
        rows[43]["hours_sale"][8] = 999.0
        self.path.write_text("".join(json.dumps(row, sort_keys=True) + "\n"
                                     for row in rows), encoding="utf-8")

    def test_in_memory_rejects_post_hash_input_mutation(self):
        original_read = retail_gate.read_jsonl

        def change_then_read(path):
            self.mutate_after_hash()
            return original_read(path)

        with patch.object(retail_gate, "read_jsonl", side_effect=change_then_read):
            with self.assertRaisesRegex(retail_gate.EvidenceError, "source changed"):
                retail_gate.benchmark(self.path, synthetic=True)

    def test_sqlite_rejects_post_hash_input_mutation(self):
        original_ingest = retail_sqlite._ingest

        def change_then_ingest(conn, path):
            self.mutate_after_hash()
            return original_ingest(conn, path)

        with patch.object(retail_sqlite, "_ingest", side_effect=change_then_ingest):
            with self.assertRaisesRegex(retail_gate.EvidenceError, "source changed"):
                retail_sqlite.benchmark_sqlite(self.path, synthetic=True)


if __name__ == "__main__":
    unittest.main()
