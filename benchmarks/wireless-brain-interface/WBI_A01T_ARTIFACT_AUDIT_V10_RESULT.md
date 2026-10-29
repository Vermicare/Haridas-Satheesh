# WBI A01T v1.0 — independently rerun source artifact-flag audit (2026-10-29 UTC)

**Verified, narrowly:** A01T *training-session* MAT source contains **15 source-flagged task trials out of 288**, including **5 of 96** held-out within-day trials. The existing v0.9 all-trial decoding result **43/96** is **unchanged**. This audit does **not** measure artifact-free decoding accuracy, cross-day generalization, a drift gate, or human action safety. WBI remains **Research / Simulation**.

## Frozen protocol and actual source

[Pre-execution v1.0 protocol](WBI_A01T_ARTIFACT_AUDIT_V10.md), [executable read-only auditor](bnci_a01t_artifact_audit_v10.py), [15 fictional adversarial tests](test_bnci_a01t_artifact_audit_v10.py), [hosted workflow](../../.github/workflows/wbi-a01t-artifact-audit-v10.yml). These were published before the hosted source audit. The v0.9 frozen decoder, [real-data result](WBI_A01T_TRAINING_ONLY_PILOT_V09_RESULT.md), [original synthetic evaluator](SYNTHETIC_EVALUATOR.md), and [synthetic execution record](EXECUTION_RECORD.md) were **not modified**.

The only fetched source was **BNCI2014_001 A01T.mat**, observed **42,806,453 bytes**, SHA-256 **054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325** (observed fingerprint, not publisher signature). The auditor requires exactly six task runs of 48 strictly ordered one-based trial positions, each with 48 binary source `artifacts` flags. No A01E or evaluation-session labels were fetched. No per-trial flags, EEG samples, predictions, or class labels were persisted.

## Independently reproduced actual counts

| A01T task run | Trials | Source artifact-flagged | Unflagged |
|---|---:|---:|---:|
| 1 (train) | 48 | 2 | 46 |
| 2 (train) | 48 | 4 | 44 |
| 3 (train) | 48 | 3 | 45 |
| 4 (calibration) | 48 | 1 | 47 |
| 5 (within-day holdout) | 48 | 2 | 46 |
| 6 (within-day holdout) | 48 | 3 | 45 |
| **All six** | **288** | **15** | **273** |

Split totals: training **9/144 flagged**, calibration **1/48 flagged**, held-out within-day **5/96 flagged**.

Given only the independently reproduced v0.9 **43 correct out of 96** and the **five held-out flagged** trials, the actual number of correct **unflagged** predictions is logically between **38 and 43**, inclusive. Therefore the *identification bounds* for unflagged accuracy are **38/91 = 41.76%** to **43/91 = 47.25%**. **These are sharp mathematical possibilities, not a measured artifact-free score, confidence interval, or new classifier result.** We deliberately did not inspect the per-trial correctness-by-artifact joint distribution.

## Hosted provenance and independent archive verification

[GitHub Actions run #40808451206](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40808451206), code-bearing commit `11b66b9f5bc0fcab7ab99c29fe1a91fa9514e23a`. Python 3.13; NumPy 2.3.3, SciPy 1.16.2, scikit-learn 1.7.2 pinned. **15/15 fictional tests passed on Ubuntu and 15/15 on Windows.** Real A01T source audit succeeded on Ubuntu in **two hosted attempts**. Both logs independently inspected.

- Attempt 1 aggregate ZIP artifact `12868983171`, SHA-256 `913eebc37436f6b70c88dfd66cf647a8b4a799f651483e10421a30a05da838ef`; inner JSON SHA-256 `e9e567540b5b67002416ab0f27a5726062ed03867a6e7c2875d1d345e4a257cb`.
- Attempt 2 aggregate ZIP artifact `12869262705`, SHA-256 `de6a1f3d6a925889b8a6f1407f80b3de06c8b1c41397f8d25f6b8d3eb99d2597`; inner JSON SHA-256 `f6a48200d171ce5cf4928c676de44b1c0ce429edd0c31ab229cd6a0d8f8e84c7`.

Both ZIPs were downloaded, their SHA-256 digests independently matched GitHub's published artifact digests, and their **single JSON member** was inspected. All substantive fields (including six run counts, split counts, source fingerprint, frozen score, and bounds) matched exactly; only `run_utc` differed. **Do not claim ZIP or inner JSON byte identity.** The source/test Git blobs were reread after publication. No raw EEG or trial-level records appeared in the archives.

## Decision and limitations

[Original competition dataset description](https://www.bbci.de/competition/iv/desc_2a.pdf), [MOABB source implementation](https://github.com/NeuroTechX/moabb/blob/develop/moabb/datasets/bnci/base.py), and [MOABB issue #1102](https://github.com/NeuroTechX/moabb/issues/1102) support treating artifact flags as an explicit, nontrivial evaluation choice. Source flags are expert-identified artifact annotations, **not** verified ground-truth model failure or a physiological quality guarantee.

**Next decisive experiment:** prefreeze a separate, label-safe trial-level sensitivity scorer that reports the *actual* unflagged subset result alongside the original all-trial result, preserving both denominators and never refitting/tuning on held-out outcomes. Then independently evaluate different-day E sessions and nine subjects, with matched-coverage confidence-only versus drift-aware gating and an explicit idle/rest protocol. Do not promote maturity from this source audit.

**Four-lens review:** hiring manager — reproducible data-integrity practice; technical reviewer — flags counted but no observed clean-subset accuracy; innovation leader — no demonstrated drift-gate advantage; founder — no safety, deployment, or market evidence. No release, patentability claim, collaborator commitment, or employer data.
