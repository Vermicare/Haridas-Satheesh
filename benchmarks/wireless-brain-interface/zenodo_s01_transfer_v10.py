#!/usr/bin/env python3
"""Bounded one-subject public EEG ZIP transfer; metadata-only report.

No EEG parsing, no extraction, no pickle, no publication of original data.
MD5 confirms publisher transfer consistency, not source authenticity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

from zenodo_archive_preflight_v09 import audit

URL = "https://zenodo.org/records/18988317/files/S01.zip?download=1"
EXPECTED_BYTES = 1_143_862_039  # observed from Zenodo file response 2026-10-30; independently checked at run
EXPECTED_MD5 = "34867b4b27a8c91fd6fe010cbf4f9caa"
MAX_BYTES = 1_250_000_000
SCHEMA = "wbi-zhou2020-s01-transfer-v1.0"


def transfer_and_audit(opener=None, expected_bytes=EXPECTED_BYTES,
                       expected_md5=EXPECTED_MD5, max_bytes=MAX_BYTES):
    """Download to an ephemeral file, fail closed, and return only safe metadata.

    `opener` permits entirely fictional network-free unit tests.
    """
    result = {
        "schema": SCHEMA, "status": "FAIL", "source_record": "10.5281/zenodo.18988317",
        "source_version": "v1", "source_url": URL, "archive": "S01.zip",
        "publisher_md5_expected": expected_md5, "bytes_expected": expected_bytes,
        "raw_signal_uploaded": False, "npz_arrays_opened": False,
        "original_ieee_equivalence": "TBD", "original_npz_authenticity": "TBD",
        "bids_event_mapping": "TBD", "held_out_decoding": "NOT_PERFORMED",
        "clinical_validation": "NOT_PERFORMED",
        "limitation": "Transfer integrity and ZIP structure only; no EEG or clinical validation",
    }
    if not isinstance(expected_bytes, int) or expected_bytes <= 0 or expected_bytes > max_bytes:
        result["failure_code"] = "invalid_expected_size"
        return result
    if not isinstance(expected_md5, str) or len(expected_md5) != 32 or any(c not in "0123456789abcdef" for c in expected_md5):
        result["failure_code"] = "invalid_expected_md5"
        return result
    open_url = opener or urllib.request.urlopen
    with tempfile.TemporaryDirectory(prefix="wbi-s01-original-private-") as private:
        archive = Path(private) / "S01.zip"
        md5, sha256 = hashlib.md5(), hashlib.sha256()
        count = 0
        try:
            with open_url(URL, timeout=90) as response, archive.open("xb") as output:
                declared = response.headers.get("Content-Length") if hasattr(response, "headers") else None
                if declared is not None:
                    try:
                        header_size = int(declared)
                    except ValueError:
                        result["failure_code"] = "invalid_content_length"
                        return result
                    if header_size != expected_bytes:
                        result["failure_code"] = "content_length_disagrees_with_pinned_size"
                        return result
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > max_bytes or count > expected_bytes:
                        result["failure_code"] = "transfer_exceeded_pinned_limit"
                        return result
                    md5.update(chunk)
                    sha256.update(chunk)
                    output.write(chunk)
        except (OSError, ValueError, TimeoutError) as exc:
            # Avoid publishing temporary paths, redirected signed URLs or response bodies.
            result["failure_code"] = "download_error_" + type(exc).__name__
            return result
        result["bytes_received"] = count
        result["zip_sha256"] = sha256.hexdigest()
        result["zip_md5_observed"] = md5.hexdigest()
        if count != expected_bytes:
            result["failure_code"] = "incomplete_transfer"
            return result
        if md5.hexdigest() != expected_md5:
            result["failure_code"] = "publisher_md5_mismatch"
            return result
        result["publisher_transfer_md5_match"] = True
        check = audit(archive, expected_md5)
        result["zip_preflight_status"] = check["status"]
        result["zip_preflight_checks"] = len(check["checks"])
        if check["status"] != "PASS":
            result["failure_code"] = "zip_preflight_failed"
            # Do not emit paths from potentially malformed ZIP member names.
            result["failed_check_count"] = sum(not c["pass"] for c in check["checks"])
            return result
        result["member_count"] = check["member_count"]
        result["total_uncompressed_bytes"] = check["total_uncompressed_bytes"]
        # ZIP member paths are not emitted; hashes can support independent audit
        # without publishing signal contents or filename-derived identifiers.
        result["npz_member_sha256"] = sorted(m["sha256"] for m in check["members"])
        result["status"] = "PASS_TRANSFER_AND_ZIP_STRUCTURE_ONLY"
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", required=True, help="aggregate-only JSON output")
    args = parser.parse_args()
    report = transfer_and_audit()
    Path(args.json_out).write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("npz_member_sha256",)}, sort_keys=True))
    return 0 if report["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
