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
