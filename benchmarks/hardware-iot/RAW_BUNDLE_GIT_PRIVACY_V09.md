# IoT raw-bundle Git-worktree privacy gate — v0.9 (2026-10-26)

**Scope:** public, fictional-data software security regression. **No physical BH1750/SCD40 capture, sensor accuracy, firmware attestation or field reliability is established.**

## Question and reproducible failure

The existing `serial_acquire.py` refused to save private raw serial bytes under a Git worktree. However, downstream `serial_bundle.py build` accepted a destination inside the same worktree and wrote `raw_serial.log`, `samples.csv` and manifests there. Raw serial may contain credentials, serial numbers or identifying debug output; a later careless `git add` could publish them.

Two new fictional negative controls cover (1) a normal checkout with a `.git` **directory**, and (2) a linked worktree with a `.git` **file**. Both assert rejection **before any output directory is created**.

**Before correction:** [GitHub Actions #40309376746](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40309376746), commit `a3ac79d687fda5e2985b15791b0dcc1ed9740b24`, Ubuntu/Python 3.13: **82 tests, 2 expected failures** (`BundleError not raised`). Windows job was cancelled; no Windows before-fix result is claimed. Ubuntu job log inspected.

**Correction:** `serial_bundle.build` reuses the existing `serial_acquire.outside_git_tree` check, which resolves the destination path and checks ancestors for `.git` files or directories. It converts the existing capture exception to `BundleError` for the bundle CLI, and checks **before** creating output. This is a guardrail against accidental in-repository raw-data publication, not a data-loss-prevention system.

**After correction:** [GitHub Actions #40309494687](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40309494687), executable commit `683e961ca5d74bbf0b0165e8d9b9f3e061babf63`: **82/82 tests passed on Ubuntu/Python 3.13 and 82/82 on Windows/Python 3.13**. Both job logs inspected, including both new tests. Source blob `b67920fe98df6915fb3a205ccf05842d4467d956`; test blob `845e363a37b2465b8412fa08782118ae692a11c2`.

## Boundaries and decision

This check cannot stop an operator from subsequently copying, emailing, syncing or explicitly committing private files; it does not inspect logs for secrets. Existing Git history may already contain secrets and is not scanned here. Private capture directories should be access-restricted and reviewed before sharing. This experiment uses only fabricated sensor rows and a fictional firmware file.

**Decision:** retain **Prototype / Hardware Architecture**. Strongest new evidence: reproducible Linux/Windows rejection of two previously accepted unsafe destinations. **Largest gap:** zero independently reviewed real >=600-second dual-sensor session; physical provenance and accuracy **TBD**. **Next decisive experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8), genuine private >=630-second host capture with >=600-second host-byte and device-monotonic coverage, raw/firmware hashes, wiring and controlled light perturbation, followed by independent review. **Reframe** as capture-integrity tooling if genuine physical provenance cannot be demonstrated. No merge, release or stage advancement.
