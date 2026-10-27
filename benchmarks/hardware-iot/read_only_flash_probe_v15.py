"""Offline, read-only esptool flash-id transcript gate.

Never connects to hardware or authorizes flashing. A transcript is an operator
assertion, not authenticated device evidence. Avoids emitting MAC/serial data.
"""
import argparse
import json
import re
import sys
from pathlib import Path


class ProbeError(ValueError):
    pass


_CHIP = re.compile(r"(?im)^\s*(?:Chip is|Chip type:)\s*ESP32-S3\b[^\n]*$")
_CHIP_ANY = re.compile(r"(?im)^\s*(?:Chip is|Chip type:)\s*(ESP[0-9A-Za-z-]+)[^\n]*$")
_SIZE = re.compile(r"(?im)^\s*Detected flash size:\s*(\d+)\s*(MB|MiB)\s*$")
_ERROR = re.compile(r"(?im)(?:^\s*(?:WARNING\b|ERROR\b|A fatal error occurred:)|\b(?:failed to connect|failed to detect|could not detect)\b)")
_ALLOWED_SIZES = {1, 2, 4, 8, 16, 32, 64, 128}


def inspect_transcript(raw: str, declared_build_flash_mb: int = 2) -> dict:
    """Return privacy-safe gate; fail closed on ambiguous/unrecognized output."""
    if not isinstance(raw, str) or len(raw) > 100_000:
        raise ProbeError("transcript missing or oversized")
    if declared_build_flash_mb not in _ALLOWED_SIZES or isinstance(declared_build_flash_mb, bool):
        raise ProbeError("unsupported declared build flash size")
    if _ERROR.search(raw):
        raise ProbeError("probe reports warning/error; manual review required")
    chips = _CHIP_ANY.findall(raw)
    if len(chips) != 1 or not _CHIP.search(raw):
        raise ProbeError("exactly one recognized ESP32-S3 identification required")
    matches = _SIZE.findall(raw)
    if len(matches) != 1:
        raise ProbeError("exactly one detected flash-size line required")
    observed = int(matches[0][0])
    if observed not in _ALLOWED_SIZES:
        raise ProbeError("unsupported detected flash size")
    return {
        "gate": "TRANSCRIPT_PARSED_FLASH_NOT_AUTHORIZED",
        "evidence_type": "OPERATOR_SUPPLIED_TRANSCRIPT_UNVERIFIED",
        "chip_family_claimed": "ESP32-S3",
        "observed_flash_mb_claimed": observed,
        "build_flash_mb_declared": declared_build_flash_mb,
        "flash_size_comparison": "MATCH" if observed == declared_build_flash_mb else "DIFFERENT_REQUIRES_BOARD_CONFIGURATION_REVIEW",
        "physical_device_attested": False,
        "flashed_image_attested": False,
        "hardware_capture_performed": False,
        "device_identity": "TBD",
        "firmware_provenance": "TBD",
        "next_step": "Independent board/port, bootloader, partitions, PSRAM, flash configuration and binary-hash review before any write.",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript", type=Path, help="Private esptool flash-id text output; never commit")
    ap.add_argument("--build-flash-mb", type=int, default=2)
    ns = ap.parse_args(argv)
    try:
        raw = ns.transcript.read_text(encoding="utf-8")
        report = inspect_transcript(raw, ns.build_flash_mb)
    except (OSError, UnicodeError, ProbeError) as exc:
        print(json.dumps({"gate": "HOLD_PROBE_REJECTED", "reason": str(exc), "flash_authorized": False}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
