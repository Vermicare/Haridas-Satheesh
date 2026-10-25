# Wireless Brain Interface — Frozen Synthetic Evaluator

**Status:** synthetic protocol specified and evaluator committed; a same-runtime deterministic execution record is published in [EXECUTION_RECORD.md](EXECUTION_RECORD.md). [Independent cross-platform reproduction](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md) passed on Linux and Windows in draft-branch [CI #40059209875](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40059209875); real EEG validation remains TBD.  
**Maturity remains:** Research / Simulation.  
**Purpose:** satisfy the pre-EEG evidence gate in Issue #3 without using real EEG labels.

The committed evaluator is deliberately dependency-free (Python standard library only). It creates deterministic fictional calibration/test probabilities, select operating thresholds on **calibration only**, freeze them, and evaluate three policies on held-out synthetic test rows:

1. ungated decoder;
2. simple confidence abstention;
3. authorization gate using confidence plus a declared drift score.

The fixture is not evidence that WBI works on EEG. Its job is to make the evaluation logic inspectable before real-data outcomes are visible.

## Run

Implementation: [`synthetic_evaluator.py`](./synthetic_evaluator.py). **A same-runtime deterministic execution is documented in [EXECUTION_RECORD.md](EXECUTION_RECORD.md); independent Linux/Windows reproduction is recorded separately in [FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md); no real EEG was decoded.** The evaluator is designed to emit machine-readable summary results and a risk–coverage table and to run hand-checkable contract tests before evaluation.

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

Next gate: connect the frozen evaluation definitions to **subject-disjoint public motor-imagery EEG** (the preregistered PhysioNet EEGMMIDB is **single-session**, not longitudinal), report per-subject results, and compare authorization gating with both ungated decoding and simple abstention at matched imagery coverage and common decision opportunities. Any longitudinal drift claim requires a **separate multi-session dataset**. The additive [v0.3 fictional matched-opportunity preflight](MATCHED_OPPORTUNITY_CONTRACT_V03.md) tests comparison integrity but is not EEG validation.

Reframe the claimed contribution if lower incorrect-action risk is mainly purchased by near-total abstention, or if the authorization gate does not improve on simple abstention at comparable coverage.

Unknown real-EEG metrics remain **TBD**.
