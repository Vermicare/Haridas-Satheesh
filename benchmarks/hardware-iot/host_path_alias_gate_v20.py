#!/usr/bin/env python3
"""Read-only path-alias/size preflight before the existing IoT v1.9 gate.

Fictional software evidence only. Path checks are not race-free, and neither
these checks nor matching hashes authenticate a physical sensor or clock.
Always run the stronger v0.7 host_bundle_chain.py independently.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from host_byte_exposure_gate_v19 import audit as audit_v19

VERSION = "iot-host-path-alias-review-v20"
MAX_MANIFEST_BYTES = 1_000_000
MAX_RAW_BYTES = 10_000_000
MAX_CSV_BYTES = 5_000_000


def audit(capture_dir, bundle_dir):
    cap, bundle = Path(capture_dir), Path(bundle_dir)
    result = {
        "schema_version": VERSION,
        "status": "REVIEW_REQUIRED",
        "problems": [],
        "physical_origin_authenticated": False,
        "physical_time_attested": False,
        "flashed_firmware_authenticated": False,
        "race_free_file_identity": False,
        "required_next_gate": "Independently run host_bundle_chain.py v0.7 and serial_bundle.py verify; review private raw capture and actual flashed firmware.",
    }
    try:
        for label, directory in (("CAPTURE", cap), ("BUNDLE", bundle)):
            if directory.is_symlink() or not directory.is_dir():
                raise ValueError(label + "_DIRECTORY_MISSING_OR_SYMLINK")
        if cap.resolve() == bundle.resolve():
            raise ValueError("CAPTURE_AND_BUNDLE_ARE_SAME_DIRECTORY")
        required = (
            (cap / "capture_manifest.json", MAX_MANIFEST_BYTES),
            (cap / "raw_serial.log", MAX_RAW_BYTES),
            (bundle / "manifest.json", MAX_MANIFEST_BYTES),
            (bundle / "raw_serial.log", MAX_RAW_BYTES),
            (bundle / "samples.csv", MAX_CSV_BYTES),
        )
        for path, limit in required:
            if path.is_symlink() or not path.is_file():
                raise ValueError("MISSING_NONREGULAR_OR_SYMLINK_" + path.name)
            if path.stat().st_size > limit:
                raise ValueError("FILE_OVER_DECLARED_SIZE_LIMIT_" + path.name)
        prior = audit_v19(cap, bundle)
        result["v19_status"] = prior["status"]
        result["v18_status"] = prior["v18_status"]
        result["host_byte_exposure_s"] = prior["host_byte_exposure_s"]
        if prior["status"] != "HOST_BYTE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED":
            result["problems"].append("V19_GATE_NOT_ACCEPTED")
            result["problems"].extend(prior["problems"])
        else:
            result["status"] = "PATHS_REGULAR_BOUNDED_ORIGIN_UNVERIFIED"
            result["host_raw_sha256"] = prior["host_raw_sha256"]
    except (OSError, ValueError) as exc:
        result["problems"].append(str(exc))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("bundle_dir", type=Path)
    args = parser.parse_args()
    result = audit(args.capture_dir, args.bundle_dir)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if result["status"] == "PATHS_REGULAR_BOUNDED_ORIGIN_UNVERIFIED" else 2)


if __name__ == "__main__":
    main()
