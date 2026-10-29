# WBI v1.2 — prospective A01E different-day *baseline* protocol (2026-10-29)

**Frozen before first A01E scoring.** This is an exploratory one-subject, different-day transfer test, **not** the nine-subject confirmatory gate, drift-aware advantage, rest-state safety or clinical validation. The frozen v0.9 A01T result and synthetic evaluator are not replaced.

## Hypothesis and decision

Question: how well does the unchanged v0.9 four-class decoder trained on A01T task runs 1–3 and confidence-calibrated on A01T task run 4 transfer to A01E, a different recording day? This is a **descriptive baseline**, not a claim that any new gate helps. A01T runs 5–6 remain the historical within-day holdout, not a model-selection resource. No tuning, refitting, feature selection or threshold adjustment using A01E samples or labels.

## Frozen before scoring

- Dataset: publisher's BNCI2014_001 / BCI Competition IV 2a; subject A01; A01T.mat pinned SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325` (observed, not publisher-signed); A01E.mat hash/size **TBD before first acquisition** and must be recorded, then independently reacquired and compared.
- Frozen training-only v0.9 code Git blob `9293fdeff26b621e966da2cd76ab2da1e3220e7f`; 22 EEG channels, 250 Hz, separate-run 8–30 Hz fourth-order Butterworth SOS filtering; 2.5–4.5 s after one-based trial start; 22 log-variance features, training-only StandardScaler and LogisticRegression(C=1, lbfgs, max_iter=2000, random_state=20261029). No EOG feature channels.
- Train A01T task runs 1–3 (144 trials), select confidence-only thresholds using A01T run 4 (48 trials), **not** E data; A01E all six task runs (expected 288 trials) is the prospective held-out set. Retain all trials as primary denominator regardless of artifact flags; report source-flag counts separately only when valid flags are present. No E-label-informed exclusion.
- Report: exact correct/total, four-class accuracy, balanced accuracy, multiclass Brier sum-of-squares, ten-bin max-confidence ECE; frozen calibration coverage targets 30%, 50%, 70%, with *actual* E acted/incorrect counts, coverage, risk, correct-action retention and zero-acted handling. Do **not** compare different coverages as proof of gate superiority.
- Any source format discrepancy, absent E labels, mismatched class mapping, missing/invalid artifacts, source hash change, missing cue positions, or unexpected dimensions must **fail closed** or be explicitly marked unavailable; no silent imputation.
- For integrity, a later scoring script should seal predicted probabilities before E labels are read; a single-process exploratory implementation that accesses E labels only after fitting must explicitly disclose this weaker firewall. Never persist raw EEG, trial-level labels, trial-level probabilities, device identifiers or personal information to public CI artifacts.
- Python 3.13; numpy 2.3.3; scipy 1.16.2; scikit-learn 1.7.2. Source/redirect allowlist, SHA-256, exact CI commit, run timestamp, host environment, failed attempts, and public aggregate-only registry are required.

## Advance / stop

No stage advancement on A01 alone. Stop and preserve failure if the evaluation labels are not available in the public MAT distribution, if a leak is detected, or if the source identity changes unexpectedly. If different-day decoding or confidence-only action risk deteriorates, report it without tuning to the held-out session. Nine-subject preregistered paired analysis and matched-coverage drift gate, rest-state false actions, independent reviewer, hardware latency and safety all remain **TBD**.

Primary sources: [BNCI catalog](https://bnci-horizon-2020.eu/database/data-sets), [BCI Competition IV](https://www.bbci.de/competition/iv/), [competition review](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2012.00055/full). The original competition E GDFs were unlabeled; the separately distributed BNCI MAT representation may differ. This protocol does **not** assume E MAT labels exist without checking the source.

## First hosted execution — observed, awaiting independent second run (2026-10-29)

[GitHub Actions #40844154710](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40844154710) at code head `dffa50c33fe95bba516fe95bd1698ea561725f48` passed **19/19 fictional tests on Ubuntu and 19/19 on Windows**. The public A01E MAT was successfully acquired, 43,772,146 bytes, observed SHA-256 `53d415f39c3d7b0c88b894d7b08d99bcdfe855ede63831d3691af1a45607fb62` (**not publisher-signed**); E labels and artifact flags were available in this derived MAT distribution. Frozen A01T source SHA and v0.9 code blob matched.

The *one-subject* A01E held-out exploratory result was **165/288 correct (57.2917% four-class accuracy and balanced accuracy)**, Brier sum-of-squares **0.5572808992**, ECE **0.0950105223**, with **7/288 source-flagged E trials** retained in the primary denominator. Calibration-only confidence thresholds yielded actual A01E (acted, incorrect): 30%-target **(59,20)**; 50%-target **(136,47)**; 70%-target **(194,76)**. These are **not** matched-coverage gate comparisons and do not establish a safety benefit. The original within-day A01T 43/96 remains unchanged; different trial sets mean the numeric difference is **not** a controlled improvement.

[Aggregate artifact #12883982888](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40844154710/artifacts/12883982888) ZIP SHA-256 `e39c824a72a10ac7eb23f18e70df89e553ba062a72dfb9e85b97706d4e657508`; independently downloaded and inspected, JSON member SHA-256 `60ad223f7fc2f9fe8f865f62d6c97e69b3632900ec52d57974aa04f3ab7f328a`. No raw EEG, trial-level predictions or labels were uploaded. Python **3.13.17**, NumPy **2.3.3**, SciPy **1.16.2**, scikit-learn **1.7.2**.

**Integrity limitations:** The pre-label prediction digest `3f07b8fe6c52709ed56dd0dbc49ac0bccc40761a44aa9e5d5090fe2f604627b7` was computed in the *same process* and not externally time-stamped. This is a weaker label firewall than independently sealed predictions. Source hash authenticates observed bytes, not publisher provenance. **Independent hosted reacquisition/reproduction is pending**; do not treat this first run as independent replication. Nine-subject E-session, matched-coverage drift gate, idle false actions, and clinical validation remain **TBD**.

## Independent second hosted acquisition and numeric-reproducibility finding

[GitHub Actions #40844371552](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40844371552) at documentation-only head `5920bce3ca149289b23278e912c8d89be79ebcdd` independently reacquired **identical A01E source bytes** (SHA-256 `53d415f39c3d7b0c88b894d7b08d99bcdfe855ede63831d3691af1a45607fb62`) and reproduced **165/288 correct, 7 source-flagged, and all three exact acted/incorrect pairs (59/20, 136/47, 194/76)**. Both runs passed **19/19 fictional tests per operating system**. [Second aggregate ZIP #12884008455](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40844371552/artifacts/12884008455) SHA-256 `37f47b9f0d9bae1baee742908566ba8adcb6bdde9cab81f2d8817860bd213cfe`; independently downloaded and inspected; member JSON SHA-256 `b9e649ab4544f5c05b7a64e08993598c85e384bca1f715d790ba3b4c624022e5`.

**Important reproducibility limit:** raw float64 prediction hashes **differed** between hosted runs (`3f07b8fe...` versus `d925f081...`) and the frozen confidence thresholds differed at about **7.3×10^-15 to 5.7×10^-14**; substantive discrete counts, source identity, ECE to displayed precision and overall accuracy matched. Therefore claim **aggregate/discrete reproducibility, not byte-identical probabilities**. The likely cause is floating-point numerical variation; the cause was not experimentally isolated.

Following these **two independent observations**, the source identity was pinned in the additive v1.2 implementation (not the v0.9 model), with two new fictional mutation tests. This was a *post-observation integrity pin*, **not** a pre-acquisition publisher signature or a model/hyperparameter change. A final-head run with this pin is required before declaring the fail-closed source check verified.
