#!/usr/bin/env python3
"""Independent, dependency-free reproduction check of the *frozen* WBI synthetic evaluator.

Synthetic protocol only. This does not evaluate EEG, devices, safety or clinical outcomes.
The source Git blob and CSV digest are pinned to the already-committed 2026-09-28
execution record; no thresholds, labels, or evaluator code are modified.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_BLOB = "2becec81a8002cc5ff2f445889b7617baf9937b9"
CSV_SHA256 = "65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a"
FROZEN_THRESHOLDS = "frozen thresholds: abstention_conf=0.75; gate_conf=0.70; gate_drift=0.70"
FROZEN_POLICIES = {
    "ungated": "coverage=1.0000 incorrect_action_risk=0.3292 correct_action_retention=1.0000",
    "confidence_abstention": "coverage=0.5125 incorrect_action_risk=0.1301 correct_action_retention=0.6646",
    "authorization_gate": "coverage=0.5833 incorrect_action_risk=0.1571 correct_action_retention=0.7329",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def verify(source: Path) -> dict:
    raw = source.read_bytes().replace(b"\r\n", b"\n")
    actual_blob = git_blob_sha(raw)
    if actual_blob != SOURCE_BLOB:
        raise ValueError(f"frozen source mismatch: {actual_blob} != {SOURCE_BLOB}")
    runs = []
    for _ in range(2):
        with tempfile.TemporaryDirectory(prefix="wbi-frozen-") as tmp:
            work = Path(tmp)
            (work / "synthetic_evaluator.py").write_bytes(raw)
            completed = subprocess.run(
                [sys.executable, "-B", str(work / "synthetic_evaluator.py")],
                cwd=work, check=True, capture_output=True, text=True, encoding="utf-8",
                timeout=45,
            )
            stdout = completed.stdout.replace("\r\n", "\n")
            csv_digest = hashlib.sha256((work / "synthetic_risk_coverage.csv").read_bytes()).hexdigest()
            if csv_digest != CSV_SHA256:
                raise ValueError(f"frozen CSV mismatch: {csv_digest} != {CSV_SHA256}")
            if "SYNTHETIC ONLY — not EEG/clinical validation" not in stdout:
                raise ValueError("synthetic evidence disclaimer missing")
            if FROZEN_THRESHOLDS not in stdout:
                raise ValueError("frozen thresholds changed")
            for policy, expected in FROZEN_POLICIES.items():
                if f"{policy} {expected}" not in stdout:
                    raise ValueError(f"frozen held-out result changed: {policy}")
            runs.append({"stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(), "csv_sha256": csv_digest})
    if runs[0] != runs[1]:
        raise ValueError("independent isolated-directory reruns differ")
    return {
        "evidence_scope": "frozen synthetic contract only; no EEG/clinical/device validation",
        "source_git_blob": actual_blob,
        "csv_sha256": runs[0]["csv_sha256"],
        "normalized_stdout_sha256": runs[0]["stdout_sha256"],
        "runs": 2,
        "python": platform.python_version(),
        "platform": platform.system(),
        "status": "PASS",
    }


if __name__ == "__main__":
    try:
        print(json.dumps(verify(Path(__file__).with_name("synthetic_evaluator.py")), sort_keys=True))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FROZEN_SYNTHETIC_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
