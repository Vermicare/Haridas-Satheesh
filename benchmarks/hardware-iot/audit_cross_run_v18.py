#!/usr/bin/env python3
"""Offline cross-run byte audit of two *unflashed* ESP-IDF v1.7 CI ZIPs.

A PASS verifies retained member bytes only. It never establishes source equivalence,
container pinning, flashed identity, sensor measurements or permission to flash.
"""
import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

PAIRS = ("app", "boot", "partition", "flasher")
NAMES = {
    "app": ("app-first.bin", "app-second.bin"),
    "boot": ("boot-first.bin", "boot-second.bin"),
    "partition": ("partition-first.bin", "partition-second.bin"),
    "flasher": ("flasher-first.json", "flasher-second.json"),
}
HASHED = {n for pair in NAMES.values() for n in pair}
META = {"SHA256SUMS.txt", "checkout_sha.txt", "comparison_status.txt",
        "compiler_version.txt", "idf_version.txt", "sdkconfig_sha256.txt"}
EXPECTED = HASHED | META
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_ZIP = 5_000_000
MAX_MEMBER = 1_000_000
MAX_TOTAL = 3_000_000


class EvidenceError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    path = Path(path)
    if path.stat().st_size > MAX_ZIP:
        raise EvidenceError("archive exceeds compressed size limit")
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        names = [i.filename for i in entries]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise EvidenceError("unexpected/missing/duplicate ZIP members")
        if sum(i.file_size for i in entries) > MAX_TOTAL:
            raise EvidenceError("aggregate uncompressed size limit exceeded")
        for i in entries:
            mode = i.external_attr >> 16
            if i.is_dir() or stat.S_IFMT(mode) == stat.S_IFLNK or i.file_size > MAX_MEMBER:
                raise EvidenceError("unsafe or oversized ZIP member")
        files = {n: z.read(n) for n in names}
    try:
        checks = files["SHA256SUMS.txt"].decode("ascii").splitlines()
        manifest = {}
        for line in checks:
            m = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
            if not m or m.group(2) in manifest:
                raise EvidenceError("malformed or duplicate manifest entry")
            manifest[m.group(2)] = m.group(1)
        if set(manifest) != HASHED:
            raise EvidenceError("manifest coverage mismatch")
        for name, expected in manifest.items():
            if digest(files[name]) != expected:
                raise EvidenceError("manifest hash mismatch: " + name)
        checkout = files["checkout_sha.txt"].decode("ascii").strip()
        if not GIT_SHA.fullmatch(checkout):
            raise EvidenceError("invalid checkout SHA")
        if files["comparison_status.txt"] != b"MATCH\n":
            raise EvidenceError("original within-run status is not MATCH")
        sdk = files["sdkconfig_sha256.txt"].decode("ascii")
        m = re.fullmatch(r"([0-9a-f]{64})  sdkconfig\n", sdk)
        if not m:
            raise EvidenceError("invalid sdkconfig hash declaration")
        env = {"idf_version": files["idf_version.txt"].decode("ascii").strip(),
               "compiler": files["compiler_version.txt"].decode("ascii").strip(),
               "sdkconfig_sha256": m.group(1)}
        if not env["idf_version"] or not env["compiler"]:
            raise EvidenceError("missing build environment declaration")
    except UnicodeError as exc:
        raise EvidenceError("non-ASCII provenance") from exc
    return files, checkout, env


def audit(first, second):
    a, ca, ea = load(first)
    b, cb, eb = load(second)
    if ca == cb:
        raise EvidenceError("expected distinct documented checkout merge SHAs")
    if ea != eb:
        raise EvidenceError("declared compiler, IDF or effective config differs")
    hashes = {}
    for name in PAIRS:
        x, y = NAMES[name]
        if a[x] != a[y] or b[x] != b[y]:
            raise EvidenceError("within-run binary mismatch: " + name)
        if a[x] != b[x] or a[y] != b[y]:
            raise EvidenceError("cross-run binary mismatch: " + name)
        hashes[name] = {"sha256": digest(a[x]), "bytes": len(a[x]),
                        "within_run_and_cross_run_equal": True}
    return {
        "gate": "PASS_STATIC_UNFLASHED_BINARY_EQUALITY_SOURCE_REVIEW_REQUIRED",
        "zip_sha256": [digest(Path(first).read_bytes()), digest(Path(second).read_bytes())],
        "checkout_merge_sha": [ca, cb],
        "environment_declared": ea,
        "members": hashes,
        "source_equivalence_from_artifacts": "NOT_ESTABLISHED",
        "container_digest_from_artifacts": "NOT_RECORDED",
        "flash_authorized": False,
        "physical_flash_attested": False,
        "sensor_measurements": "NONE",
        "limitations": "Offline bytes only. Source diff, CI image digest and host identity require independent external verification."
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("first_zip")
    p.add_argument("second_zip")
    p.add_argument("--output", type=Path, help="Optional aggregate-only JSON; no binaries")
    args = p.parse_args(argv)
    try:
        result = audit(args.first_zip, args.second_zip)
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    except (EvidenceError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"gate": "REJECTED", "reason": str(exc), "flash_authorized": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
