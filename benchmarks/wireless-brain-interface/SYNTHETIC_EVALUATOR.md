# Wireless Brain Interface — Frozen Synthetic Evaluator

**Status:** synthetic protocol specified; executable evaluator pending.  
**Maturity remains:** Research / Simulation.  
**Purpose:** satisfy the pre-EEG evidence gate in Issue #3 without using real EEG labels.

The planned evaluator is deliberately dependency-free (Python standard library only). It will create deterministic fictional calibration/test probabilities, select operating thresholds on **calibration only**, freeze them, and evaluate three policies on held-out synthetic test rows:

1. ungated decoder;
2. simple confidence abstention;
3. authorization gate using confidence plus a declared drift score.

The fixture is not evidence that WBI works on EEG. Its job is to make the evaluation logic inspectable before real-data outcomes are visible.

## Run

**TBD — implementation not yet committed.** The documented protocol is not executable evidence yet. When implemented, the evaluator must emit machine-readable summary results and a risk–coverage table and must run hand-checkable contract tests before evaluation.

## Frozen contract

Calibration rows and test rows are generated from separate deterministic seeds. Threshold selection receives calibration rows only. The selected thresholds are immutable during test evaluation.

The simple-abstention threshold is chosen to minimize incorrect-action risk subject to retaining at least 50% calibration coverage. The authorization gate searches confidence and drift thresholds under the same minimum-coverage constraint. This is a **protocol choice**, not a claim that 50% is operationally acceptable.

Metrics:

- **coverage** = acted rows / all rows;
- **incorrect-action risk** = incorrect acted rows / acted rows;
- **correct-action retention** = correct acted rows / correct decoder predictions;
- **Brier score** = mean squared probability error;
- **ECE** = 10-bin expected calibration error over predicted confidence.

A risk–coverage table is emitted for confidence thresholds from 0.50 to 0.95. Drift-segment rows are explicitly marked in the fixture.

## Advancement / kill rule

Passing these contract tests only permits the next experiment. It does **not** advance maturity.

Next gate: connect this evaluator logic unchanged to a longitudinal public motor-imagery EEG benchmark, report per-subject/per-session results, and compare the authorization gate with both ungated decoding and simple abstention at comparable coverage.

Reframe the claimed contribution if lower incorrect-action risk is mainly purchased by near-total abstention, or if the authorization gate does not improve on simple abstention at comparable coverage.

Unknown real-EEG metrics remain **TBD**.
