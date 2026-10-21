# WBI synthetic evaluator — independent verification record

Status: **execution not verified in this record**. This is a reproducibility checklist, not a result or a maturity upgrade.

Source of truth: [frozen evaluator contract](../wireless-brain-interface/SYNTHETIC_EVALUATOR.md). Preserve prior verified evidence and do not interpret synthetic fixtures as public EEG validation.

## Clean-room procedure

1. Check out a specific immutable commit of this repository and record its full SHA.
2. Record Python implementation/version, OS, UTC timestamp, and exact commands.
3. Run the committed evaluator's contract tests and capture complete stdout/stderr and exit codes.
4. Execute the evaluator twice from clean output directories with identical declared inputs/seeds.
5. Record SHA-256 of each generated artifact and compare bytes, threshold selection, risk–coverage rows and metrics.
6. Check calibration/test separation, frozen thresholds, coverage definitions, false-action risk, correct-action retention, Brier score, ECE and drift segmentation against the contract.
7. Preserve negative results and discrepancies; do not adjust thresholds using held-out test rows.
8. Report unknown details as TBD. Only after the synthetic contract is independently verified, plan a separate public EEG benchmark with explicit provenance and subject/session split.

## Run registry (not yet executed)

| Field | Value |
|---|---|
| Repository commit | TBD |
| Python version | TBD |
| OS / environment | TBD |
| Exact test command | TBD |
| Exact evaluator command | TBD |
| Seeds / configuration | TBD |
| Contract tests and exit codes | TBD |
| Run 1 artifact SHA-256 | TBD |
| Run 2 artifact SHA-256 | TBD |
| Byte-identical output | TBD |
| Deviations / failures | TBD |
| Decision | Pending independent execution |

**Advance criterion:** two independently inspected clean executions satisfy the frozen synthetic contract; this alone does not demonstrate real EEG performance. **Reframe criterion:** reproducibility failure, data leakage, or gating advantage that disappears against matched-coverage abstention.
