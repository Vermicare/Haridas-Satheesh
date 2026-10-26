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
