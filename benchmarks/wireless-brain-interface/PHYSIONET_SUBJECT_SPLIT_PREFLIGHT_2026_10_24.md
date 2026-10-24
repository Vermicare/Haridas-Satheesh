# WBI — PhysioNet motor-imagery split preregistration (2026-10-24)

**Status: executable split preflight, not an EEG benchmark.** Stage remains **Research / Simulation**. No EDF files were downloaded, parsed, trained on, or scored in this experiment. No clinical, device, streaming, safety, novelty or product claims.

## Decision-changing dataset constraints

Source: PhysioNet [EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI [10.13026/C28G6P](https://doi.org/10.13026/C28G6P), ODC-By-1.0. The public data contain 109 subjects, 64 EEG channels, and 14 runs per subject. Task/event codes depend on the run. [MNE's EEGBCI run mapping](https://www.nmr.mgh.harvard.edu/mne/0.14/generated/mne.datasets.eegbci.load_data.html) identifies **4, 8, 12** as imagined left-versus-right fist, whereas **6, 10, 14** are imagined hands-versus-feet. Mixing these would silently corrupt labels.

[MOABB's PhysionetMI documentation](https://moabb.neurotechx.com/docs/generated/moabb.datasets.PhysionetMI.html) describes **one session** and flags subjects **88, 92, 100** as recorded at **128 Hz**, not 160 Hz. Therefore this dataset must **not** be described as a longitudinal multi-session validation. Sampling frequency must be inspected per actual EDF; no rate normalization, exclusion or result is claimed yet. MOABB's resampling behavior is an implementation detail, not evidence that the source recordings were uniform.

## Frozen preflight contract

- Executable generator: [eegmmidb_split_contract.py](eegmmidb_split_contract.py); tests: [test_eegmmidb_split_contract.py](test_eegmmidb_split_contract.py). Python 3.10+ standard library only.
- All subject identifiers 001–109 are ranked by SHA-256 of the fixed ASCII seed tag and subject ID, then assigned **70 train / 19 calibration / 20 held-out test** subjects. Groups are subject-disjoint; no held-out subject contributes training or calibration epochs.
- Only run numbers **04, 08, 12** are eligible; **T1 = imagined left fist, T2 = imagined right fist, T0 = rest excluded**. The generator enumerates **327 expected EDF paths**, without asserting their presence or integrity.
- Calibration subjects may select operating thresholds; test labels must never influence features, hyperparameters, drift-score construction, thresholds, exclusion decisions, or coverage matching. Any normalization, filtering or feature fitting that learns from data must be fit using train subjects only. Exact signal pipeline and decoder remain **TBD**, and must be locked before test labels are read.
- This is a **cross-subject generalization** protocol using runs from the same recorded session, not longitudinal drift validation. Separate genuine multi-session data would be needed for that claim.
- On real-data execution, preserve per-file checksums, actual sampling frequencies, channel/event checks, preprocessing versions, split membership, artifact hashes, exclusion reasons, run conditions, per-subject metrics and failures. All are currently **TBD**.

## Reproduce the current *preflight only*

From this directory:

```sh
python -m unittest -v test_eegmmidb_split_contract.py
python eegmmidb_split_contract.py --out eegmmidb_subject_splits.json
sha256sum eegmmidb_subject_splits.json
```

Local CPython 3.13.5 run on 2026-10-24: **11/11 contract tests passed**, including adversarial mutation of test membership, run IDs and fabricated data-verification status. The generated canonical JSON SHA-256 was `b626225f4560c30de94f6f7953c1f80c867712cb59e3bd929eeba4c0bdb26b67`; the generator source Git blob is `cd791df405dcf256984434c689eb239aff732162`, test source blob `de5bd64431afc13b6c9a88a85dff7f73c273bf9b`. [GitHub Actions #40103737750](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40103737750) **passed on Ubuntu and Windows**: both ran 11/11 split-contract tests, checked the identical pinned manifest SHA-256, reproduced byte-identical JSON twice, and uploaded generated artifacts. The unchanged frozen synthetic evaluator's independent [CI #40103737761](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40103737761) also passed. These are software/preflight tests only, **not** EEG evaluation.

The original [frozen synthetic evaluator](SYNTHETIC_EVALUATOR.md), [same-runtime execution record](EXECUTION_RECORD.md), and [cross-platform reproduction record](FROZEN_CROSS_PLATFORM_REPRO_2026_10_24.md) remain unchanged. This split preflight does not replace the frozen evaluator or supply real EEG evidence.

## Advancement, failure and stop rules

**Next actual evidence:** acquire a *small, pinned* subset of original EDFs, verify bytes and per-file sampling frequencies, inspect event mappings, then implement a leakage-tested baseline that feeds **the frozen evaluation definitions**. Declare decoder, drift score, calibration budget, risk–coverage matching and negative controls before held-out scoring. Use an independent dataset with multiple sessions if longitudinal adaptation is the hypothesis.

**Reframe:** if the drift gate is not better than calibrated confidence abstention at comparable coverage on genuinely held-out subjects, or if any improvement disappears under subject-level uncertainty and preprocessing-leakage checks, treat drift gating as an unproven optional diagnostic. Do not promote stage for passing split-contract tests.

**Four-lens review:** hiring manager—transparent preregistration; technical reviewer—subject leakage and run-label traps covered, real EDF validation missing; innovation leader—explicit stop gate; founder—no validated utility, user, clinical or patentability claim. No employer/private data or collaborator tracking is included.
