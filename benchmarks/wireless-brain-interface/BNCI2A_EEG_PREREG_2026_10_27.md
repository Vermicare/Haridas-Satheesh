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
| Metadata split preflight | Fictional metadata only; 9/9 tests passed on Ubuntu and 9/9 on Windows in GitHub Actions #40415140397 (2026-10-27 IST); both job logs inspected |
| EEG measurements, risk, uncertainty | TBD |
| Frozen synthetic baseline | [September execution](EXECUTION_RECORD.md), [cross-OS draft reproduction](SEPARATE_CONTAINER_REPRO_2026_10_26.md) |
| Maturity | Research / Simulation, unchanged |
| Next experiment | Acquire and hash actual BNCI2a session files, extract trial-only metadata, run preflight, freeze preprocessing/model and then evaluate held-out session E |

**Security/IP/privacy:** do not publish raw EEG, private identities, credentialed URLs, personal contact details, or employer data. Dataset subject numbers are public pseudonymous IDs, not participant names. Preserve source licensing and attribution.

**Hosted verification:** [Actions #40415140397](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40415140397) passed on Ubuntu and Windows, preserving the frozen synthetic evaluator Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9` and CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`. Both logs show all nine fictional metadata regressions passing. This is software-contract evidence, not EEG validation.


## October 27 source-archive gate — no real data ingested

**New primary-source constraint:** the official BCI Competition IV dataset 2a training GDFs contain cue class events 769–772, while evaluation GDFs use an unknown cue marker (783) and their class labels are released separately. The publisher's dataset download lists a roughly 420 MB GDF archive. Consequently **E labels must not enter acquisition preflight, training, calibration, or threshold selection**. An E-session accuracy score is not available merely from reading the E GDF. The dataset also has eyes-open/eyes-closed idle calibration events, but these do **not** by themselves constitute a validated continuous rest/false-action evaluation protocol.

Primary sources: [official dataset download](https://www.bbci.de/competition/iv/download/); [competition review with event codes and E-label separation](https://pmc.ncbi.nlm.nih.gov/articles/PMC3396284/).

Added a **no-extraction source-archive inspector** ([implementation](bnci2a_source_archive_preflight.py); [14 synthetic ZIP tests](test_bnci2a_source_archive_preflight.py)). It checks all 18 named T/E GDF files, SHA-256 of archive and members, ZIP CRC on streamed GDF bytes, GDF signature, member/path duplication, traversal, symlinks, encrypted members, size/ratio limits and exclusion of embedded MAT/other non-document files. It writes **hashes and sizes only**; never extracts EEG, imports labels or runs a decoder. The source URL field is explicitly a *declared, unverified* provenance string, not publisher authentication. The separate BNCI2a trial split preflight still requires genuine source-derived run/trial metadata and cannot be satisfied by this ZIP check alone.

To run **after independently obtaining the publisher archive** (do not commit the archive, extracted signals, evaluation labels or personal information):

    python -B benchmarks/wireless-brain-interface/bnci2a_source_archive_preflight.py --archive /private/path/BCICIV_2a_gdf.zip --out /private/path/source_manifest.json --source-url https://www.bbci.de/competition/download/competition_iv/BCICIV_2a_gdf.zip

**Run provenance:** local CPython 3.11 Linux standard-library-only synthetic ZIP fixtures; 14/14 tests passed. GitHub-hosted Ubuntu/Windows verification is **TBD** until the current workflow run is inspected. Actual 420 MB archive download was unavailable in this execution environment; actual publisher SHA-256, per-file SHA-256, GDF event counts, source authenticity, loader version, test labels, all EEG outcomes and safety claims are **TBD**. This is a *software and acquisition-integrity gate*, not a real EEG benchmark or maturity advancement.

**Next decisive evidence step:** acquire the 18 actual GDFs from the official publisher; run this gate; preserve source hash/URL/terms; then use a pinned GDF loader to derive **real** trial/run identifiers without E class labels and check the 18 predeclared folds. Only after freezing preprocessing, classifier and thresholds may E labels be loaded in an isolated final scoring stage. Report idle/rest separately with defensible windows; do not infer false-action safety from motor-imagery accuracy.
