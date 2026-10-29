# WBI A01T v1.1 — pre-execution, frozen descriptive artifact-flag sensitivity

**Protocol frozen before real-data v1.1 scoring.** Actual v1.1 unflagged accuracy: **TBD**. This is **post-hoc descriptive** work following the public v0.9 and v1.0 results; it is **not** a preregistered confirmatory test, new classifier, independent subject/day, drift-gate result, or evidence of safe brain-controlled action. Maturity: **Research / Simulation (unchanged)**.

## Fixed inputs and protections

- Acquire only public BNCI2014_001 **A01T.mat** via the existing allowlisted loader. Observed source: 42,806,453 bytes; SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325` (not a publisher signature). **Never acquire A01E**.
- Import the **unchanged** v0.9 feature extraction, training runs 1–3, calibration run 4, within-day held-out runs 5–6, train-only StandardScaler, logistic regression and calibration-only confidence thresholds. Preserve original all-trial 43/96 correct and threshold operating points 19 acted/6 incorrect, 38/15, 55/24.
- Import the v1.0 source-artifact validator; require six task-run artifact counts exactly **2,4,3,1,2,3** and five flagged trials in held-out runs 5–6. The flags are source annotations, not proof of physiological invalidity or model errors.
- **Do not** use artifact flags to fit, tune, select thresholds, change epoch/channel choices, or remove trials from the original v0.9 primary score. Source flags only define a *secondary* held-out descriptive subset.
- Fail closed on changed source hash, trial alignment, nonbinary flags, invalid probabilities, changed frozen all-trial predictions or changed selective counts.

## Exact reported metrics

Report only aggregate counts/rates: 96 all-trial denominator and original correct count; 5 flagged, 91 unflagged, **observed unflagged correct count / 91**; for each of the **same three frozen confidence thresholds**, all-trial acted/incorrect counts, unflagged acted/incorrect counts, unflagged coverage and unflagged incorrect-action risk. Zero denominator yields JSON null, never zero risk. No per-trial EEG, flags, labels, probabilities, fitted model, class-specific table or personal information in artifacts. Preserve original v0.9 all-trial and v1.0 identification-bound reports unchanged.

## Reproduction and acceptance

From `benchmarks/wireless-brain-interface` run `python -B -m unittest -v test_wbi_a01t_clean_subset_v11` (fictional tests only). For real A01T scoring run `python -B wbi_a01t_clean_subset_v11.py --output <new-private-aggregate-json-path>`. Pin Python 3.13, NumPy 2.3.3, SciPy 1.16.2, scikit-learn 1.7.2; record actual hosted runner image, commit, UTC, output hash, run conditions and any mismatch. The hosted workflow must test on Ubuntu and Windows, and acquire the A01T training file **only** on Ubuntu after fictional tests pass. Independently rerun and inspect job logs and aggregate-only ZIP contents before marking results verified. Never overwrite earlier results.

**Decision gate:** observed clean-subset score may change interpretation of v0.9, but cannot advance maturity. Next decisive experiment remains nine-subject, different-day held-out E-session EEG with leakage controls and a matched-coverage confidence-only versus drift-aware comparison. **Reframe** if the drift gate fails the simpler baseline or source-quality sensitivity undermines the claimed benefit. Clinical, hardware, deployment, novelty, patentability, employer and real-user claims are out of scope.

**Four lenses:** hiring manager — reproducible negative/positive evidence; technical reviewer — label-safe frozen thresholds but post-hoc subset; innovation leader — no drift-specific differentiation; founder — no verified safety or decision value.
