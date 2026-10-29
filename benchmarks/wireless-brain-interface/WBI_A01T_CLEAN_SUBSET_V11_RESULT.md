# WBI A01T v1.1 — observed clean-subset sensitivity, independently rerun (2026-10-29 UTC)

**Verified narrowly:** reusing the frozen v0.9 A01T training-session-only decoder, the **91 source-unflagged held-out trials** had **42 correct predictions (46.15%)**. The unchanged **all-trial primary result remains 43/96 (44.79%)**. This is a **post-hoc descriptive sensitivity analysis**, not a new preregistered hypothesis test, cross-session EEG benchmark, causal artifact effect, drift-gate comparison or action-safety result. Maturity remains **Research / Simulation**.

## Frozen protocol and provenance

The [v1.1 pre-execution protocol](WBI_A01T_CLEAN_SUBSET_V11.md) was committed at `a44bd7f08a9a150fd49d17954f354ef8761c9693` **before** the hosted real-data workflow. The [executable](wbi_a01t_clean_subset_v11.py), [14 fictional adversarial tests](test_wbi_a01t_clean_subset_v11.py), [read-only workflow](../../.github/workflows/wbi-a01t-clean-subset-v11.yml), and [machine-readable registry](WBI_A01T_CLEAN_SUBSET_V11_REGISTRY.json) are on unmerged draft PR #16.

- Public BNCI2014_001 **A01T.mat training source only**, 42,806,453 bytes, observed SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325` (observed fingerprint, **not** publisher signature); no A01E download or labels.
- Existing v0.9 run split **1–3 training / 4 calibration / 5–6 within-day held-out**, existing 22-channel feature pipeline, trained model and calibration-only thresholds reused unchanged. v1.0 source flags **2,4,3,1,2,3** were verified again; **five of 96** held-out trials flagged.
- Flags were applied **only after** generating the same frozen held-out predictions. No refit, recalibration, exclusion from original primary score, held-out tuning, or trial-level output. Aggregate JSON only; no EEG, trial-level flags, predictions or labels persisted.

## Actual observed descriptive sensitivity

| Quantity | All 96 held-out trials | 91 source-unflagged trials |
|---|---:|---:|
| Correct predictions | **43/96** | **42/91** |
| Four-class accuracy | **44.79%** | **46.15%** |
| Source-flagged trials | 5 | 0 |
| Calibration 30% threshold: acted / incorrect | 19 / 6 | 19 / 6 |
| Calibration 50% threshold: acted / incorrect | **38 / 15** | **37 / 15** |
| Calibration 70% threshold: acted / incorrect | 55 / 24 | 53 / 23 |

At the **unchanged** calibration-50% confidence threshold, incorrect-action risk was **15/38 = 39.47%** on all trials and **15/37 = 40.54%** on the source-unflagged subset: excluding flagged trials **did not improve** that operating point. At the calibration-30% threshold, the same 6/19 errors remained; at 70%, risk changed from 24/55 = 43.64% to 23/53 = 43.40%. These are *different denominators* and descriptive comparisons, not matched-coverage intervention effects.

Only **one of five flagged trials** was correctly classified in this frozen pilot; this does **not** establish that artifact flags caused the other errors. The earlier v1.0 mathematical identification interval **38/91 to 43/91** is retained as the valid pre-scoring bound; **42/91** is now the observed value within that interval. Original v0.9 all-trial and synthetic evaluator results remain unchanged.

## Independent hosted verification

[GitHub Actions run #40813817810](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40813817810), code-bearing commit `8b4ac05c71766f3dfb9d1fa7e0f7e11e1df0bb90`, **two successful hosted attempts**. Ubuntu and Windows each passed **14/14 fictional adversarial tests in both attempts**; Ubuntu independently reacquired A01T and reproduced **all discrete metrics and substantive rates** twice. CPython 3.13.17, NumPy 2.3.3, SciPy 1.16.2, scikit-learn 1.7.2; exact runner image **TBD**. Both Ubuntu real-data job logs were inspected.

Both aggregate-only ZIPs were downloaded, independently SHA-256 checked against GitHub's artifact metadata and opened; each contains **one JSON file only**. No raw EEG, trial-level flags, labels or predictions were present.

| Hosted attempt | Artifact ID | ZIP SHA-256 | Inner aggregate JSON SHA-256 |
|---|---|---|---|
| 1 | `12871836222` | `a15676a595c0f097a7f0b787fd7f77cae436a7f4f014d43ae6e978f227e251d2` | `5231abfc0cda8191e4ebefc5439d8ff05293993958ecec99b6cc28fa50973e99` |
| 2 | `12871154131` | `da8edd358d1c58c2844485e5761ed8f7c163bb6b2776afa582220c3239b1a23e` | `0b96fae725731d8b69c8b6f9188efe887e6370db26703cb589e4c6ac88308ee7` |

UTC timestamps and floating confidence thresholds differed at approximately 1e-14; **do not claim byte-identical JSON or ZIPs**. Source and tests were reread and matched independently locally computed Git blob IDs.

## Research decision

**No maturity advancement.** The observed source-unflagged accuracy **42/91** is a narrow same-day sensitivity check. Source flags are not a randomized intervention, do not identify physiological causes of error and cannot validate the proposed drift-aware authorization gate. Different-day E-session performance, nine-subject replication, idle-state false-action risk, matched-coverage drift benefit, latency, energy and real-world/clinical safety remain **TBD**.

**Next decisive experiment:** freeze an E-session, nine-subject evaluation firewall and compare confidence-only abstention versus drift-aware gating at **identical actual action coverage**, with per-subject uncertainty and all-trial plus separately reported flag sensitivity. **Kill/reframe:** if drift gating does not beat simpler abstention across sessions/subjects, remove the drift-specific superiority thesis.

**Four lenses:** hiring manager — reproducible real-data descriptive evidence and honest negative operating-point finding; technical reviewer — correct separation of source flags from fitting, but post-hoc and one-day; innovation leader — no proven drift differentiation; founder — no validated safety, market, clinical or product benefit. No release, merge, patentability claim, external action or employer data.
