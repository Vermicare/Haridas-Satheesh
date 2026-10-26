# Retail v1.3 — store-clustered uncertainty sensitivity (2026-10-27)

**Status:** executable post-hoc sensitivity protocol; hosted real-data result **TBD** until its workflow completes and both logs and aggregate artifact are independently inspected. **Maturity: Research / Architecture (unchanged).** This does not constitute a new held-out evaluation, latent-demand identification, commercial validation, or a new model.

## Motivation and evidence inherited, not overwritten

The [official 90+7 held-out v1.2 result](OFFICIAL_HOLDOUT_V12_RESULT.json) evaluated 512 deterministically TRAIN-selected store-product series, scoring 2,183 in-stock days and excluding 1,401 censored days. Day-weighted MAE was 0.478562 (last observed), 0.485180 (seasonal naive), and 0.479906 (stockout-history correction). The paired **series** bootstrap 95% interval for correction-minus-seasonal macro MAE was [-0.042840, +0.012164]; it crossed zero. The [second-runner reproduction](OFFICIAL_HOLDOUT_V12_REPRODUCTION_2026_10_26.md) matched those aggregates using the same frozen implementation.

The series-level resampling unit is questionable because products share stores. This experiment checks how uncertainty changes when whole **stores** are resampled. It was specified **after the original v1.2 scores were seen**, so it is a *post-hoc robustness check*, not preregistered confirmatory evidence.

## Frozen v1.3 analysis rule (before v1.3 output inspection)

1. **Data:** identical publisher train/eval Parquet bytes, required SHA-256 train `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d` and eval `1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e`. Mutable-branch download fallback is permitted **only** if both byte hashes match. Publisher origin remains not independently attested.
2. **Cohort:** identical original TRAIN-only 512-series selection, required digest `7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710`. No held-out replacement, refitting, tuning, changed model, changed date split, or new outcome label.
3. **Scoring:** call unchanged v1.2 `evaluate_cohort` on the complete cohort and again on each store's selected series. For stores with no uncensored evaluation day, report their count but do not manufacture a score. Require the recomposed series-weighted paired macro delta to match the original to absolute tolerance 1e-12; abort on mismatch.
4. **Uncertainty:** paired bootstrap of **stores**, resampling all scored product series within each store together. Preserve the original series-weighted mean delta estimand using scored-series counts as weights. Fixed seed `20261027`, 2,000 replicates, percentile 2.5%/97.5% interval. At least two distinct scored stores required.
5. **Decision:** interval crossing zero => no stable correction-vs-seasonal evidence. An interval excluding zero would be an exploratory sensitivity result, **not** an independent confirmatory discovery; correction still trails the strongest original day-weighted last-observed baseline. If store-level dependence changes the conclusion materially, prioritize broader clustered evaluation before model claims.
6. **Privacy/IP:** public output includes only cluster counts, aggregate paired delta, confidence interval, hashes, runtime provenance and explicit unknowns. Never publish publisher rows, individual store IDs, employer data or private outreach.

## Reproduction

```sh
python -m pip install pyarrow==20.0.0
cd benchmarks/retail-demand/observable_baseline
python -B -m unittest -v test_official_holdout_v12 test_cluster_sensitivity_v13
python -B cluster_sensitivity_v13.py --train /private/train.parquet --eval /private/eval.parquet --output /private/new_v13.json
```

The [hosted v1.3 workflow](../../../.github/workflows/retail-store-cluster-v13.yml) checks original source and result Git blobs before execution, verifies both dataset hashes, and uploads aggregate JSON and runtime/source provenance only. It does not run on a schedule. Preserve failed logs; no result is verified solely by committing code.

**Four lenses:** Hiring manager — an honest negative benchmark plus follow-up robustness check; technical reviewer — cluster bootstrap accounts for shared stores but not shared products, time dependence, dataset sampling bias or post-selection inference; innovation leader — determine whether complexity offers any stable gain over simple baselines; founder — inventory benefit, actual recovered demand, intervention outcomes, users and ROI remain **TBD**.

**Largest remaining gap:** independent model implementation, a stronger daily-count baseline, store/product dependence sensitivity, latent-demand labels and actionable inventory experiments. **Next evidence-producing step:** inspect hosted v1.3 logs/artifact, preserve actual clustered interval, then freeze a stronger simple daily-count baseline without using held-out results for tuning.
