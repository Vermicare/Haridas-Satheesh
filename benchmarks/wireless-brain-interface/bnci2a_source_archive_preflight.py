#!/usr/bin/env python3
"""Fail-closed, no-extraction provenance gate for BCI IV 2a GDF ZIP.

This checks ZIP container integrity and GDF file identity, not EEG events,
trial counts, labels, session authenticity, model performance or clinical safety.
No network access or evaluation-label ingestion is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

EXPECTED = {f"A{s:02d}{session}.gdf" for s in range(1, 10) for session in ("T", "E")}
MAX_GDF_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED = 3 * 1024 * 1024 * 1024
MAX_COMPRESSION_RATIO = 2000
CHUNK = 1024 * 1024
SAFE_DOCUMENT_SUFFIXES = {".txt", ".md", ".pdf"}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_archive(path: Path, source_url: str = "TBD", *, max_gdf_bytes: int = MAX_GDF_BYTES) -> dict:
    """Inspect source bytes in-place, streaming. Never extract or read E labels."""
    if not path.is_file():
        raise ValueError("source archive does not exist")
    if not isinstance(source_url, str) or not source_url or len(source_url) > 1000:
        raise ValueError("invalid source URL declaration")
    gdf = {}
    docs = []
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if not entries:
                raise ValueError("empty archive")
            total = 0
            seen_paths = set()
            for info in entries:
                name = info.filename
                if (not name or "\\" in name or "\x00" in name or name.startswith("/")
                        or re.match(r"^[A-Za-z]:", name)):
                    raise ValueError("unsafe archive path")
                parts = PurePosixPath(name).parts
                if any(part in (".", "..") for part in name.split("/")):
                    raise ValueError("unsafe archive traversal")
                canonical = "/".join(parts).casefold()
                if canonical in seen_paths:
                    raise ValueError("duplicate archive member path")
                seen_paths.add(canonical)
                if info.flag_bits & 1:
                    raise ValueError("encrypted member")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("symlink member")
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise ValueError("unsupported compression")
                if info.is_dir():
                    continue
                total += info.file_size
                if total > MAX_ARCHIVE_UNCOMPRESSED:
                    raise ValueError("uncompressed archive exceeds safety limit")
                if info.file_size > max_gdf_bytes:
                    raise ValueError("member exceeds size limit")
                if info.file_size > MAX_COMPRESSION_RATIO * max(1, info.compress_size):
                    raise ValueError("implausible compression ratio")
                basename = parts[-1]
                if basename in EXPECTED:
                    if basename in gdf:
                        raise ValueError("duplicate GDF session")
                    digest = hashlib.sha256()
                    first = b""
                    count = 0
                    with archive.open(info) as stream:
                        for block in iter(lambda: stream.read(CHUNK), b""):
                            if not first:
                                first = block[:16]
                            count += len(block)
                            if count > max_gdf_bytes:
                                raise ValueError("GDF exceeds streamed size limit")
                            digest.update(block)
                    if count != info.file_size:
                        raise ValueError("GDF size mismatch")
                    if not first.startswith(b"GDF"):
                        raise ValueError("missing GDF signature")
                    gdf[basename] = {"archive_member": name, "bytes": count,
                                     "sha256": digest.hexdigest(), "zip_crc32": f"{info.CRC:08x}"}
                elif basename.lower().endswith(".gdf"):
                    raise ValueError("unexpected GDF file")
                elif PurePosixPath(basename).suffix.lower() in SAFE_DOCUMENT_SUFFIXES:
                    docs.append(name)
                else:
                    # In particular, never ingest test-session class labels (.mat).
                    raise ValueError("unexpected non-document member; label firewall")
            if set(gdf) != EXPECTED:
                missing = sorted(EXPECTED - set(gdf))
                raise ValueError(f"missing expected GDF sessions: {missing}")
    except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, EOFError, OSError) as exc:
        raise ValueError(f"archive integrity failure: {type(exc).__name__}") from exc
    return {
        "status": "ARCHIVE INTEGRITY ONLY — NO EEG EVENTS OR LABELS READ",
        "dataset": "BCI Competition IV dataset 2a / BNCI2014_001",
        "source_url_declared_unverified": source_url,
        "source_archive_sha256": _sha256_file(path),
        "source_archive_bytes": path.stat().st_size,
        "gdf_file_count": len(gdf),
        "gdf": dict(sorted(gdf.items())),
        "additional_document_members": sorted(docs),
        "evaluation_labels_accessed": False,
        "trial_counts_verified": False,
        "real_eeg_signal_or_outcome_metrics": "TBD",
        "source_authenticity": "TBD; hash alone does not authenticate publisher",
        "loader_version": "TBD",
        "python_version": sys.version.split()[0],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-url", default="TBD")
    args = parser.parse_args()
    try:
        report = inspect_archive(args.archive, args.source_url)
    except ValueError as exc:
        parser.exit(2, f"PREFLIGHT FAIL: {exc}\n")
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ARCHIVE INTEGRITY PASS; EEG events, labels and model results remain unverified")


if __name__ == "__main__":
    main()
