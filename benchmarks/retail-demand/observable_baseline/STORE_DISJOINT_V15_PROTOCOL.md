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


## Verified first execution and decision — 2026-10-27

[GitHub Actions run #40445663158](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40445663158) **passed 33/33 fictional contract tests** and completed the one frozen publisher-data evaluation. Both original train/eval byte hashes matched; the immutable publisher revision URLs returned HTTP 404 and fallback to publisher main was accepted **only after both original SHA-256 pins matched**. Frozen v1.2/v1.4 source Git blobs matched. Python 3.13.16, Ubuntu runner, pyarrow 20.0.0; precise platform and source blobs are in [provenance](STORE_DISJOINT_V15_PROVENANCE.json).

The new cohort contains **512 series across 293 stores**, with **zero store overlap** with the original 512-series / 374-store cohort. Of 3,584 possible evaluation days, **2,092 in-stock days** were scored and **1,492 censored days excluded**. All 512 series had at least one in-stock evaluation day. Day-weighted observed-sales MAE:

| Frozen comparator | New store-disjoint cohort MAE |
|---|---:|
| Causal stockout-history | **0.499880** |
| Seasonal naive | 0.514213 |
| Weekday median (v1.4) | 0.516406 |
| Last observed | 0.536860 |

**Predeclared primary gate FAILED:** weekday median improved the point MAE over last-observed, but the paired store-cluster 95% interval for weekday-minus-last-observed per-series MAE was **[−0.063019, +0.033285]**, crossing zero. No superiority claim.

**Secondary, non-primary observation:** stockout-history outperformed weekday median in point MAE; the paired weekday-minus-correction store-cluster interval was **[+0.000875, +0.043310]**. This is exploratory, with multiple-comparison and same-date limitations; it does **not** establish stockout correction's latent-demand recovery, causal value or temporal generalization. The changed ranking relative to the original cohort is a useful **heterogeneity/instability finding**, not a basis to choose a winner post-hoc.

[Exact aggregate result](STORE_DISJOINT_V15_RESULT.json) and [run provenance](STORE_DISJOINT_V15_PROVENANCE.json) were preserved **byte-identically** from the downloaded hosted artifact: ZIP SHA-256 dbdd3c83e901bbcf4a74196656368a392545e57d7bcc129fd937a0bc41c367f7; result SHA-256 adcb2d0db4c27a32fd996f65b48f81b45465387a7b8bf010cb65bfd67bf762df; provenance SHA-256 aa984fc3ae3fad5b85f555e527ace2b673f2e435a7bda0e4bb592eebbe92f7e3. Both committed Git blob identities were checked against the downloaded artifact's original bytes. Raw publisher rows were not committed.

**Decision:** maintain Research / Architecture, preserve the failed primary gate, and require an untouched temporal/external holdout with independent model implementation, product/store dependence and decision-value metrics before any maturity or performance promotion. No release, merger, real-world intervention or collaborator result.
