# WBI A01T v0.9 — first real training-session-only decoder pilot (2026-10-29 UTC)

**Verified, narrowly:** the previously fingerprinted public BNCI2014_001 A01T **training** MAT source was acquired and a four-class decoder was trained and scored on held-out runs **within the same training day**. This is **not** the preregistered different-day E-session test, not independent-subject replication, not a confidence-versus-drift comparison, and not evidence of real-world action safety. **Research / Simulation maturity unchanged.**

## Frozen method and provenance

The [protocol was committed before hosted EEG scoring](WBI_A01T_TRAINING_ONLY_PILOT_V09.md). Source: [BNCI/Graz public catalog](https://bnci-horizon-2020.eu/database/data-sets), A01T training MAT, 42,806,453 bytes; observed SHA-256 **054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325**. Hash identifies observed bytes, **not** publisher authenticity. Terms: CC BY-ND 4.0; no original EEG redistributed.

- 22 EEG channels (exclude all three EOG); 8–30 Hz fourth-order Butterworth, log-variance features from 2.5–4.5 seconds after trial start (cue at t=2 seconds).
- A01T task runs **1–3 train** (144 trials), **4 confidence-threshold calibration** (48), **5–6 held-out within-day test** (96). All task trials retained; three cue-free baseline blocks excluded. Training labels used; A01E **not downloaded** and E labels **not accessed**.
- Train-only StandardScaler and four-class logistic regression (C=1, lbfgs, max_iter=2000, seed 20261029); thresholds frozen from calibration confidences only, before held-out scoring.
- Hosted Python **3.13.17**, NumPy **2.3.3**, SciPy **1.16.2**, scikit-learn **1.7.2**; Ubuntu real-data job. [Code](bnci_a01t_training_run_pilot_v09.py), [fictional tests](test_bnci_a01t_training_run_pilot_v09.py), [read-only workflow](../../.github/workflows/wbi-a01t-training-only-pilot-v09.yml).
- GitHub Actions [run #40795478458](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40795478458), code-bearing branch head **5ae3801a6406b867e2e616012212bd9d281d0e29**; **two completed hosted attempts**. Fictional adversarial tests **15/15 on Ubuntu and 15/15 on Windows**; real training-only decoder job succeeded twice on Ubuntu. All completed job logs inspected.

## Observed aggregate result — same-day training-session holdout only

| Metric | Held-out A01T runs 5–6 |
|---|---:|
| Four-class accuracy | **43/96 = 44.7917%** |
| Balanced accuracy | **44.7917%** |
| Multiclass Brier (four squared errors summed per trial) | **0.595913** |
| Ten-bin maximum-confidence ECE | **0.143080** |
| Different-day E-session accuracy | **TBD — not tested** |
| Drift-aware gate benefit | **TBD — not tested** |

Confidence-only abstention thresholds were selected on **calibration run 4**. The achieved held-out coverage was *lower* than each calibration target, an important within-day transfer warning:

| Calibration target coverage | Frozen threshold (approx.) | Held-out acted / 96 | Incorrect / acted | Correct-action retention |
|---|---:|---:|---:|---:|
| 30% | 0.747399 | **19/96 (19.79%)** | **6/19 (31.58%)** | **13/43 (30.23%)** |
| 50% | 0.618928 | **38/96 (39.58%)** | **15/38 (39.47%)** | **23/43 (53.49%)** |
| 70% | 0.521577 | **55/96 (57.29%)** | **24/55 (43.64%)** | **31/43 (72.09%)** |

The ungated incorrect-prediction fraction is **53/96 = 55.21%**. Reduced incorrect-action *risk* at lower coverage cannot be interpreted as evidence that a drift gate works: **no drift gate was implemented or tested here**, and abstention sacrifices correct actions. These one-subject descriptive numbers are **not** a confirmatory performance claim or a confidence interval.

## Independent rerun and integrity verification

The same workflow was independently rerun (attempt 2), reacquiring the public training bytes and rerunning the real-data job. **All discrete results matched exactly**: source SHA-256, 43/96 correct, acted counts 19/38/55, incorrect acted counts 6/15/24, and all corresponding coverage/risk/retention ratios. Floating-point thresholds, ECE and Brier differed only at approximately **1e-14** between attempts; **do not claim byte-identical aggregate JSON**.

Both aggregate ZIPs were independently downloaded, SHA-256 checked against GitHub's artifact metadata, and inspected. Each contains exactly **one aggregate JSON**; no raw EEG, class-label vector, trial-level predictions or fitted model:
- Attempt 1: artifact **12863746663**, ZIP SHA-256 **448f8168129b0c64f232e67be646eca07c5163d46afe259e2b6b9a90071f6b73**; inner JSON SHA-256 **905ef839de6e1659e00a6c484d26dce47ba8ec4160cf62cb0bb5bdfa213156f1**.
- Attempt 2: artifact **12863448094**, ZIP SHA-256 **34d7379818a0ec00301858e7d3c995bab6bd00dce2bbb1b68b22fe036f0acf8e**; inner JSON SHA-256 **37105b3cf276f29744c55239100d2c8602eb8cf878d26776749a8d6659d4ec96**.

## Decision and next decisive experiment

**No stage advancement.** This is a reproducible exploratory baseline on **one subject, one training session**, not a public-EEG cross-session benchmark or validation of the proposed authorization gate. The within-day confidence-coverage shift cautions against assuming thresholds transfer to a later day. Original frozen [synthetic evaluator](SYNTHETIC_EVALUATOR.md) and [execution record](EXECUTION_RECORD.md), including negative drift-gate comparisons, remain unchanged.

**Next:** freeze and independently review a nine-subject, different-day E-session pipeline with held-out-label isolation, comparable coverage for confidence-only versus drift-aware gating, per-subject uncertainty and a separate defensible idle/rest protocol. Reframe the drift-specific contribution if it fails simpler confidence abstention at matched coverage. No clinical, therapeutic, patentability, human-actuation, employer or commercial claim.

**Four-lens review:** hiring manager — executable real-data baseline and rerun; technical reviewer — one-subject within-day selection and no E-session firewall tested; innovation leader — no drift-gate differentiation; founder — no validated safety or product benefit.


## Dataset-implementation cross-check (2026-10-29; changes next experiment)

Two documented MOABB project discussions independently reinforce limitations relevant to this exact loader:

- [MOABB issue #1073 — incorrect BNCI2014_001 stimulus illustration](https://github.com/NeuroTechX/moabb/issues/1073), closed 2026-05-20, points back to the publisher's **2-second fixation, 1.25-second cue and 4-second motor-imagery interval**. The pilot deliberately uses a 2.5–4.5-second post-trial-start window rather than copying an incorrect simplified diagram. This supports window provenance; it does **not** independently validate the MAT loader or classifier.
- [MOABB issue #1102 — artifact-flag preservation](https://github.com/NeuroTechX/moabb/issues/1102), closed 2026-06-27, describes how MAT trial-level artifact flags can be lost in MOABB conversion. This pilot **predeclared retaining all 48 trials per task run**, with no artifact exclusion. Consequently its 43/96 result must **not** be compared as equivalent to studies silently rejecting flagged trials. Before the nine-subject E-session benchmark, freeze a primary all-trials analysis and a separately reported artifact-flag sensitivity analysis; record actual flag counts, exclusions, and class/run denominators. Never tune exclusion policy on held-out outcomes.

These are source-backed **protocol decisions**, not claims of originality or proof of physiological robustness.
