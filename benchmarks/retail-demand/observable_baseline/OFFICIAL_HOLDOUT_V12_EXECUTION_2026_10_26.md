# Retail v1.2 — verified publisher 90+7 held-out result (2026-10-26)

**Stage unchanged: Research / Architecture.** This is the first independently inspectable execution of the **official publisher 90-day train + seven-day eval split** for this portfolio experiment. It is an **observational in-stock sales** benchmark, not a measure of latent demand recovery, inventory performance, or business uplift.

## Execution provenance

- **Hosted execution:** [GitHub Actions #40342565683](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40342565683), successful Ubuntu job, code-bearing commit **aee03661442111a727e0fda44a534ad492e2e251**.
- **Frozen evaluator blob:** ddd12a4e0695c474f752d98c99fd781931373bce; **tests blob:** 6153f7631f143d62e915ef0f70482fa90d42ddee; **workflow blob:** 0c7a709d150950f944a389aeb97cd6f780b850de.
- **Runner:** Ubuntu Linux 6.17.0-1022-azure x86_64, Python 3.13.16, pyarrow 20.0.0. **10/10 fictional contract tests passed** before downloading real data.
- **Publisher revision:** 08c1fab7f9257bc73679d415d65d644165d351d4. Both downloaded Parquet files matched the publisher-reported SHA-256: train **6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d**, eval **1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e**. Origin was not independently authenticated.
- **Frozen cohort:** 512 series ranked by TRAIN-only seeded SHA-256. Cohort SHA-256 **7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710**. All 512 series had at least one uncensored eval day. **2,183 in-stock days scored; 1,401 censored days excluded.**
- **Preserved artifact:** [artifact #12659682091](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40342565683/artifacts/12659682091), expires **2026-11-09 14:45:42 UTC**. Downloaded ZIP SHA-256 **9cbc63175fb06983cf60d11a41fa53920fcf1f560d7b8784af2bb63f12eb3b5a**; member result JSON SHA-256 **e07b1b9384e240cc95f5b3c392987180a42fe1aa7377c8a6460d273bc85095e8**; provenance JSON SHA-256 **e89de5ef568bc6bba934a408343478180b06346373931d03d2ae8d780021a9cd**. Both members were inspected; summary calculations were independently recomputed from preserved aggregate values.
- **Machine-readable permanent summary:** [OFFICIAL_HOLDOUT_V12_RESULT.json](OFFICIAL_HOLDOUT_V12_RESULT.json). Full raw publisher data were **not uploaded**.

## Results — matched uncensored evaluation opportunities

| Method | Day-weighted MAE (lower better) | Per-series macro MAE |
|---|---:|---:|
| Last observed | **0.478562** | 0.474283 |
| Seasonal naive | 0.485180 | 0.483769 |
| Causal stockout-history correction | 0.479906 | **0.469314** |

Correction improved **day-weighted** MAE by **1.09% relative to seasonal naive**, but performed **0.28% worse than last observed**. The paired per-series macro delta (correction minus seasonal naive) was **−0.014455**; a seeded 2,000-resample **series-level** bootstrap gave an exploratory 95% interval **[−0.042840, +0.012164]**, crossing zero. No statistically robust superiority or general stockout-correction benefit is established. Related series may share stores/products, violating simple bootstrap independence.

**Contrast with prior negative evidence:** the earlier [train-only single-series run](PINNED_TRAIN_EXECUTION_2026_10_26.md) reported correction MAE 0.67 versus seasonal naive 0.56 on just 10 in-stock days. **Both results remain preserved**; differing split, cohort and sample sizes prohibit direct effect-size comparison.

## Evidence interpretation and next experiment

This execution verifies publisher-snapshot byte matching, train-only cohort selection, no eval-label forecast leakage under the frozen algorithm, reproducible test contract and actual held-out scoring. It does **not** recover true censored demand, establish intervention/stockout reduction, support a product claim, or validate production generality.

**Decision: retain mixed/negative evidence and do not advance stage.** Next: independently rerun the pinned experiment, then preregister a **store-clustered uncertainty analysis** and a stronger daily-count baseline on the same frozen cohort. If correction cannot outperform simpler baselines consistently under matched conditions, reframe toward an observability/diagnostic tool instead of promising forecasting uplift. Keep draft PR #9 unmerged until review; no release or external outreach is justified.

**Four lenses:** Hiring—inspect full runnable workflow and honest negative result; technical—challenge selection, censoring and bootstrap dependence; innovation—ask whether hourly stock flags add value beyond daily baselines; founder—no revenue, customer or ROI evidence.
