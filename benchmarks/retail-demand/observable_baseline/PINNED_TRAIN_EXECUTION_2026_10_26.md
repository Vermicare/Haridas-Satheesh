# First publisher-pinned TRAIN-only retail benchmark — 2026-10-26

**Evidence class:** real publisher-snapshot bytes, **training-only** rolling-origin evaluation on one selected store/product series. **Not** the publisher's official 90+7-day held-out evaluation; **not** a latent-demand or revenue experiment. Stage remains **Research / Architecture**.

## Source and execution

- [GitHub Actions #40316866555](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40316866555), job `publisher-train-smoke`: **success**, verified from job steps and full job log.
- Executed branch commit `7edb99902763a35dca2a23c6b0a094f233d51eb5`, Ubuntu 24.04, Python 3.13.16, PyArrow 20.0.0; completion 2026-10-26 11:44:25 UTC.
- [FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K) publisher-reported revision `08c1fab7f9257bc73679d415d65d644165d351d4`. Downloaded TRAIN Parquet SHA-256 was checked against the publisher-reported `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d`. Independent publisher-origin attestation: **no**.
- 4,500,000 publisher TRAIN rows exported to ephemeral JSONL; export SHA-256 `7974c0b2ad08a11b80c3d08ebf47d9e3189cf1f11b6ba20c994b1d42a5e074ce`. No raw publisher rows were committed or uploaded as an artifact.
- [Artifact `retail-pinned-train-only-evidence`](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40316866555) ID `12647720891`, ZIP SHA-256 `e607bf9971988f03e64f039bfc28d6aa470b2aea326846a5feb9afa607ec0f84`, retention until 2026-11-09 11:44:25 UTC. Three JSON members: `rolling_origin_result.json` SHA-256 `a14e030b1292224627f7c99b0f3506ea7201dcab529f7f26c43dae27506b5fc6`, `export_manifest.json` SHA-256 `38d4d98114ae400051eda9cf7806f656f4f37d0219db2e96ede7a57ce7d78ffa`, `run_evidence.json` SHA-256 `9476bd92de351e7a31e4548b6ce08f49eca0f41131c9d98544afd085e02733ba`.
- [Machine-readable evidence summary](PINNED_TRAIN_EXECUTION_2026_10_26.json) preserves the selected cohort, fold scores, hashes, limitations, and negative decision after artifact expiry. Original artifact JSON remains the exact score source.

## Frozen evaluation and observed negative result

The code selected the lexicographically first eligible series using only the first 42 TRAIN days: store `0`, product `104`. It scored seven-day windows at training offsets 42, 56 and 70. Metric: MAE of observed 06:00–21:59 sales **only on fully in-stock held-out days**. Eleven censored days were excluded; only **10** in-stock days were scored across all folds.

| Test origin | In-stock days | Excluded censored days | Last observed MAE | Seasonal naive MAE | Causal stockout-history MAE |
|---|---:|---:|---:|---:|---:|
| 2024-05-09 | 2 | 5 | 1.5500 | 0.8000 | 0.7500 |
| 2024-05-23 | 6 | 1 | 0.5833 | 0.4833 | 0.4583 |
| 2024-06-06 | 2 | 5 | 0.8500 | 0.5500 | 1.2250 |
| **Day-weighted aggregate (10 in-stock days)** | **10** | **11** | **0.8300** | **0.5600** | **0.6700** |

The correction method is **worse than seasonal naive on this selected cohort**: MAE `0.67` versus `0.56`, or **19.6% higher error**. It improves on seasonal naive in the first two tiny folds but loses substantially in the third. This is a **negative/unstable baseline comparison**, not a claim that stockout-aware methods generally fail. The three folds are not an independent statistical sample, and the tiny denominator prevents generalization.

## Decision, advancement gate, and next experiment

**Decision: retain negative result; do not advance maturity, merge as validated model, or claim commercial/forecast uplift.** The exact-hour status question remains open. Before adding complexity, run a preregistered, multi-series comparison with a frozen cohort selection rule, chronological train/calibration/official held-out split, matched denominators, missingness and uncertainty analysis, and both seasonal-naive and daily-stockout-count baselines. Score official held-out observations separately from any latent-demand assumptions. Preserve unfavorable results and document any excluded series. Reframe if the corrected method consistently fails to beat transparent baselines on matched eligible days.

**Not established:** public-dataset identity beyond the locally matched publisher hash; official held-out 90/7 accuracy; latent-demand truth; stockout intervention value; confidence intervals; independent second-run reproducibility; novel method; commercial performance. These remain **TBD**.

Four-lens review: hiring manager—first real public-data execution with honest negative result; technical reviewer—frozen one-series test is underpowered and requires independent reproduction; innovation leader—prior-art-aware comparison is falsifiable; founder—no decision or revenue uplift evidence.

No employer information, customer records, private outreach log, or raw publisher dataset is included.
