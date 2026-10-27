#!/usr/bin/env python3
"""Read-only upstream byte fingerprint for BNCI2014_001 A01T.mat.

Streams one public upstream MAT file to SHA-256 without storing EEG samples
or evaluation labels. NOT a classifier or clinical evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

SOURCE_URL = "https://bnci-horizon-2020.eu/database/data-sets/001-2014/A01T.mat"
ALLOWED_HOSTS = frozenset({"bnci-horizon-2020.eu", "lampx.tugraz.at"})
MAX_BYTES = 100 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024


def validate_source_url(url: str) -> None:
    """Reject unexpected redirect destinations and other source file IDs."""
    if not isinstance(url, str):
        raise ValueError("source URL must be a string")
    parts = urlparse(url)
    if (parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS
            or parts.username or parts.password or parts.port is not None
            or parts.query or parts.fragment
            or parts.path not in ("/database/data-sets/001-2014/A01T.mat",
                                  "/~bci/database/001-2014/A01T.mat")):
        raise ValueError("source URL is outside the pinned publisher route")
    if parts.hostname == "bnci-horizon-2020.eu" and parts.path != "/database/data-sets/001-2014/A01T.mat":
        raise ValueError("unexpected BNCI path")
    if parts.hostname == "lampx.tugraz.at" and parts.path != "/~bci/database/001-2014/A01T.mat":
        raise ValueError("unexpected Graz path")


class PinnedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_source_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fingerprint_stream(stream, *, final_url: str, declared_length: int | None = None) -> dict:
    """Fingerprint bytes without writing a local data file or reading labels."""
    validate_source_url(final_url)
    if declared_length is not None and (declared_length <= 0 or declared_length > MAX_BYTES):
        raise ValueError("declared source size outside bound")
    sha = hashlib.sha256()
    first = b""
    size = 0
    while True:
        block = stream.read(CHUNK_BYTES)
        if not block:
            break
        if not isinstance(block, bytes):
            raise ValueError("source stream returned non-bytes")
        if len(first) < 128:
            first += block[:128 - len(first)]
        size += len(block)
        if size > MAX_BYTES:
            raise ValueError("source exceeds size limit")
        sha.update(block)
    if declared_length is not None and size != declared_length:
        raise ValueError("incomplete source transfer")
    if first.startswith(b"MATLAB 5.0 MAT-file"):
        file_format = "MATLAB_5"
    elif first.startswith(b"\x89HDF\r\n\x1a\n"):
        file_format = "HDF5_MAT_7_3"
    else:
        raise ValueError("unexpected source signature; do not interpret as EEG")
    if size < 128:
        raise ValueError("truncated source header")
    return {
        "dataset": "BNCI2014_001",
        "file": "A01T.mat",
        "provider": "BNCI Horizon 2020 / Graz TU",
        "publisher_source_url": SOURCE_URL,
        "resolved_source_url": final_url,
        "source_format": file_format,
        "source_bytes": size,
        "source_sha256": sha.hexdigest(),
        "sha256_is_publisher_authenticated": False,
        "read_only_streamed_source": True,
        "raw_eeg_or_labels_saved": False,
        "session_E_labels_accessed": False,
        "trial_counts_verified": False,
        "decoding_metrics": "TBD",
        "license_declared_by_bnci_catalog": "CC BY-ND 4.0; review terms before any redistribution",
        "research_stage": "Research / Simulation; unchanged",
    }


def probe() -> dict:
    opener = build_opener(PinnedRedirect())
    req = Request(SOURCE_URL, headers={"User-Agent": "WBI-evidence-source-probe/0.1", "Accept-Encoding": "identity"})
    with opener.open(req, timeout=60) as response:
        final_url = response.geturl()
        validate_source_url(final_url)
        if response.status != 200:
            raise ValueError("source did not return HTTP 200 full content")
        length_str = response.headers.get("Content-Length")
        if length_str is not None and (not length_str.isascii() or not length_str.isdecimal()):
            raise ValueError("invalid source Content-Length")
        declared_length = int(length_str) if length_str is not None else None
        report = fingerprint_stream(response, final_url=final_url, declared_length=declared_length)
    report["probed_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["python_version"] = platform.python_version()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional path for metadata-only JSON; never contains EEG samples")
    args = parser.parse_args()
    try:
        report = probe()
    except Exception as exc:
        print(f"SOURCE_PROBE_FAILED: {type(exc).__name__}: {str(exc)[:160]}", file=sys.stderr)
        return 2
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
