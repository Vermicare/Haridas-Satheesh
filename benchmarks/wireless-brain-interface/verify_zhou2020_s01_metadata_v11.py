#!/usr/bin/env python3
"""Fail-closed, metadata-only Zhou2020 S01 provenance verifier.

This checks preserved GitHub Actions JSON, NOT original EEG archive authenticity.
No third-party packages, network, signal decoding or unsafe pickle loading.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

JSON_SHA256 = "4dd22f27bd72f21200976372fb238517b1affdd224d27b884afec4f69f61631b"
ZIP_SHA256 = "f174c606fd221012d08906bd375307e4d7f5eb8ac19ae0608f99a898e5cb3bd2"
SOURCE_ZIP_SHA256_REPORTED = "897c8316ac8130635821cab42d39b946dcedf54a582f3252bf028e190f294dbf"
PUBLISHER_MD5_REPORTED = "34867b4b27a8c91fd6fe010cbf4f9caa"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def inspect_json(raw):
    checks = {"preserved_json_sha256": sha256(raw) == JSON_SHA256,
              "preserved_json_length": len(raw) == 4185}
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        checks["json_parseable"] = False
        return checks
    checks["json_parseable"] = isinstance(data, dict)
    if not isinstance(data, dict):
        return checks
    expected = {
        "schema": "wbi-zhou2020-s01-transfer-v1.0",
        "source_record": "10.5281/zenodo.18988317",
        "archive": "S01.zip",
        "source_version": "v1",
        "status": "PASS_TRANSFER_AND_ZIP_STRUCTURE_ONLY",
        "zip_sha256": SOURCE_ZIP_SHA256_REPORTED,
        "publisher_md5_expected": PUBLISHER_MD5_REPORTED,
        "zip_md5_observed": PUBLISHER_MD5_REPORTED,
        "bytes_received": 1143862039,
        "bytes_expected": 1143862039,
        "member_count": 43,
        "zip_preflight_checks": 4141,
        "zip_preflight_status": "PASS",
        "raw_signal_uploaded": False,
        "npz_arrays_opened": False,
        "held_out_decoding": "NOT_PERFORMED",
        "clinical_validation": "NOT_PERFORMED",
        "original_ieee_equivalence": "TBD",
        "original_npz_authenticity": "TBD",
        "bids_event_mapping": "TBD",
        "publisher_transfer_md5_match": True,
    }
    checks["frozen_metadata_fields"] = all(type(data.get(k)) is type(v) and data.get(k) == v for k, v in expected.items())
    digests = data.get("npz_member_sha256")
    checks["43_unique_sorted_digest_strings"] = (
        isinstance(digests, list) and len(digests) == 43
        and all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for v in digests)
        and digests == sorted(set(digests))
    )
    return checks


def inspect_zip(path, preserved_json):
    checks = {}
    # Reject before decompression: only the exact, independently hashed 2,401-byte ZIP is admissible.
    checks["original_metadata_zip_size"] = path.stat().st_size == 2401
    if not checks["original_metadata_zip_size"]:
        return checks
    raw = path.read_bytes()
    checks["original_metadata_zip_sha256"] = sha256(raw) == ZIP_SHA256
    if not checks["original_metadata_zip_sha256"]:
        return checks
    try:
        with zipfile.ZipFile(path) as z:
            checks["single_expected_zip_member"] = z.namelist() == ["s01-metadata-only.json"]
            checks["zip_crc_pass"] = z.testzip() is None
            checks["zip_json_matches_preserved_bytes"] = z.read("s01-metadata-only.json") == preserved_json
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, RuntimeError):
        checks["zip_open_and_read"] = False
    return checks


def check_negative_controls(raw):
    mutations = [
        raw.replace(b'"TBD"', b'"PASS"', 1),
        raw.replace(b'"member_count": 43', b'"member_count": 44', 1),
        raw[:-1] + b" ",
    ]
    return len(set(mutations)) == 3 and all(
        mutated != raw and not all(inspect_json(mutated).values()) for mutated in mutations
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", type=Path, help="exact original 4,185-byte hosted metadata JSON")
    parser.add_argument("--zip", type=Path, help="optional original 2,401-byte GitHub Actions metadata ZIP")
    args = parser.parse_args()
    try:
        if args.json_path.stat().st_size > 4185:
            raise ValueError("JSON exceeds pinned 4,185-byte limit")
        raw = args.json_path.read_bytes()
        checks = inspect_json(raw)
        checks["three_mutation_negative_controls"] = check_negative_controls(raw)
        if args.zip:
            checks.update(inspect_zip(args.zip, raw))
    except (OSError, ValueError) as exc:
        print(f"FAIL: input unavailable or invalid: {exc}", file=sys.stderr)
        return 1
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    passed = sum(checks.values())
    print(f"{'PASS' if passed == len(checks) else 'FAIL'} {passed}/{len(checks)} metadata-only checks")
    print("LIMIT: does not independently reacquire/hash 1.14 GB EEG source; no decoding, event validation or clinical claim")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
