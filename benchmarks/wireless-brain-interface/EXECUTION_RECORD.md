# WBI Synthetic Evaluator — Execution Record

**Status:** synthetic execution evidence only; not EEG, clinical, hardware, or real-world validation.  
**Evaluator:** `synthetic_evaluator.py` blob `2becec81a8002cc5ff2f445889b7617baf9937b9`  
**Run date:** 2026-09-28  
**Runtime:** CPython 3.13.5, GCC 14.2.0; evaluator uses Python standard library only.

## Reproducibility check

The exact committed evaluator source was executed twice in the same isolated runtime. Both executions completed their built-in contract tests without assertion failure, produced identical console output, and produced byte-identical `synthetic_risk_coverage.csv`.

SHA-256 of the CSV on both runs:

`65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`

This is a same-runtime deterministic rerun, **not** independent cross-environment reproduction. Clean CI / second-environment reproduction remains outstanding.

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
