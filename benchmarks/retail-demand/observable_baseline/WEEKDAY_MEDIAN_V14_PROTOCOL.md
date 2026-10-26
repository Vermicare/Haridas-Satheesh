# Retail v1.4 — post-hoc weekday-median comparator (2026-10-27)

**Status:** code-bearing [hosted CI #40397695520](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40397695520) **PASSED**; exact aggregate JSON and provenance verified against the hosted artifact and permanently preserved. **Maturity: Research / Architecture, unchanged.** This is a stacked research branch based on the existing v1.2/v1.3 draft; no main-branch merge or release.

## Question and evidence boundary

The original official 90-day training / seven-day evaluation benchmark on 512 train-selected series found that stockout-history correction did not reliably beat simple baselines. Its original, independently rerun v1.2 results and the v1.3 store-cluster interval are preserved unchanged. A decision-changing next question is whether a transparent, non-parametric *weekday-median* comparator is competitive with the existing last-observed, seasonal-naive and stockout-history methods.

**This comparator was chosen AFTER the v1.2 holdout results were inspected.** Consequently the same seven-day publisher evaluation is an **exploratory reuse of a seen holdout**, not a new untouched confirmatory test. Any favorable result needs a fresh temporal or dataset-level holdout before an improvement claim.

## Frozen algorithm for this exploratory comparison

- Source: [FreshRetailNet-50K publisher dataset](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K), original train/eval Parquet SHA-256 pins in [v1.2 protocol](OFFICIAL_HOLDOUT_V12_PROTOCOL.md). Original v1.2 evaluator blob: `ddd12a4e0695c474f752d98c99fd781931373bce`.
- **Cohort:** exactly the original 512 series chosen from TRAIN IDs alone, digest `7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710`; no replacement if eval rows are missing.
- **Prediction:** for each of the seven evaluation dates, median of the last **four fully in-stock training observations on the same weekday**. If none, median of fully in-stock observations from the **last 14 training days**. If none, predict zero and count the fallback. No evaluation sales or stock flags are inputs to prediction.
- **Target:** observed business-hour sales (06:00–21:59) only on evaluation days with **no stockout flags**. Censored evaluation days are excluded, exactly as v1.2. This does **not** recover latent demand.
- **Comparators:** original unchanged last-observed, seasonal-naive, and causal stockout-history forecasts. Recompute and assert the original v1.2 day-weighted MAEs and 2,183-day scoring denominator before accepting a real-data report.
- **Metrics:** day-weighted MAE; per-series macro MAE; paired per-series macro difference against last-observed and stockout-history; paired store-cluster bootstrap 95% intervals (2,000 replicates, seed 20261027). Store resampling is descriptive, not causal. Record all training-only fallback counts and zero-scored series.
- **Provenance:** Git commit/source blob, Python, pinned `pyarrow==20.0.0`, dataset hashes, cohort hash, run ID, artifact SHA-256. Raw publisher rows remain runner-local; aggregate JSON only is uploaded.

## Reproduce

From `benchmarks/retail-demand/observable_baseline/`:

```sh
python -B -m unittest -v test_official_holdout_v12 test_weekday_median_v14
python -m pip install pyarrow==20.0.0
python weekday_median_v14.py --train /local/pinned/train.parquet --eval /local/pinned/eval.parquet --output /tmp/weekday_v14_result.json
```

The executable [CI workflow](../../../.github/workflows/retail-weekday-v14.yml) is at repository root `.github/workflows/retail-weekday-v14.yml`; it fetches publisher files with a hash-gated fallback if the immutable revision URL is unavailable. It refuses to overwrite an existing output and fails closed on altered original source, cohort, dataset bytes or scoring denominator. Fictional tests include censored-history spikes, fallbacks, nonfinite values, missing days, duplicate cohorts, and bootstrap determinism.

## Results / learning / decision

| Item | Result |
|---|---|
| v1.4 + original v1.2 contract tests, code-bearing CI | **22/22 passed** (Ubuntu / Python 3.13.16); later documentation commits do not alter tested source |
| Publisher hash checks on v1.4 runner | **Both matched** original pinned train/eval SHA-256 after immutable URL 404 and hash-gated fallback |
| Weekday-median in-stock-day MAE | **0.463961979** vs last-observed **0.478562071** and correction **0.479905634** on unchanged 2,183 days / 512 series |
| Weekday-minus-last-observed series-macro delta; store-cluster 95% CI | **−0.015864; [−0.055629, +0.023005]** (crosses zero) |
| Weekday-minus-correction series-macro delta; store-cluster 95% CI | **−0.010895; [−0.026016, +0.004254]** (crosses zero) |
| Training-only forecast fallbacks | **3,572 same-weekday; 9 recent-14; 3 zero** across 3,584 forecasts |\n| Independent new holdout | TBD; this is post-hoc reuse of the original observed holdout |
| Latent demand / inventory / revenue uplift | **UNAVAILABLE / TBD** |

**Advance only if:** an independently reproduced, genuinely unseen evaluation shows stable improvement over strong simple baselines, with uncertainty and an actionable decision metric. **Reframe if:** the weekday-median or last-observed comparator remains as good or better; do not claim stockout correction is useful merely because it beats a weak baseline.

**Four lenses:** hiring manager—repeatable baseline comparison; technical reviewer—post-hoc holdout reuse and store dependence explicitly disclosed; innovation leader—negative evidence allowed to change the method; founder—no validated commercial uplift, users, product, patentability or deployment claim. No employer/private data or collaborator tracking.

## Hosted artifact verification and research decision

[GitHub Actions run #40397695520](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40397695520) passed at code-bearing commit `2baa7951378eba99729f7c3c2163389088e75bc6`. The log confirms 22 tests, both publisher checksum matches, frozen original MAEs, and completion of the v1.4 evaluator. The publisher's immutable revision URL returned HTTP 404 for both files; fallback to `main` was allowed **only after both original SHA-256 checks passed**. This is not a new independent data version.

The [hosted artifact ZIP](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40397695520/artifacts/12686718202) was independently downloaded and verified: ZIP SHA-256 `c7ffab79ec51f509ccb31a68dcf4824615377460a6b5a4d7659dfc2cef9c5375`; contained [result](WEEKDAY_MEDIAN_V14_RESULT.json) SHA-256 `c9aca32510f7ba9ada738e9dd5c0a79e7c55fdaf1b8bbdb253406084f56ca039` and [provenance](WEEKDAY_MEDIAN_V14_PROVENANCE.json) SHA-256 `3bb8ee14004928e8b7fd65c20dc1466a1792c0caf034ae0692e27919873ffafd`. Both committed JSON Git blobs were checked against the exact hosted artifact bytes. Hosted artifact retention is 14 days; committed aggregate records persist.

**Decision:** the transparent weekday-median baseline has a **3.05% lower point-estimate day-weighted MAE** than last-observed, but both paired store-cluster confidence intervals cross zero. Because this comparator was chosen after viewing the holdout, this is **exploratory evidence, not a confirmed improvement**. The complex stockout correction does not earn a superiority claim. **Next experiment:** preregister the unchanged weekday-median and original baselines on a genuinely unseen temporal or external evaluation split, with store/product dependence and decision metrics; do not tune against these observed seven days. No stage advancement, deployment, merge or release.
