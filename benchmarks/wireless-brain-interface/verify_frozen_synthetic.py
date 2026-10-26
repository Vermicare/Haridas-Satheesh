#!/usr/bin/env python3
"""Fail-closed independent reproducibility check of the frozen WBI synthetic fixture.

Synthetic-only regression: not evidence for EEG, clinical safety, or superiority.
Run: python verify_frozen_synthetic.py
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

EVALUATOR = Path(__file__).with_name("synthetic_evaluator.py")
EXPECTED_SOURCE_GIT_BLOB = "2becec81a8002cc5ff2f445889b7617baf9937b9"
EXPECTED_CSV_SHA256 = "65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a"
EXPECTED_THRESHOLDS = "frozen thresholds: abstention_conf=0.75; gate_conf=0.70; gate_drift=0.70"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_once() -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="wbi-synthetic-") as directory:
        copied = Path(directory) / EVALUATOR.name
        shutil.copyfile(EVALUATOR, copied)
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = "0"
        # Windows defaults to a legacy console code page; the frozen evaluator prints an em dash.
        # Force UTF-8 in the child without modifying the pinned evaluator source.
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            [sys.executable, str(copied)], cwd=directory, env=env,
            capture_output=True, check=True, text=True, encoding="utf-8"
        )
        output = Path(directory, "synthetic_risk_coverage.csv")
        assert output.is_file(), "Evaluator did not emit risk-coverage CSV"
        assert EXPECTED_THRESHOLDS in result.stdout, "Frozen thresholds changed"
        assert "SYNTHETIC ONLY" in result.stdout, "Evidence boundary missing"
        digest = sha256(output.read_bytes())
        assert digest == EXPECTED_CSV_SHA256, f"CSV changed: {digest}"
        return digest, sha256(result.stdout.encode("utf-8"))


def main() -> None:
    source = EVALUATOR.read_bytes()
    git_blob = hashlib.sha1(f"blob {len(source)}\0".encode() + source).hexdigest()
    assert git_blob == EXPECTED_SOURCE_GIT_BLOB, f"Unexpected evaluator source: {git_blob}"
    first = run_once()
    second = run_once()
    assert first == second, "Independent temporary-directory reruns differ"
    print(f"PASS: frozen synthetic evaluator Git blob {git_blob}")
    print(f"PASS: two isolated reruns; CSV SHA-256 {first[0]}")
    print(f"PASS: identical stdout SHA-256 {first[1]}")
    print(f"Python: {sys.version.split()[0]}; platform: {sys.platform}")
    print("Scope: deterministic synthetic evaluator only; EEG results TBD")


if __name__ == "__main__":
    main()
