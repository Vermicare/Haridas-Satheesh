# Zhou2020 v0.7 — metadata-only candidate subject/session/run split

**Date:** 2026-10-30. **Stage:** Wireless Brain Interface Research / Simulation, unchanged. **Evidence:** local independent analysis of the SHA-256-pinned, public corrected event-file structural census v0.5; **not** original EEG verification, a prospective untouched preregistration, or a decoder experiment.

## Why this matters

The previous census confirmed 833 actual event-TSV files, not a uniform 840-file grid. Session/run availability is irregular, including nine files for subject 20 session 4, eight for subject 20 session 5, and no subject 20 session 6. A hard-coded six-runs-per-session split could silently drop or misassign files.

This script deterministically assigns **each subject’s highest available session index** to a *candidate* held-out test role, the immediately preceding available session index to calibration, and all earlier available session indices to training. It uses **only subject/session/run identifiers and source paths**, never event row counts, event types, EEG, decoder outcomes or model performance. The output includes a source Git blob per event TSV, a per-file role, per-subject allocation and provenance flags.

## Locally reproduced outcome

Input: exact original v0.5 census JSON, 216,160 bytes, SHA-256 `b891a3edfd8b1c535bc50032f7d46717de4f45d0eddbfd500f06430e757ec6b1`, corrected public upstream Git ref `a291ed8a2afab3f93b85a540134dceb98092fcaf`. Local CPython 3.13.5, standard library only, **10/10 tests passed** with original source. In a source-absent run, **8 tests passed, 2 original-source integration tests skipped**; do not misreport skips as passes.

**File allocation:** training **588**, calibration **123**, candidate test **122**; **833/833 unique files** assigned, **20/20 subjects** represented in all three roles. Subject 20 uses session 4 for calibration and session 5 for candidate test, **not** missing session 6. The canonical 833-entry JSON output is **SHA-256 `5ccad200cb36ca0414cef25e19d3dc5530f1a352bb9520b7d188170a162783d8`**. These counts are metadata-file counts, **not authenticated EEG trials**.

## Reproduce

Run from `benchmarks/wireless-brain-interface` with the exact frozen v0.5 JSON member from the previously preserved [v0.5 hosted evidence](ZHOU2020_EVENT_CENSUS_V05.md), saved as `frozen_v05_census.json` next to the scripts. The original JSON is intentionally not committed or modified. The script imports the existing v0.6 structural verifier; its test imports the existing v0.6 fictional fixture.

```bash
python -m unittest -v test_zhou2020_session_split_v07
python zhou2020_session_split_v07.py frozen_v05_census.json --output session_split_v07.json
sha256sum session_split_v07.json
```

The CLI rejects a mismatched source JSON byte hash. Adversarial tests cover duplicate subject/session/run, path metadata mismatch, boolean subject, count/label independence, irregular run availability and no-outcome-claim flags. The manifest itself is **generated locally**, not an EEG dataset or trained model.

## Source attribution and metadata discrepancy

The [public NEMAR nm000237 dataset README](https://github.com/nemarDatasets/nm000237/blob/main/README.md) identifies the Zhou et al. 2021 dataset and labels it **CC-BY-4.0**; cite the original investigators and the dataset source when reusing derived metadata. That README describes a **nominal** 20 × 7 × 6 × 40 = 33,600-trial grid, while the pinned corrected event-TSV census contains **833 files / 33,534 structural rows**. This is a metadata-level discrepancy, **not** proof of missing original EEG trials. The upstream repository has no GitHub API license object in the checked repository metadata; this attribution is based on its README's explicit license statement.

## Limits and gate

**Not a confirmed chronological or untouched held-out evaluation:** session *indices* have not been independently matched to actual acquisition timestamps; original NPZ recording bytes and event-to-NPZ pairing are **TBD**. Three event files had earlier exploratory trial-type preview disclosed in v0.4; this allocation was designed **after** structural event-count inspection. A test candidate must not be described as prospectively label-blind or as independently held out until source authenticity and a separate outcome-control protocol are established.

**Next decisive experiment:** authenticate a preregistered subset of original NPZ bytes, check one-to-one event-to-recording provenance and acquisition order, independently freeze the subject-specific train/calibration/test assignment before decoding results, then evaluate the unchanged underlying classifier with drift-aware gating versus confidence-only abstention at matched coverage. **Reframe/stop:** reject source mismatches, label leakage, non-independent outcomes or any claimed benefit that disappears at matched coverage. No maturity upgrade, clinical claim, release, patentability assertion or external review.

**Four lenses:** hiring manager — accountable data split without inflated accuracy; technical reviewer — deterministic file-level split and negative controls; innovation leader — source limitations and prior-art humility; founder — no validated users, efficacy or commercialization evidence. Employer/private data and collaborator tracking are excluded.

**Hosted cross-platform verification (verified 2026-10-30):** [GitHub Actions #41004917344](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41004917344) completed **success** at research head `0cfc30790dc4207cd26f47e3561cf3be10488d38`. Ubuntu (CPython 3.13.17) and Windows (CPython 3.13.16) independently downloaded the original v0.5 public-metadata artifact, passed **10/10 tests each**, and generated the **same 228,606-byte canonical JSON**, SHA-256 `5ccad200cb36ca0414cef25e19d3dc5530f1a352bb9520b7d188170a162783d8`. Both hosted logs were inspected; both original artifact ZIPs were downloaded and independently checked for archive integrity and identical JSON members. ZIP SHA-256 differs as expected: Ubuntu `de28d0476b01d792c2be3d232131f493a825afbe2b991a7edcea2a110a5d30d7`, Windows `b410e92a2f2899f50bef7b402a06769a473039f85b243f7a1d400f9e0d724980`. Hosted artifacts expire 2026-11-06; upstream v0.5 source artifact expires 2026-11-13. This is metadata-only reproducibility, not real EEG provenance or held-out evaluation.
