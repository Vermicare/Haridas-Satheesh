#!/usr/bin/env python3
"""Compare two retained *unflashed* GitHub Actions firmware ZIPs.

Byte-level reproducibility audit only: no flash, sensor or origin attestation.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

FILES = {"iot_dual_sensor_capture.bin", "bootloader/bootloader.bin",
         "partition_table/partition-table.bin", "flasher_args.json",
         "SHA256SUMS.txt", "BUILD_PROVENANCE.txt"}
HASHED = FILES - {"SHA256SUMS.txt", "BUILD_PROVENANCE.txt"}
HEX = re.compile(r"^[0-9a-f]{64}  (.+)$")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    if Path(path).stat().st_size > 5_000_000:
        raise ValueError("archive exceeds 5 MB safety limit")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(FILES) or set(names) != FILES:
            raise ValueError("unexpected, missing or duplicate ZIP member")
        if any(z.getinfo(n).file_size > 1_000_000 for n in names):
            raise ValueError("ZIP member exceeds 1 MB safety limit")
        data = {n: z.read(n) for n in names}
    lines = data["SHA256SUMS.txt"].decode("ascii").splitlines()
    hashes = {}
    for line in lines:
        match = HEX.fullmatch(line)
        if not match or match.group(1) in hashes:
            raise ValueError("malformed or duplicate SHA256SUMS entry")
        hashes[match.group(1)] = line[:64]
    if set(hashes) != HASHED or any(sha(data[n]) != hashes[n] for n in HASHED):
        raise ValueError("retained SHA256SUMS does not verify")
    prov = {}
    for line in data["BUILD_PROVENANCE.txt"].decode("utf-8").splitlines():
        if "=" not in line:
            raise ValueError("malformed provenance line")
        k, v = line.split("=", 1)
        if not k or k in prov:
            raise ValueError("duplicate provenance key")
        prov[k] = v
    for k in ("repository", "checked_out_sha", "pr_head_sha", "run_id", "run_attempt"):
        if not prov.get(k):
            raise ValueError("missing provenance key: " + k)
    return data, prov


def ranges(a, b):
    out, start = [], None
    for i in range(max(len(a), len(b))):
        different = i >= len(a) or i >= len(b) or a[i] != b[i]
        if different and start is None:
            start = i
        elif not different and start is not None:
            out.append([start, i])
            start = None
    if start is not None:
        out.append([start, max(len(a), len(b))])
    return out


def compare(first, second):
    a, pa = load(first)
    b, pb = load(second)
    for key in ("repository", "checked_out_sha", "pr_head_sha", "run_id"):
        if pa[key] != pb[key]:
            raise ValueError("not the same recorded source/run: " + key)
    if pa["run_attempt"] == pb["run_attempt"]:
        raise ValueError("two distinct run attempts required")
    report = {"comparison": "same-run-different-attempts",
              "checked_out_sha": pa["checked_out_sha"],
              "pr_head_sha": pa["pr_head_sha"], "run_id": pa["run_id"],
              "attempts": [pa["run_attempt"], pb["run_attempt"]],
              "files": {}}
    for name in sorted(FILES):
        x, y = a[name], b[name]
        diff = ranges(x, y)
        report["files"][name] = {"bytes": [len(x), len(y)],
                                 "sha256": [sha(x), sha(y)],
                                 "identical": not diff,
                                 "different_byte_count": sum(
                                     1 for i in range(max(len(x), len(y)))
                                     if i >= len(x) or i >= len(y) or x[i] != y[i]),
                                 "difference_ranges_half_open": diff}
    report["boundary"] = "UNFLASHED_CI_BUILDS_ONLY; physical provenance TBD"
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("attempt1_zip")
    p.add_argument("attempt2_zip")
    args = p.parse_args()
    print(json.dumps(compare(args.attempt1_zip, args.attempt2_zip),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
