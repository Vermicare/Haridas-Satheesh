# Retail Demand Intelligence — Reproducible Public-Data Benchmark

**Project stage:** Research / Architecture  
**Benchmark status:** Specification — results are **TBD**

## Evidence question

Does a stockout-aware, uncertainty-aware demand pipeline improve decision quality over simpler forecasting baselines on a public retail dataset, without using private retailer data?

The benchmark must separate **forecast quality** from **decision usefulness**. A more complex model does not advance the project merely because one forecasting metric improves.

## Dataset gate

Use a public dataset with time-indexed item/store demand and inventory/availability information when possible. Record:

- canonical source URL and license,
- exact dataset/version or retrieval date,
- selected category/items/stores,
- date range,
- exclusions,
- missing-data handling,
- whether stockouts are directly observed or only approximated.

If availability is not observable, label any inferred stockout treatment as a proxy and do not present it as ground truth.

## Leakage-safe evaluation

Use chronological rolling-origin backtests only. No random train/test split.

For each fold:

1. train using information available before the forecast origin,
2. create features without future information,
3. forecast the declared horizon,
4. apply the stockout treatment using only information that would have been available at that time,
5. rank opportunities,
6. evaluate against held-out observations.

All transformations that learn parameters must be fitted inside the training window.

## Baselines

1. **Seasonal naive** — primary minimum baseline.
2. **Simple statistical or tree/boosting model** — only if justified and reproducibly configured.
3. **Probabilistic forecast** — P10 / P50 / P90 or equivalent quantiles.
4. **Stockout-aware variant** — identical evaluation window with the censoring/correction mechanism isolated.
5. **Opportunity-ranking layer** — converts forecasts into ranked decisions without claiming realized commercial impact.

## Predeclared metrics

### Forecasting

| Metric | Definition | Result |
|---|---|---:|
| WAPE | sum absolute error / sum observed demand | TBD |
| MAE | mean absolute error | TBD |
| Pinball loss | quantile loss for declared forecast quantiles | TBD |
| Interval coverage | fraction of observations inside declared prediction interval | TBD |

### Stockout / censoring

| Metric | Definition | Result |
|---|---|---:|
| Observable-stockout subset error | forecast error restricted to directly observed stockout periods | TBD |
| Non-stockout subset error | forecast error where availability is observed | TBD |
| Correction uplift vs same model | metric delta caused by stockout treatment, not model-family change | TBD |

If stockouts are not directly observable, these remain **TBD / not measurable** rather than being estimated as fact.

### Decision layer

| Metric | Definition | Result |
|---|---|---:|
| Precision@K | fraction of top-K ranked opportunities satisfying the predeclared opportunity condition | TBD |
| Recall@K | fraction of qualifying opportunities captured in top K | TBD |
| Ranking lift vs baseline | improvement over ranking by the declared simple baseline | TBD |
| Intervention outcome | realized effect from an actual controlled intervention | TBD — unavailable in public retrospective benchmark |

The retrospective benchmark may test ranking quality. It must **not** claim revenue uplift or intervention causality.

## Reproducibility package

The executable package should contain:

- `data/README.md` with provenance and download instructions, but no redistributed dataset unless its license clearly permits it,
- pinned environment/dependencies,
- immutable experiment configuration,
- deterministic seed where applicable,
- data validation,
- chronological split generator,
- baseline implementation,
- probabilistic model,
- stockout treatment,
- evaluator,
- machine-readable results,
- benchmark table generated from results,
- failure/learning log,
- one command for a smoke test and one for the full benchmark.

## Minimum tests

- split dates are strictly chronological,
- no target/future-derived feature enters training,
- evaluation rows never occur before their training cutoff,
- quantiles are ordered or violations are explicitly measured,
- metric calculations pass fixed toy examples,
- stockout correction cannot access future availability,
- results table is generated from machine-readable output rather than hand-entered values.

## Advancement criterion

Remain **Research / Architecture** until a clean environment can reproduce the benchmark and the stockout/uncertainty-aware pipeline shows a useful, interpretable improvement over declared simple baselines on predeclared metrics.

A forecasting improvement alone does not establish business value.

## Kill / reframe criterion

Simplify or reframe the thesis if:

- added signals or stockout treatment do not beat simpler baselines consistently across rolling folds,
- gains depend on leakage or unstable proxy assumptions,
- probabilistic forecasts are poorly calibrated without useful ranking improvement,
- the decision layer cannot outperform a simple transparent ranking rule.

## Next implementation step

Choose and document one license-compatible public dataset, then implement the **seasonal-naive + chronological-split + evaluator** path before adding stockout correction or complex models.
