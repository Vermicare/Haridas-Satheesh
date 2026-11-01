#!/usr/bin/env python3
"""Offline v1.9 ESP32-S3 firmware artifact audit. Python 3 standard library only.

Usage: python verify_v19_artifacts.py ubuntu22.zip ubuntu24.zip comparison.zip
No hardware access, flashing, external dependencies, or private identifiers.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

RUN_ID = 41177363687
CHECKOUT = "7728c67e55bced481d25ddd765c3ffa4eb2134a3"
IMAGE = "espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c"
ARCHIVES = (
    "d4115c3116443581a54378076eb75608fa369a305c2a465ddc87e661f6855227",
    "076e5cc6d1cf7a84a1fc84f62ed8d59f99aaf455189808d429f6e107a6fdd941",
    "6072bc8216970bd6a5038c97feb479b67f441e749375848571d2600d70192e5d",
)
EXPECTED = {
    "app.bin": "050cb7ac2bf0fe94748cda4d744cd0ae2f7a38cb86ccaadf34749ffb3fda3183",
    "bootloader.bin": "aff00d000954beee5e794e825bbfe0a639c6ba3d5bce0f4dee7a448fa030229f",
    "partition.bin": "7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820",
    "flasher_args.json": "05e0e4b03c968992f46699ce25bb3ca7e033f828ba7e84456d6ee4806d5c1fc5",
}
SAME = tuple(EXPECTED) + (
    "checkout_sha.txt", "sdkconfig_sha256.txt", "target_defaults_sha256.txt",
    "image_config_digest.txt", "compiler_version.txt", "idf_version.txt",
    "requested_image.txt", "target_assertions.txt",
)

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read_archive(path, expected):
    raw = Path(path).read_bytes()
    require(digest(raw) == expected, f"archive digest mismatch: {path}")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "duplicate ZIP member")
        require(all(not n.startswith("/") and ".." not in Path(n).parts for n in names), "unsafe ZIP member path")
        require(all(archive.getinfo(n).file_size < 50_000_000 for n in names), "oversized ZIP member")
        return {n: archive.read(n) for n in names}

def verify_build(data):
    manifest = data["SHA256SUMS.txt"].decode().strip().splitlines()
    seen = set()
    for line in manifest:
        expected_hash, name = line.split("  ", 1)
        require(name in EXPECTED and name not in seen, f"unexpected manifest member: {name}")
        require(digest(data[name]) == expected_hash == EXPECTED[name], f"member digest mismatch: {name}")
        seen.add(name)
    require(seen == set(EXPECTED), "incomplete manifest")
    flash = json.loads(data["flasher_args.json"])
    require(flash["extra_esptool_args"]["chip"] == "esp32s3", "wrong chip target")
    require(flash["flash_settings"]["flash_size"] == "8MB", "wrong nominal flash size")
    for name in ("app.bin", "bootloader.bin"):
        blob = data[name]
        require(len(blob) >= 14 and blob[0] == 0xE9, f"invalid image header: {name}")
        require(int.from_bytes(blob[12:14], "little") == 9, f"not ESP32-S3 image chip ID: {name}")
    require(data["checkout_sha.txt"].decode().strip() == CHECKOUT, "wrong merge checkout")
    require(data["requested_image.txt"].decode().strip() == IMAGE, "wrong immutable image")
    require(IMAGE.split("@", 1)[1] in data["image_repo_digests.json"].decode(), "unverified image digest")
    require("ESP32-S3 target and 8MB nominal flash settings verified" in data["target_assertions.txt"].decode(), "missing build assertions")
    require(data["idf_version.txt"].decode().strip() == "ESP-IDF v6.1", "unexpected ESP-IDF")
    require("15.2.0" in data["compiler_version.txt"].decode(), "unexpected compiler")

def audit(paths):
    require(len(paths) == 3, "supply Ubuntu 22.04, Ubuntu 24.04, comparison ZIPs")
    a, b, comparison = (read_archive(path, sha) for path, sha in zip(paths, ARCHIVES))
    verify_build(a)
    verify_build(b)
    for name in SAME:
        require(a[name] == b[name], f"cross-run mismatch: {name}")
    require("MATCH: four unflashed members from independently provisioned runner images" in comparison["comparison.log"].decode(), "comparison log mismatch")
    print(f"PASS run {RUN_ID}: three ZIP digests, eight member checksums, four binary/layout byte matches, source/config/toolchain/target provenance")
    for name, sha in EXPECTED.items():
        print(f"{name} SHA-256 {sha}")
    print("No physical flash, PSRAM, sensor, deployment, or performance validation.")

if __name__ == "__main__":
    try:
        audit(sys.argv[1:])
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, UnicodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
