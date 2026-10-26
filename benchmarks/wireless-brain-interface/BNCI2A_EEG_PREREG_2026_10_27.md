# WBI prospective public-EEG gate — BNCI2014_001 (2026-10-27)

**Status: protocol + fictional metadata preflight only. Real EEG ingestion, classifier, thresholds, outcomes, clinical/device safety and external review: TBD.** This document does not modify the frozen synthetic evaluator or upgrade Research / Simulation.

## Decision-changing dataset check

PhysioNet EEG Motor Movement/Imagery v1.0.0 (DOI 10.13026/C28G6P) has 14 runs per subject, but the MOABB PhysionetMI representation has **one session**. It is suitable for subject-disjoint classification but **not a genuine different-day session-shift test**. Its T1/T2 codes also change meaning by task/run. Do not treat runs as independent recording days or mix those labels blindly.

**Selected initial session-shift dataset:** BCI Competition IV dataset 2a, exposed as `BNCI2014_001` in MOABB. Publisher/benchmark documentation describes **9 subjects, two sessions on different days, six runs per session, 48 trials per run, four motor-imagery classes, 22 EEG channels at 250 Hz**. This is small (9 independent subjects) and cannot establish safety.

Sources (checked 2026-10-27):
- Primary competition: https://www.bbci.de/competition/iv/
- Dataset details / session structure: https://moabb.neurotechx.com/docs/generated/moabb.datasets.BNCI2014_001.html
- PhysioNet source: https://physionet.org/content/eegmmidb/1.0.0/
- PhysionetMI session metadata: https://moabb.neurotechx.com/docs/generated/moabb.datasets.PhysionetMI.html

## Frozen pre-outcome split proposal

The companion `bnci2a_split_preflight.py` consumes **metadata only** (no labels, EEG or outcomes), checks exactly 9 × 2 × 6 × 48 public-dataset trial identifiers, and emits SHA-256 identifiers for 18 folds. All trial IDs must be unique; malformed/incomplete manifests fail closed. This is a **schema expectation from dataset documentation**, not a claim that actual files were loaded.

**Primary within-subject temporal transfer (9 folds):** for each subject, session T runs 1–4 train, T runs 5–6 calibration, and all session E runs held out for test. Fit preprocessing, feature selection, classifier, probability calibration, and action-policy thresholds **only on T** in their assigned partitions. Never refit using E.

**Secondary subject-disjoint transfer (9 folds):** for each held-out subject, train using *other subjects* T runs 1–4; calibrate using *other subjects* T runs 5–6; test on the held-out subject's E runs. Do not access any held-out subject data for model selection. These two protocols answer different questions and must not be pooled as independent replications.

**After metadata validation:** predeclare left-vs-right imagery task subset (or a four-class decoder with an explicitly documented action map), epoch window, artifact handling, preprocessing, decoder, seed, calibration method and model selection before revealing E labels. Record upstream file hashes, dataset terms, exact loader and dependency versions, and any exclusions. All currently **TBD**. The metadata preflight does not verify signal quality, label semantics, class balance, or source authenticity.

## Comparison / stopping rules

Use one frozen decoder's test probabilities for ungated, confidence-only abstention and drift-aware gating on **identical trial opportunities**. Choose policy thresholds from calibration only. Predeclare target action coverages 0.30, 0.50, 0.70; only compare risk at held-out coverage differences ≤0.05 absolute, report exclusions and coverage mismatches rather than manufacturing deltas. Report incorrect-action risk, correct-action retention, coverage, balanced accuracy, Brier and ECE with denominators; subject-paired uncertainty (9 subject units), class imbalance, drift-segment definitions and multiple-comparison caveats. No test-label-informed tuning.

**Advance only** if independent public-data reproduction shows useful coverage with reliably lower incorrect-action risk than confidence-only abstention at matched coverage, with traceable subject/session splits. **Reframe/kill drift-specific claims** if its apparent benefit disappears under matched coverage, across subjects, or after correcting leakage. Even positive results are research, **not clinical safety or live actuation evidence**.

## Evidence registry

| Item | Value |
|---|---|
| Source family | BCI Competition IV 2a / BNCI2014_001 |
| Dataset release/hash | TBD / TBD |
| Loader and dependencies | TBD |
| Source acquisition/execution | Not performed |
| Metadata split preflight | Fictional metadata only; local 9/9 tests passed 2026-10-27 (CI TBD) |
| EEG measurements, risk, uncertainty | TBD |
| Frozen synthetic baseline | [September execution](EXECUTION_RECORD.md), [cross-OS draft reproduction](SEPARATE_CONTAINER_REPRO_2026_10_26.md) |
| Maturity | Research / Simulation, unchanged |
| Next experiment | Acquire and hash actual BNCI2a session files, extract trial-only metadata, run preflight, freeze preprocessing/model and then evaluate held-out session E |

**Security/IP/privacy:** do not publish raw EEG, private identities, credentialed URLs, personal contact details, or employer data. Dataset subject numbers are public pseudonymous IDs, not participant names. Preserve source licensing and attribution.
