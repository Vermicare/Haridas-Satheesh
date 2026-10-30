#!/usr/bin/env python3
"""Supplemental host-byte exposure review for IoT v1.8; fictional tests only.

Read-only structural safeguard. Not physical sensor, clock, firmware, or
measurement attestation. The existing v0.7 host_bundle_chain.py independently
checks host exposure AND device telemetry; run that chain too.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from capture_chain_v18 import check_chain, _json, _number

VERSION = "iot-host-byte-exposure-review-v19"
MIN_SPAN_S = 600.0  # existing v0.7 policy; not a physical time attestation


def audit(capture_dir, bundle_dir):
    base = check_chain(capture_dir, bundle_dir)
    result = {
        "schema_version": VERSION,
        "status": "REVIEW_REQUIRED",
        "problems": [],
        "minimum_host_byte_exposure_s": MIN_SPAN_S,
        "host_byte_exposure_s": None,
        "v18_status": base["status"],
        "physical_origin_authenticated": False,
        "firmware_identity_authenticated": False,
        "physical_time_attested": False,
        "device_span_verified": False,
        "required_next_gate": "Run host_bundle_chain.py v0.7 and serial_bundle.py verify; obtain independent physical provenance review.",
    }
    if base["status"] != "HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD":
        result["problems"].append("V18_CHAIN_NOT_ACCEPTED")
        return result
    cm = _json(Path(capture_dir) / "capture_manifest.json")
    first = _number(cm.get("first_byte_host_offset_seconds"), "first byte offset")
    last = _number(cm.get("last_byte_host_offset_seconds"), "last byte offset")
    span = last - first
    result["host_byte_exposure_s"] = span
    result["host_raw_sha256"] = base["host_raw_sha256"]
    if span < MIN_SPAN_S:
        result["problems"].append("HOST_BYTE_EXPOSURE_UNDER_600_SECONDS")
    if not result["problems"]:
        result["status"] = "HOST_BYTE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED"
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("capture_dir", type=Path)
    p.add_argument("bundle_dir", type=Path)
    args = p.parse_args()
    r = audit(args.capture_dir, args.bundle_dir)
    print(json.dumps(r, sort_keys=True, indent=2, allow_nan=False))
    raise SystemExit(2 if r["status"] == "REVIEW_REQUIRED" else 0)


if __name__ == "__main__":
    main()
