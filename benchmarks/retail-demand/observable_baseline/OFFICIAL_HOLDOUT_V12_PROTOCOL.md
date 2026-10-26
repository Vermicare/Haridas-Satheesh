# Retail v1.2 — official 90+7 publisher holdout, frozen 512-series comparison

**Frozen executable before score inspection:** `official_holdout_v12.py` and `test_official_holdout_v12.py` were committed before the one-time CI run. This is an **observational, in-stock-day sales forecast** comparison, not recovered latent demand, inventory optimization, independent publisher attestation, or evidence of causal impact. **Maturity: Research / Architecture.**

## Why this experiment

The first pinned **train-only** rolling benchmark ([2026-10-26 negative evidence](PINNED_TRAIN_EXECUTION_2026_10_26.md)) evaluated one series and only 10 uncensored days. Its causal stockout-history method had MAE 0.67 versus seasonal naive 0.56, worse by 19.6% at those operating conditions. That result is preserved; it is not superseded or generalized by this protocol.

The [publisher's pinned train Parquet](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/blob/08c1fab7f9257bc73679d415d65d644165d351d4/data/train.parquet) has reported SHA-256 `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d`; [pinned eval Parquet](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/blob/08c1fab7f9257bc73679d415d65d644165d351d4/data/eval.parquet) has reported SHA-256 `1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e`. Matching downloaded bytes checks local integrity against publisher-reported hashes, **not independent origin authentication**.

## Frozen decision contract

- **Calendar:** 90 training dates 2024-03-28 through 2024-06-25; seven held-out dates 2024-06-26 through 2024-07-02. Validate complete, duplicate-free daily coverage for every preselected series; **abort, do not replace** if any series is missing dates.
- **Cohort:** rank unique TRAIN-only `(store_id, product_id)` pairs by `SHA256("retail-official-holdout-v12-20261026|store|product")`, ascending; take the first **512**. No eval row or label can select the cohort. Preserve cohort SHA-256; never publish raw publisher rows.
- **Target:** observed sales summed for hours 06:00–21:59. Score **only eval dates with zero business-hour stockout flags**. Report every excluded censored day and series with no scorable day. This target cannot identify unobserved lost demand.
- **Baselines:** last observed daily business-hour sales; seven-day seasonal naive; causal same-weekday stockout-history correction. The correction uses only earlier uncensored training days; **all methods forecast from day 90 without reading eval sales or stock status**.
- **Primary descriptive metric:** day-weighted MAE across matched uncensored eval days, all methods evaluated on identical opportunities. **Secondary:** per-series macro MAE and paired (correction minus seasonal) macro MAE delta; 2,000 seeded (`20261026`) bootstrap resamples of store-product series, percentile 95% interval. Bootstrap is exploratory uncertainty, not a causal effect or a guarantee of independence across related series.
- **Decision:** negative delta favors correction; positive favors seasonal naive. Retain a negative result; do not tune on eval or assert significance/novelty/deployment from this single selected cohort. If the full predeclared cohort fails, preserve logs and diagnose without silently choosing a replacement.
- **Provenance:** Git commit, Python 3.13, pinned `pyarrow==20.0.0`, OS, both downloaded SHA-256s, selected cohort digest, run URL, source Git blobs, score JSON hash and any failures. **Unknown = TBD** until inspected.

## Reproduce and verify

The [GitHub Actions workflow](../../../.github/workflows/retail-official-holdout.yml) has no cron schedule, no write token and no access to employer or personal data. It downloads both publisher snapshots only into ephemeral runner storage, executes [the frozen evaluator](official_holdout_v12.py), and uploads **aggregate JSON only**. [Synthetic contract tests](test_official_holdout_v12.py) exercise chronology, cohort determinism, no eval-label access to forecasts, censoring, duplicate/gap rejection and seeded bootstrap.

Local reproduction with the pinned files:

```sh
python -m pip install pyarrow==20.0.0
cd benchmarks/retail-demand/observable_baseline
python -m unittest -v test_official_holdout_v12
python official_holdout_v12.py --train /private/train.parquet --eval /private/eval.parquet --output /private/new_result.json
```

**Result and external review:** TBD until the hosted run completes and both its log and aggregate artifact are inspected. The earlier single-series train-only negative result remains valid. No held-out score, improved forecasting, product candidate, employer result, release or maturity advancement is claimed here.

**Four lenses:** Hiring manager—inspect exact reproducibility and failure discipline; technical reviewer—challenge cohort sampling, censoring, aggregation and shared-store dependence; innovation leader—test whether extra correction complexity beats seasonal naive; founder—no evidence yet of demand recovery, revenue effect, customers or ROI.
