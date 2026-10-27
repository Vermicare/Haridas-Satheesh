# Retail v1.5 — predeclared store-disjoint series transfer (2026-10-27)

**Evidence boundary:** This is a new, training-selected **store-disjoint cohort** on the **same publisher evaluation dates (2024-06-26 to 2024-07-02)** previously inspected for other stores. It is **not a new temporal holdout, independent dataset, latent-demand test, causal intervention, product result, or external review**. Maturity remains Research / Architecture.

## Question and frozen decisions (before inspecting this cohort's evaluation labels)

Does the v1.4 **post-hoc selected** weekday-median forecast outperform the v1.2 last-observed baseline on stores completely absent from the original v1.2/v1.4 512-series cohort?

- **Publisher:** Dingdong-Inc/FreshRetailNet-50K. Frozen train SHA-256 6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d; evaluation SHA-256 1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e. Dataset byte checks are necessary, not independent source attestation.
- **Original cohort:** reconstruct exactly 512 original series from TRAIN IDs only using frozen v1.2 SHA-256 ranking. Assert original cohort digest 7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710.
- **New cohort:** exclude **all stores** represented in the original cohort, not merely its store/product pairs. From remaining TRAIN IDs, choose the 512 lowest SHA-256 ranks of the string retail-store-disjoint-v15-20261027|store_id|product_id. Do not read evaluation data during selection. Do not replace any selected series if evaluation coverage is missing.
- **Forecasts:** exact frozen v1.2 last-observed, seasonal naive and causal stockout-history; exact frozen v1.4 weekday median of last four in-stock same-weekday training days, with documented fallbacks. Do not retune.
- **Outcome:** observed in-stock business-hour sales, not latent demand. Exactly 90 TRAIN and seven EVAL days per selected series are required; report missingness rather than substituting stores.
- **Primary comparison:** weekday median versus last-observed. Predeclare paired store-cluster 95% percentile bootstrap interval for per-series MAE difference (2,000 resamples, seed 20261027) and day-weighted MAE. A *conditional store-transfer gate* requires both lower weekday day-weighted MAE and an interval upper bound **strictly below zero**. Crossing zero fails the gate. The original v1.4 confidence interval was [−0.055629, +0.023005] and did not establish superiority.
- **Secondary/descriptive:** seasonal-naive and stockout-history comparison; macro MAE, store counts, scoring denominator and training-only fallback counts. No new comparator or significance rule may be added after the result.
- **Kill/reframe:** if the primary gate fails, do not promote weekday median or stockout correction as superior. If it passes, call it **conditional same-date cross-store transfer evidence only**; require a genuinely new temporal period/external dataset and decision-value outcome before any stronger claim.

## Reproduction

From the benchmark directory after obtaining publisher original matching Parquet bytes, run:

    python -B -m unittest -v test_official_holdout_v12 test_weekday_median_v14 test_store_disjoint_v15
    python -m pip install pyarrow==20.0.0
    python store_disjoint_v15.py --train /path/train.parquet --eval /path/eval.parquet --output /new/path/store_disjoint_v15_result.json

The hosted workflow is [retail-store-disjoint-v15.yml](../../../.github/workflows/retail-store-disjoint-v15.yml). It verifies original source blobs, dataset byte hashes, original cohort digest and new cohort store separation. It uploads only aggregate results and a run-provenance JSON; original publisher rows remain runner-local. Existing v1.2–v1.4 source and result files are not modified.

## Pre-run evidence registry

| Item | Value |
|---|---|
| Experiment ID | retail-store-disjoint-transfer-v15 |
| Dataset / publisher | FreshRetailNet-50K / Dingdong-Inc |
| Train/EVAL byte hashes | Pinned above; reverify at execution |
| Cohort selection seed | retail-store-disjoint-v15-20261027 |
| Target selected series | 512, entirely different stores from original 512 |
| Python | 3.13.x in CI; exact patch TBD |
| Parquet reader | pyarrow 20.0.0 |
| Code / test revisions | Branch research/retail-store-disjoint-v15-20261027; record final commit and blobs after execution |
| Observed results, CI run, scoring denominator | **TBD until verified** |
| Publisher data redistribution | None |
| Independent temporal holdout / external review | TBD / TBD |
| Stage change | None |

**Four lenses:** hiring manager—transparent comparison and negative results; technical reviewer—same-date limitation and frozen selection; innovation leader—no promotion on favorable post-hoc point estimate; founder—no sales uplift, inventory value, users, pilot or deployment claim.
