"""Pinned-parquet to canonical JSONL preflight for the retail research harness.

No real dataset is bundled. A matching local SHA256 checks bytes, not publisher identity.
The pure-stdlib conversion core is tested with fictional rows; Parquet I/O requires pyarrow.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path

REQUIRED = ("store_id", "product_id", "dt", "hours_sale", "hours_stock_status", "stock_hour6_22_cnt")
SOURCE = "https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K"
PINNED_REVISION = "08c1fab7f9257bc73679d415d65d644165d351d4"
PUBLISHER_REPORTED_TRAIN_SHA256 = "6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d"


class ExportError(ValueError):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def normalized_row(row, line_no):
    """Strictly preserve only the evaluator's required fields; reject coercion."""
    if not isinstance(row, dict):
        raise ExportError("row %d: expected object" % line_no)
    missing = set(REQUIRED).difference(row)
    if missing:
        raise ExportError("row %d: missing %s" % (line_no, ",".join(sorted(missing))))
    for name in ("store_id", "product_id"):
        if type(row[name]) is not int or row[name] < 0:
            raise ExportError("row %d: invalid %s" % (line_no, name))
    day = row["dt"]
    if not isinstance(day, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ExportError("row %d: invalid date format" % line_no)
    try:
        if dt.date.fromisoformat(day).isoformat() != day:
            raise ValueError("noncanonical date")
    except ValueError as exc:
        raise ExportError("row %d: invalid date" % line_no) from exc
    sales = row["hours_sale"]
    status = row["hours_stock_status"]
    if not isinstance(sales, (list, tuple)) or len(sales) != 24:
        raise ExportError("row %d: hours_sale must contain 24 values" % line_no)
    if not isinstance(status, (list, tuple)) or len(status) != 24:
        raise ExportError("row %d: hours_stock_status must contain 24 values" % line_no)
    if any(type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in sales):
        raise ExportError("row %d: invalid sales value" % line_no)
    if any(type(x) is not int or x not in (0, 1) for x in status):
        raise ExportError("row %d: invalid stock flag" % line_no)
    count = row["stock_hour6_22_cnt"]
    if type(count) is not int or count != sum(status[6:22]):
        raise ExportError("row %d: stockout count mismatch" % line_no)
    return {"store_id": row["store_id"], "product_id": row["product_id"],
            "dt": day, "hours_sale": list(sales), "hours_stock_status": list(status),
            "stock_hour6_22_cnt": count}


def _publish_exclusive(staged_path, destination):
    """Atomically publish complete staged bytes without replacing an existing path.

    Staging and destination are in the same directory/filesystem. Hard-link
    creation fails if another writer created the destination after preflight.
    """
    try:
        os.link(staged_path, destination)
    except FileExistsError as exc:
        raise ExportError("refusing to overwrite an output or manifest created during export") from exc


def export_batches(batches, output_path, manifest_path, *, source_path,
                   expected_source_sha256, source_revision, pyarrow_version="TBD",
                   synthetic=False):
    """Stream batches with bounded memory, refuse overwrites, and record local hashes."""
    source_path, output_path, manifest_path = map(Path, (source_path, output_path, manifest_path))
    if output_path == manifest_path or output_path.exists() or manifest_path.exists():
        raise ExportError("refusing to overwrite an output or manifest")
    if not re.fullmatch(r"[a-f0-9]{40}", source_revision):
        raise ExportError("source revision must be an immutable 40-character commit SHA")
    if not re.fullmatch(r"[a-fA-F0-9]{64}", expected_source_sha256):
        raise ExportError("expected source SHA256 must contain 64 hex characters")
    source_hash = sha256_file(source_path)
    if source_hash != expected_source_sha256.lower():
        raise ExportError("local source SHA256 mismatch")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".retail_export_", suffix=".tmp", dir=str(output_path.parent))
    count = 0
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            for batch in batches:
                for raw in batch:
                    count += 1
                    row = normalized_row(raw, count)
                    out.write(json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
        if count == 0:
            raise ExportError("empty export")
        if sha256_file(source_path) != source_hash:
            raise ExportError("source changed during export; aborting")
        export_hash = sha256_file(temp_name)
        manifest = {
            "schema_version": "1.0", "data_kind": "FICTIONAL_TEST_ONLY" if synthetic else
                         "EXTERNAL_SNAPSHOT_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",
            "source_uri_declared": SOURCE, "source_revision_declared": source_revision,
            "local_source_sha256": source_hash, "export_sha256": export_hash,
            "export_rows": count, "export_fields": list(REQUIRED),
            "parquet_reader_version": pyarrow_version,
            "source_origin_independently_attested": False,
            "forecast_results": "TBD", "maturity_change": "NONE",
            "converter_contract": "ordered parquet row batches, 1024 rows per batch, strict 24-hour arrays; JSON sort_keys compact UTF-8 newline"
        }
        # Stage both outputs before committing either. Neither pre-existing file is replaced.
        fd2, temp_manifest = tempfile.mkstemp(prefix=".retail_manifest_", suffix=".tmp", dir=str(manifest_path.parent))
        try:
            with os.fdopen(fd2, "w", encoding="utf-8", newline="\n") as mf:
                mf.write(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
            _publish_exclusive(temp_name, output_path)
            try:
                _publish_exclusive(temp_manifest, manifest_path)
            except Exception:
                # Roll back our own published link, not an unrelated replacement.
                # A process crash between publishes can still leave an orphan
                # output; consumers must verify the manifest and its hashes.
                if output_path.exists() and os.path.samefile(temp_name, output_path):
                    output_path.unlink()
                raise
        finally:
            if os.path.exists(temp_manifest):
                os.unlink(temp_manifest)
        return manifest
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def parquet_batches(path, batch_size=1024):
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise ExportError("pyarrow required for actual parquet reading; install pinned dependency separately") from exc
    parquet = pq.ParquetFile(path)
    missing = set(REQUIRED).difference(parquet.schema_arrow.names)
    if missing:
        raise ExportError("parquet missing columns: " + ",".join(sorted(missing)))
    for batch in parquet.iter_batches(batch_size=batch_size, columns=list(REQUIRED)):
        yield batch.to_pylist()


def main():
    p = argparse.ArgumentParser(description="Pinned FreshRetailNet parquet to canonical JSONL")
    p.add_argument("--parquet", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--revision", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    args = p.parse_args()
    try:
        import pyarrow
    except ImportError as exc:
        raise SystemExit("pyarrow is required to read parquet; no real dataset export performed") from exc
    report = export_batches(parquet_batches(args.parquet), args.output, args.manifest,
                            source_path=args.parquet, expected_source_sha256=args.expected_sha256,
                            source_revision=args.revision, pyarrow_version=pyarrow.__version__)
    print("EXTERNAL_SNAPSHOT_ORIGIN_NOT_INDEPENDENTLY_ATTESTED rows=%d export_sha256=%s" %
          (report["export_rows"], report["export_sha256"]))


if __name__ == "__main__":
    main()
