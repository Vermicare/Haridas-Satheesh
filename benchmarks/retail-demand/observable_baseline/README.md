# Retail Demand Intelligence — observable-sales prebenchmark v0.1

**Stage:** Research / Architecture (unchanged). **Real FreshRetailNet measurements: TBD.** This directory contains a tested, dependency-free evaluation harness and an entirely fictional demo. It is **not** a completed public-data benchmark or proof of latent-demand recovery.

## Why this experiment

[Retail Issue #2](https://github.com/Vermicare/Haridas-Satheesh/issues/2) requires a chronological, leakage-safe comparison before forecasting complexity or business value can be claimed. The first step isolates a deliberately modest question: **Does a causal training-history stockout heuristic beat seasonal naive on observed sales when the held-out item is in stock?**

Official upstream sources: [FreshRetailNet-50K v1.0 dataset card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K) (Dingdong-Inc; CC BY 4.0 as declared by publisher), [paper](https://arxiv.org/abs/2505.16319), and [authors' baseline](https://github.com/Dingdong-Inc/frn-50k-baseline). The official dataset viewer exposes `hours_sale`, `hours_stock_status`, and `stock_hour6_22_cnt`. The tool checks 16 business-hour status flags, indices 6–21 inclusive. This is a **schema assumption to verify on a pinned snapshot**, not evidence that the dataset was downloaded here.

## Reproduce (Python 3.9+, standard library)

From this directory:

```bash
python -m unittest discover -v
python demo_60s.py
```

The demo generates its own **fictional** 84-day store/product sequence, runs three frozen rolling-origin folds, and labels all scores fictional. The same source and tests were locally executed on CPython 3.13.5/Linux on 2026-10-24: **22/22 tests passed**. CI is proposed; its outcome must be verified separately.

## Frozen protocol

- Parse daily JSONL records with `store_id`, `product_id`, ISO `dt`, 24 `hours_sale` values, 24 binary `hours_stock_status` flags, and `stock_hour6_22_cnt`.
- Require the stockout count to equal `sum(hours_stock_status[6:22])`; reject missing/invalid/duplicate rows.
- Select the lexicographically first series having **42 consecutive training days** and both stocked/stockout days *using training data only*. If its later horizon is incomplete, **fail**, rather than cherry-pick a replacement using future completeness.
- Forecast seven days at fixed offsets **42, 56, 70**. Compare last-observed, seven-day seasonal naive, and same-weekday uncensored-history substitution (maximum four prior eligible values).
- Score **MAE of observed 06:00–21:59 sales only on held-out days with zero stockout flags**. Exclude stockout days because their latent demand is unobserved; record the number excluded per fold.
- No future labels, future stock status, post-origin features, parameter search, or observed-censored-sales-as-latent-truth scoring.

## Real-data gate (not executed)

Acquire the **official train parquet** from the publisher, record the immutable dataset revision, license, original parquet SHA-256, exact export command and JSONL SHA-256. Export **all required columns without changing values**. Run:

```bash
python retail_gate.py --input verified_export.jsonl \
  --source-sha256 <SHA256_OF_EXPORT> \
  --source-uri https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K \
  --output measured_result.json
```

The tool verifies the **local file hash only**, not the authenticity of a claimed source URI or the upstream snapshot. No data or private employer material is committed here. The external data host was not reachable from the local execution environment on 2026-10-24; upstream snapshot hash, conversion and actual public-data results remain **TBD**.

## Failure / learning / decision

A discarded initial selection strategy checked future completeness *before* choosing a cohort, which risks selection leakage. This implementation selects on training history and fails on missing future coverage; regression tests exercise that failure. The fictional demo's seasonal-naive and corrected-history models tie on eligible days; it is **not** evidence of an uplift.

The observable in-stock-day evaluation conditions on availability and cannot identify latent stockout demand, forecast interval calibration, opportunity ranking, revenue uplift, causal interventions or commercial value. Those are **TBD**. Next: pinned official-data snapshot, deterministic export, clean reproducible fold execution, then multi-series and decision-layer evaluation. **Reframe** if correction consistently fails to outperform transparent baselines; do not advance maturity or release a product from this test harness.

Four-lens review: **Hiring manager**—runnable evidence discipline; **technical reviewer**—schema and temporal leakage tests; **innovation leader**—clear falsifiable hypothesis; **founder**—no revenue or product claims.
