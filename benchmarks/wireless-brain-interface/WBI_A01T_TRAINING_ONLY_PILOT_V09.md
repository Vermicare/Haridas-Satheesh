# WBI v0.9 — exploratory A01T training-only EEG decoder

**Protocol frozen before first live EEG scoring.** Current evidence: local fictional tests only. Actual A01T decoder performance, reproducibility and confidence-only selective risk are **TBD** until hosted execution. This is **not** the preregistered different-day E-session study. Stage remains Research / Simulation.

## Fixed source, splits and method

- Source: BNCI2014_001 A01T **training** MAT only, via allowlisted official BNCI/Graz HTTPS route. Previously observed source identity: **42,806,453 bytes**, SHA-256 **054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325** ([prior provenance](BNCI_MAT_SOURCE_PROBE_V01.md)). This is an observed fingerprint, not a publisher signature. [BNCI catalog and CC BY-ND 4.0 terms](https://bnci-horizon-2020.eu/database/data-sets); [original competition paradigm](https://www.bbci.de/competition/iv/desc_2a.pdf).
- Trial cue is at **t=2 s** after trial start. Epoch is **2.5–4.5 s after trial start**, or 0.5–2.5 s after cue. Exactly 22 EEG channels, excluding all three EOG channels. Ignore three cue-free baseline blocks. Do not assume MAT block index 0 is task run 1.
- Split **within A01T only**: task runs **1–3 train** (144 trials), **4 calibration** (48), **5–6 held-out test** (96). No A01E download, evaluation-session label inspection, artifact-based exclusions or trial-level output.
- Per-run fourth-order 8–30 Hz Butterworth filtering; log-variance features over 22 channels; train-only StandardScaler plus four-class logistic regression (C=1, lbfgs, max_iter=2000, seed 20261029). Cal-only confidence quantiles target 0.30, 0.50 and 0.70 coverage; test labels never influence model or thresholds.
- Report held-out four-class accuracy, balanced accuracy, multiclass Brier sum-of-squares, ten-bin max-confidence ECE, and at each frozen confidence threshold: actual coverage, incorrect acted / acted, correctly acted / all correct predictions, and denominators. Zero acted => null risk, not zero.

## Reproduction and boundaries

Pinned Python 3.13 dependencies: numpy==2.3.3, scipy==1.16.2, scikit-learn==1.7.2. Run the [fictional adversarial tests](test_bnci_a01t_training_run_pilot_v09.py), then [the executable](bnci_a01t_training_run_pilot_v09.py) with --output pointing to a **new** local JSON path. The [read-only hosted workflow](../../.github/workflows/wbi-a01t-training-only-pilot-v09.yml) runs tests on Ubuntu and Windows, acquires real A01T only on Ubuntu and uploads **aggregate JSON only**, never raw EEG, trial labels, individual predictions or fitted weights.

This pilot tests software feasibility on **one subject, one training day**, not longitudinal transfer, idle-state false-action safety, calibrated human authorization or drift-gate superiority. The original [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md) and its [execution record](EXECUTION_RECORD.md) remain unchanged, including their negative confidence-versus-drift comparison. Any negative or near-chance live result must be retained.

**Advance only after:** independent reproduction of held-out different-day EEG on multiple subjects with confidence-only versus drift-gate risk compared at matched coverage and uncertainty. **Kill/reframe:** if a drift gate fails a simpler abstention comparator, or leakage-free decoding cannot be demonstrated. Real E-session metrics, safety, latency, energy, clinical validation and deployment remain **TBD**. No patentability or novelty claim.
