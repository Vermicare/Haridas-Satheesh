# WBI v1.0 — A01T source artifact-flag audit (pre-execution protocol)

**Status:** frozen design; actual A01T artifact counts **TBD** until an independently inspected hosted run. No maturity change. This is a source-quality sensitivity gate, **not** new decoding, safety evidence, or a different-day evaluation.

## Rationale and frozen input

The [v0.9 same-day A01T pilot](WBI_A01T_TRAINING_ONLY_PILOT_V09_RESULT.md) retained all 96 held-out trials and reproduced **43/96 correct**. The publisher's [BCI Competition IV 2a description](https://www.bbci.de/competition/iv/desc_2a.pdf) identifies artifact-marked trials; [MOABB BNCI2014_001 documentation](https://moabb.neurotechx.com/docs/generated/moabb.datasets.BNCI2014_001.html) exposes explicit `artifact_handling` modes. Flag-aware and all-trial estimates must not be conflated.

Use the **same** previously pinned A01T source (42,806,453 bytes; observed SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325`), existing allowlisted loader and existing six-task-run split: train 1–3, calibrate 4, held-out within-day 5–6. **Do not access A01E or evaluation labels.** No raw EEG, per-trial flags, labels, or predictions may be persisted.

## Predeclared checks and output

1. Require nine MAT blocks and exactly 48 monotonically increasing one-based trial positions plus 48 binary `artifacts` flags in **each** task run; fail closed on missing/malformed flags.
2. Publish only six run-level counts and three split-level counts (flagged, unflagged, total). No class-level or trial-level outputs.
3. Keep the v0.9 **43/96 all-trial** result unchanged. Given only the aggregate number of correct predictions `c=43`, total `n=96`, and held-out flagged count `f`, report the sharp logical **identification** interval for unflagged accuracy:
   - `clean = n - f`
   - `min_correct_clean = max(0, c - f)`
   - `max_correct_clean = min(c, clean)`
   - bounds are `[min_correct_clean / clean, max_correct_clean / clean]`; if `clean=0`, both rates are null.
4. These bounds are **not** measured artifact-free accuracy, a confidence interval, a causal estimate, or an uncertainty estimate for independent subjects. They cannot support model selection or any clinical/safety claim. A future separate frozen trial-level sensitivity analysis is required to know the actual clean-subset score.
5. Fail on overwrite, malformed flags, source fingerprint mismatch, or missing evidence. Log environment versions, code commit, UTC run time, and all unknowns as `TBD`.

## Reproduction and decision

`python -B -m unittest -v test_bnci_a01t_artifact_audit_v10` from this directory, then `python -B bnci_a01t_artifact_audit_v10.py --output <new-local-json-path>`. Hosted workflow executes fictional contracts on Ubuntu and Windows and real **A01T training only** on Ubuntu; aggregate JSON only.

**Advance:** only after separate multi-subject different-day evaluation and a coverage-matched drift-gate advantage over confidence-only abstention. **Reframe:** if clean-trial sensitivity, coverage shifts, or cross-session tests erase any proposed benefit. WBI stays **Research / Simulation**; real different-day and drift-gate outcomes remain **TBD**. No novelty, patentability, clinical, deployment, or employer-data claim.
