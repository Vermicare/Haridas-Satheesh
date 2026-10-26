# WBI frozen synthetic evaluator — separate-container reproduction (2026-10-26)

**Scope:** software reproducibility only. **No EEG data, human participants, clinical validation, safety validation, or superiority claim.** Maturity remains **Research / Simulation**.

## What was independently executed

The frozen `synthetic_evaluator.py` was retrieved from the live public GitHub repository through the connected GitHub API, reconstructed byte-for-byte in a **separate execution container**, and authenticated against its original Git blob SHA `2becec81a8002cc5ff2f445889b7617baf9937b9` before running. The original record is [EXECUTION_RECORD.md](EXECUTION_RECORD.md), dated 2026-09-28.

- **Run date:** 2026-10-26 (Asia/Kolkata).
- **Runtime:** Python 3.13.5, GCC 14.2.0; Linux 6.18.55 x86_64, glibc 2.41.
- **Dependencies:** Python standard library only; no external EEG data.
- **Reproduction:** two clean temporary-directory subprocess runs with `PYTHONHASHSEED=0`, followed by an intentionally mutated-source negative control.
- **Commands:** `python benchmarks/wireless-brain-interface/verify_frozen_synthetic.py` from the repository root is also supported; the checker locates the evaluator beside itself.

## Verified outcome

| Check | Result |
|---|---|
| Original source Git blob identity | **MATCH** |
| Frozen calibration thresholds | abstention 0.75; gate confidence 0.70; gate drift 0.70 |
| Generated CSV SHA-256 | `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` — **MATCH** to preserved September record |
| Two clean-directory reruns | **MATCH** |
| Console-output SHA-256 (both) | `39014b30200d6ddd20b7791ba3e70c48f17770a65a833d365af30b04b7a55c91` — **MATCH** |
| Source-mutation negative control | **PASS**: verifier rejects a changed test seed before executing |
| EEG metrics, external investigator verification, Windows CI | **TBD** |

The held-out **synthetic** incorrect-action risk was 0.1301 for confidence abstention (coverage 0.5125) versus 0.1571 for the drift-aware gate (coverage 0.5833). These are **different coverage operating points** and do not prove superiority.

## Limitations and next gate

This is a **separate execution environment**, not independent external investigator validation, not a different Python version, and not a cross-operating-system reproduction. Both the September record and this execution used Python 3.13.5 / GCC 14.2.0. The verifier intentionally pins the historical source and CSV hash; legitimate evaluator changes require a **new versioned** reference record, not silent baseline replacement.

**Next:** run this exact frozen verifier in clean Windows and Linux CI with retained logs, then independently benchmark subject-disjoint public EEG using predeclared matched-coverage comparisons. If drift gating fails to outperform confidence-only abstention under comparable action opportunities, **reframe the hypothesis** rather than advancing maturity.

**Security and privacy:** fictional data only; no credentials, employer data, private contacts or external actions.

## Hosted cross-OS verification and preserved negative controls — 2026-10-26

**New evidence; does not revise the original September result.** The first hosted [Ubuntu/Windows run #40301404861](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40301404861) reproduced a **Windows failure**: checkout converted the frozen Python file's LF line endings, so its raw Git-blob identity changed to `889b4b4614aa7c2b65932641330c95225c38f71e`. The validator correctly rejected it. No evaluator source was changed. After configuring `core.autocrlf=false` **before checkout**, [run #40301487346](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40301487346) exposed a second Windows-only failure: the evaluator's em dash was encoded by the legacy console code page, while the parent subprocess decoded as UTF-8. The resulting `UnicodeDecodeError` was a verifier transport/encoding defect, not a change in synthetic model output.

The verifier now explicitly sets `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1` in its **child process only**, preserving the frozen evaluator's bytes and thresholds. The existing draft PR #16 branch gained a Linux/Windows GitHub Actions workflow; this is CI, **not** a new scheduled portfolio automation.

**Verified final-head run:** [GitHub Actions #40301577095](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40301577095), commit `4c7dab1d4a34bdb2eb7cc47f722d099a0f12612b`, CPython **3.13.16** on **Ubuntu and Windows**. Both jobs completed successfully and both logs were inspected. Each OS reports:
- Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9` — **MATCH** to the frozen evaluator;
- two clean temporary-directory reruns; CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` — **MATCH** to the September record;
- stdout SHA-256 `39014b30200d6ddd20b7791ba3e70c48f17770a65a833d365af30b04b7a55c91` — **MATCH** across both OS runners.

**Interpretation:** the frozen fictional experiment is reproducible across two operating systems with Python 3.13.16; this is stronger software reproducibility evidence than the original Linux-only run. It does **not** demonstrate cross-version equivalence across Python major/minor releases, independently collected EEG, biological validity, drift-gate superiority, real-world safety, or external peer review. **Maturity remains Research / Simulation.** The decisive next experiment is subject-disjoint public EEG with leakage controls and confidence-abstention comparison at matched action coverage. Do not claim the drift gate wins on the current unequal-coverage synthetic comparison.
