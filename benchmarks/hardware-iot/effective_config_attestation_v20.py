#!/usr/bin/env python3
"""Bounded, privacy-minimized ESP32-S3 effective Kconfig evidence extraction.

No hardware access, flashing, or PSRAM physical-detection claims.
Usage: python effective_config_attestation_v20.py extract sdkconfig output.json
       python effective_config_attestation_v20.py self-test
"""
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_INPUT = 4_000_000
ALLOWED = re.compile(r"^CONFIG_(?:IDF_TARGET(?:_ESP32S3)?|ESPTOOLPY_FLASHSIZE(?:_[A-Z0-9]+)?|APP_REPRODUCIBLE_BUILD|APP_PROJECT_VER(?:_FROM_CONFIG)?|SPIRAM[A-Z0-9_]*)$")
ENTRY = re.compile(r'^(CONFIG_[A-Z0-9_]+)=(.*)$')
UNSET = re.compile(r'^# (CONFIG_[A-Z0-9_]+) is not set$')
REQUIRED = {
    "CONFIG_IDF_TARGET": '"esp32s3"',
    "CONFIG_IDF_TARGET_ESP32S3": "y",
    "CONFIG_ESPTOOLPY_FLASHSIZE": '"8MB"',
    "CONFIG_APP_REPRODUCIBLE_BUILD": "y",
    "CONFIG_APP_PROJECT_VER_FROM_CONFIG": "y",
    "CONFIG_APP_PROJECT_VER": '"iot-repro-v19-s3"',
}


def extract(raw):
    if not raw or len(raw) > MAX_INPUT:
        raise ValueError("sdkconfig empty or over 4MB")
    text = raw.decode("utf-8", errors="strict")
    selected = {}
    for line in text.splitlines():
        match = ENTRY.fullmatch(line) or UNSET.fullmatch(line)
        if not match:
            continue
        name = match.group(1)
        if not ALLOWED.fullmatch(name):
            continue
        if name in selected:
            raise ValueError(f"duplicate allowed key: {name}")
        selected[name] = match.group(2) if line.startswith("CONFIG_") else "NOT_SET"
    for name, value in REQUIRED.items():
        if selected.get(name) != value:
            raise ValueError(f"required effective setting mismatch: {name}")
    if selected.get("CONFIG_ESPTOOLPY_FLASHSIZE_8MB") not in ("y", None):
        raise ValueError("8MB selection conflicts with required flash size")
    spiram = {key: val for key, val in sorted(selected.items()) if key.startswith("CONFIG_SPIRAM")}
    state = ("configured_enabled" if spiram.get("CONFIG_SPIRAM") == "y"
             else "configured_disabled" if spiram.get("CONFIG_SPIRAM") == "NOT_SET"
             else "not_explicitly_observed")
    return {
        "schema": "iot-effective-config-subset-v20",
        "full_sdkconfig_sha256": hashlib.sha256(raw).hexdigest(),
        "selected_settings": dict(sorted(selected.items())),
        "psram_configuration_observation": state,
        "physical_flash_identity": "TBD",
        "physical_psram_identity": "TBD",
        "physical_sensor_capture": "TBD",
        "scope": "Unflashed software Kconfig snapshot only; no device attestation",
    }


def encode(record):
    return (json.dumps(record, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def self_test():
    base = "\n".join(f"{k}={v}" for k, v in REQUIRED.items()) + "\n"
    good = (base + "# CONFIG_SPIRAM is not set\nCONFIG_WIFI_PASSWORD=\"DO_NOT_LEAK\"\n").encode()
    record = extract(good)
    assert record["psram_configuration_observation"] == "configured_disabled"
    assert "DO_NOT_LEAK" not in encode(record).decode()
    assert encode(record) == encode(extract(good))
    assert extract(base.encode())["psram_configuration_observation"] == "not_explicitly_observed"
    assert extract((base + "CONFIG_SPIRAM=y\nCONFIG_SPIRAM_MODE_OCT=y\n").encode())["psram_configuration_observation"] == "configured_enabled"
    negatives = [
        base.replace('"esp32s3"', '"esp32"').encode(),
        base.replace('"8MB"', '"2MB"').encode(),
        (base + 'CONFIG_IDF_TARGET="esp32s3"\n').encode(),
        (base + 'CONFIG_SPIRAM=y\n# CONFIG_SPIRAM is not set\n').encode(),
        b"", b"X" * (MAX_INPUT + 1),
        (base + "\udcff").encode("utf-8", errors="surrogatepass"),
    ]
    for idx, case in enumerate(negatives, 1):
        try:
            extract(case)
        except (ValueError, UnicodeDecodeError):
            pass
        else:
            raise AssertionError(f"negative control {idx} was accepted")
    print(f"PASS: 4 positive/structural checks, {len(negatives)} rejection controls; synthetic sdkconfig only")


def main(argv):
    if argv == ["self-test"]:
        self_test()
        return
    if len(argv) != 3 or argv[0] != "extract":
        raise ValueError("usage: extract sdkconfig output.json | self-test")
    source = Path(argv[1])
    if source.stat().st_size > MAX_INPUT:
        raise ValueError("sdkconfig over 4MB")
    record = extract(source.read_bytes())
    output = Path(argv[2])
    output.write_bytes(encode(record))
    print(f"PASS: privacy-minimized config evidence {output}; physical identity TBD")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, UnicodeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
