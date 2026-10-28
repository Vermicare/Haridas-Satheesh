# WBI Synthetic Evaluator — Execution Record

**Status:** synthetic execution evidence only; not EEG, clinical, hardware, or real-world validation.  
**Evaluator:** `synthetic_evaluator.py` blob `2becec81a8002cc5ff2f445889b7617baf9937b9`  
**Run date:** 2026-09-28  
**Runtime:** CPython 3.13.5, GCC 14.2.0; evaluator uses Python standard library only.

## Reproducibility check

The exact committed evaluator source was executed twice in the same isolated runtime. Both executions completed their built-in contract tests without assertion failure, produced identical console output, and produced byte-identical `synthetic_risk_coverage.csv`.

SHA-256 of the CSV on both runs:

`65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`

This was a same-runtime deterministic rerun, **not** independent cross-environment reproduction at the time (2026-09-28). The subsequent independent cross-platform verification is documented in the dated addendum below.

## Frozen thresholds selected from calibration only

- confidence-abstention threshold: **0.75**
- authorization-gate confidence threshold: **0.70**
- authorization-gate drift threshold: **0.70**

## Held-out synthetic test result

| Policy | Coverage | Incorrect-action risk | Correct-action retention | Brier | ECE |
|---|---:|---:|---:|---:|---:|
| Ungated | 1.0000 | 0.3292 | 1.0000 | 0.1865 | 0.1099 |
| Confidence abstention | 0.5125 | 0.1301 | 0.6646 | 0.1865 | 0.1099 |
| Authorization gate | 0.5833 | 0.1571 | 0.7329 | 0.1865 | 0.1099 |

Nominal/drift segmentation exposed an important failure mode. The authorization gate's incorrect-action risk was **0.1071 nominal** but **0.3571 under synthetic drift**. Confidence abstention was **0.0741 nominal** and **0.2381 under synthetic drift**.

## Decision

**Do not advance maturity.** On this synthetic fixture, the authorization gate does not establish superiority over simple confidence abstention. It retains more correct actions and covers more rows, but also has higher incorrect-action risk; those operating points are not coverage-matched, so this is not yet a fair superiority test.

Before real EEG work, extend the evaluator to compare policies on a common risk–coverage frontier (or matched coverage targets) and add an explicit drift-gate diagnostic. If the gate still fails to improve incorrect-action risk at comparable coverage across multiple deterministic fixtures, reframe the contribution rather than protecting the architecture.

The generated risk–coverage CSV is preserved beside this record. Unknown real-EEG metrics remain **TBD**.

## 2026-10-26 addendum — independent synthetic cross-platform reproduction

The original September result above is preserved unchanged. [Draft PR #16](https://github.com/Vermicare/Haridas-Satheesh/pull/16) introduced a separate verifier and workflow; it remains **open, draft and unmerged**. [GitHub Actions run #40301577095](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40301577095) completed successfully on both **Ubuntu** (job `121500489305`) and **Windows** (job `121500489045`), CPython **3.13.16** on each. Both job logs were inspected on 2026-10-28 and report:

- Frozen main-branch evaluator Git blob: `2becec81a8002cc5ff2f445889b7617baf9937b9` (unchanged).
- Two isolated reruns per operating system; CSV SHA-256: `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` (matches the original record).
- Stdout SHA-256: `39014b30200d6ddd20b7791ba3e70c48f17770a65a833d365af30b04b7a55c91` on both systems.

**Boundary:** This is independent reproducibility of a deterministic *synthetic* evaluator only. It does not establish public-EEG decoding, a coverage-matched advantage over simple abstention, human safety, or clinical validity. Original results and CSV were not replaced. Maturity remains Research / Simulation; real-EEG outcome metrics remain **TBD**.
