"""Disk-backed deterministic JSONL benchmark ingestion.

Source URI and input SHA-256 are declarations, not independent origin attestation.
Frozen forecast/metric logic is reused from retail_gate.py.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sqlite3
import tempfile
from pathlib import Path
from contextlib import closing
from retail_gate import EvidenceError, HORIZON, ORIGINS, evaluate, parse_row, sha256_file


def _ingest(conn, path):
    conn.execute("""CREATE TABLE daily (
        store TEXT NOT NULL, product TEXT NOT NULL, day TEXT NOT NULL,
        y REAL NOT NULL, censored INTEGER NOT NULL, stockout_hours INTEGER NOT NULL,
        PRIMARY KEY(store, product, day)) WITHOUT ROWID""")
    seen = 0
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise EvidenceError(f"line {n}: malformed JSON") from e
            row = parse_row(obj, n)
            try:
                conn.execute("INSERT INTO daily VALUES (?,?,?,?,?,?)",
                             (*row["key"], row["day"].isoformat(), row["y"],
                              int(row["censored"]), row["stockout_hours"]))
            except sqlite3.IntegrityError as e:
                raise EvidenceError(f"line {n}: duplicate store/product/date") from e
            seen += 1
    if not seen:
        raise EvidenceError("empty dataset")
    conn.commit()


def _select(conn):
    """Choose using only first 42 training days; fail on later gaps."""
    cur = conn.execute("SELECT DISTINCT store, product FROM daily ORDER BY store, product")
    for key in cur:
        training = conn.execute("""SELECT day, censored FROM daily
            WHERE store=? AND product=? ORDER BY day LIMIT ?""",
            (*key, ORIGINS[0])).fetchall()
        if len(training) < ORIGINS[0]:
            continue
        dates = [dt.date.fromisoformat(x[0]) for x in training]
        if any((b-a).days != 1 for a,b in zip(dates, dates[1:])):
            continue
        if not any(x[1] for x in training) or not any(not x[1] for x in training):
            continue
        raw = conn.execute("""SELECT day, y, censored, stockout_hours FROM daily
            WHERE store=? AND product=? ORDER BY day""", key).fetchall()
        rows = [{"key": key, "day": dt.date.fromisoformat(day), "y": y,
                 "censored": bool(censored), "stockout_hours": stockout_hours}
                for day,y,censored,stockout_hours in raw]
        if len(rows) < max(ORIGINS) + HORIZON or any(
            (b["day"]-a["day"]).days != 1 for a,b in zip(rows, rows[1:])
        ):
            raise EvidenceError("preselected cohort has incomplete held-out horizon; do not select replacement using test data")
        return key, rows
    raise EvidenceError("no eligible first-42-day training cohort; do not relax selection")


def benchmark_sqlite(path, expected_hash=None, source_uri=None, synthetic=False):
    """Same report as in-memory benchmark; SQLite temp storage, bounded application RAM."""
    if not synthetic and (not expected_hash or not source_uri):
        raise EvidenceError("external input requires source URI and pinned local SHA-256")
    actual = sha256_file(path)
    if expected_hash and actual.lower() != expected_hash.lower():
        raise EvidenceError("source checksum mismatch")
    with tempfile.TemporaryDirectory(prefix="retail_evidence_") as folder:
        with closing(sqlite3.connect(str(Path(folder) / "daily.sqlite"))) as conn:
            _ingest(conn, path)
            key, rows = _select(conn)
    return {"schema_version": "1.0",
            "data_kind": "FICTIONAL_TEST_ONLY" if synthetic else
                         "EXTERNAL_SNAPSHOT_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",
            "source_uri": "fictional fixture" if synthetic else source_uri,
            "input_sha256": actual, "selected_store_id": key[0],
            "selected_product_id": key[1],
            "selection_rule": "lexicographically first consecutive 42-day training series with stockout and nonstockout; reject if its 77-day held-out coverage is incomplete",
            "business_hours": "06:00-21:59", "folds": evaluate(rows),
            "latent_demand_ground_truth": "UNAVAILABLE",
            "ranking_intervention_outcome": "TBD",
            "maturity": "Research / Architecture — unchanged"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--source-sha256")
    p.add_argument("--source-uri")
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = benchmark_sqlite(a.input, a.source_sha256, a.source_uri, a.synthetic)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['data_kind']}: {len(report['folds'])} folds, report={a.output}")


if __name__ == "__main__":
    main()
