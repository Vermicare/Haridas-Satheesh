# Retail v1.3 — verified store-cluster sensitivity execution (2026-10-27 IST)

**Result:** [GitHub Actions #40380214505](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40380214505) **SUCCESS**, code-bearing commit `b85ccb302bf894740e980e36afd66143e4737bfb`. One Ubuntu job log was inspected, including tests, publisher hash checks, actual evaluator stdout and uploaded artifact confirmation. This is a **post-hoc uncertainty sensitivity** on the **same** 512-series official held-out cohort; not a new test set, independent implementation, latent-demand result or evidence of commercial impact.

## Reproduced evidence and new measurement

| Check | Verified outcome |
|---|---|
| Original frozen v1.2 source Git blob | `ddd12a4e0695c474f752d98c99fd781931373bce` matched |
| New v1.3 source Git blob | `dd929b6600fa0504855c4dc7aba3f67b8ab793ff` matched artifact provenance |
| Tests | **17/17 PASS** (10 original holdout + 7 new fictional/negative controls) |
| Publisher train Parquet SHA-256 | `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d` — MATCH |
| Publisher eval Parquet SHA-256 | `1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e` — MATCH |
| Immutable revision retrieval | HTTP 404 for both; publisher `main` fallback accepted **only** because both original hashes matched |
| Frozen cohort digest | `7c14c678af51878ac68a3359e3dae0be1208feba4b0fa30d437191e855f62710` — MATCH |
| Unchanged v1.2 scored days | **2,183** |
| Scored product series / distinct store clusters | **512 / 374** |
| Original series-macro paired correction-minus-seasonal MAE delta | **−0.014454543340773807** — EXACT MATCH after store recomposition |
| Original series-bootstrap 95% interval | **[−0.04284015, +0.01216397]** |
| **New paired store-cluster bootstrap 95% interval** | **[−0.04281792, +0.01346010]** |
| Bootstrap | 2,000 resamples, seed `20261027`, resampling entire stores |
| Result / model maturity | **No superiority established / Research–Architecture unchanged** |

Both intervals cross zero. The store-clustered interval is slightly wider; allowing within-store dependence **does not rescue the correction method**. The strongest original day-weighted comparator remains last observed (MAE 0.478562 versus correction 0.479906). The store bootstrap changes the resampling unit, **not** the underlying forecasts or held-out labels.

## Artifact verification and reproducibility

- [Frozen post-hoc analysis contract](STORE_CLUSTER_SENSITIVITY_V13.md) was published before inspecting v1.3 output.
- [Executable cluster analysis](cluster_sensitivity_v13.py), [seven negative controls](test_cluster_sensitivity_v13.py), [read-only workflow](../../../.github/workflows/retail-store-cluster-v13.yml) and [byte-identical aggregate JSON](STORE_CLUSTER_SENSITIVITY_V13_RESULT.json) are committed on **draft PR #9**, not merged.
- GitHub Actions artifact ID **12678251639**, retention until **2026-11-09 18:43:38 UTC**. The ZIP was independently downloaded and inspected. ZIP SHA-256 `e356acaa7fdf90f80557d964fbab4381660dac6aab3ccc82b4c5cfbef327f3a9`; it contained **only** `cluster_sensitivity_v13_provenance.json` and `cluster_sensitivity_v13_result.json`.
- Result JSON SHA-256 `661f0a317b77fdb47e4395a2788482c22e98a03c51ce3523945883321fc999c2`; the provenance JSON records the same result hash. The public committed result has the **exact artifact Git blob** `5e9e003faa4c841f1ff87e3f0e2fd68ba9b7d0e9`.
- Runtime: GitHub-hosted Ubuntu Linux 6.17.0-1022-azure, Python 3.13.16, pinned `pyarrow==20.0.0`; no private data, employer data, store-level output or outreach tracking published.

## Decision and next evidence gate

**Decision:** keep the negative/mixed finding. A paired interval that crosses zero is not evidence of superiority. The store-level bootstrap is a sensitivity check **performed after seeing v1.2 results**, not a confirmatory replication. Shared products across stores, time dependence, selection effects, and stockout-censored latent demand remain unresolved. Publisher-reported hashes confirm downloaded byte identity but do not independently authenticate publisher origin.

**Strongest evidence:** two hosted executions of frozen v1.2 and one additional v1.3 store-clustered sensitivity run, all with verified source/data hashes and preserved aggregate artifacts. **Largest gap:** stronger simple daily-count baseline and independent implementation, followed by decision-relevant interventions and lost-demand labels. **Next experiment:** freeze a training-only daily-count baseline and a store/product-dependence sensitivity before another held-out comparison; no evaluation-driven tuning.

**Four lenses:** Hiring manager — reproducible negative evidence; technical reviewer — cluster-level uncertainty still not independent external review; innovation leader — no demonstrated incremental gain from correction; founder — ROI, inventory decisions, users and deployments **TBD**. No merge, release, maturity advance, outreach or patentability claim.
