# Retail Demand Intelligence — observable-sales prebenchmark v0.1

**Stage:** Research / Architecture (unchanged). **First limited FreshRetailNet TRAIN-only real-data smoke completed 2026-10-26; official held-out, latent demand and intervention evidence: TBD.** This directory contains a tested, dependency-free evaluation harness and a separate fictional demo. The one-series public TRAIN-only smoke is **not** the publisher's official held-out benchmark or proof of latent-demand recovery.

## Latest verified public-data result — 2026-10-26

[GitHub Actions #40316866555](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40316866555) **succeeded** on pinned publisher TRAIN Parquet (4,500,000 rows, local SHA-256 verified against publisher-reported value). The frozen three-origin evaluation of one training-selected series scored only **10 in-stock days**: day-weighted seasonal-naive MAE **0.56**, causal stockout-history MAE **0.67** (**19.6% worse**). Eleven censored days were excluded. [Preserved evidence and limitations](PINNED_TRAIN_EXECUTION_2026_10_26.md) · [machine-readable record](PINNED_TRAIN_EXECUTION_2026_10_26.json). **No official 90+7 held-out evaluation, independent second execution, latent-demand ground truth, or commercial benefit is established.** Earlier dated acquisition-pending descriptions below are retained as historical research notes and superseded by this result.

## Why this experiment

[Retail Issue #2](https://github.com/Vermicare/Haridas-Satheesh/issues/2) requires a chronological, leakage-safe comparison before forecasting complexity or business value can be claimed. The first step isolates a deliberately modest question: **Does a causal training-history stockout heuristic beat seasonal naive on observed sales when the held-out item is in stock?**

Official upstream sources: [FreshRetailNet-50K v1.0 dataset card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K) (Dingdong-Inc; CC BY 4.0 as declared by publisher), [paper](https://arxiv.org/abs/2505.16319), and [authors' baseline](https://github.com/Dingdong-Inc/frn-50k-baseline). The official dataset viewer exposes `hours_sale`, `hours_stock_status`, and `stock_hour6_22_cnt`. The tool checks 16 business-hour status flags, indices 6–21 inclusive. This is a **schema assumption to verify on a pinned snapshot**, not evidence that the dataset was downloaded here.

## Reproduce (Python 3.9+, standard library)

From this directory:

```bash
python -m unittest discover -v
python demo_60s.py
```

The demo generates its own **fictional** 84-day store/product sequence, runs three frozen rolling-origin folds, and labels all scores fictional. The same source and tests were locally executed on CPython 3.13.5/Linux on 2026-10-24: **22/22 tests passed**. CI results must be verified separately for each revision.

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

## Disk-backed evaluator — additional v0.2 research candidate (2026-10-24)

The original in-memory JSONL reader materializes every row; the official train split has 4.5 million rows. For a large **verified** export, use the dependency-free, disk-backed `retail_sqlite.py` with the same flags and frozen forecast/metric functions:

```bash
python -m unittest discover -v
python retail_sqlite.py --input verified_export.jsonl \
  --source-sha256 <LOCAL_EXPORT_SHA256> \
  --source-uri https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K \
  --output measured_result.json
```

It ingests validated JSONL rows into temporary SQLite storage with a uniqueness constraint, selects the first eligible cohort using **only the first 42 training days**, and rejects missing future horizons without replacement selection. The database is removed after execution. A shuffled fictional 77,000-row/1,000-series fixture and six other adversarial tests matched the original in-memory report; both engines **share the frozen evaluator** and are not independent forecasting models. Python application memory scales with the number of distinct series keys plus the selected series, rather than all daily rows; temporary disk and SQLite cache are required. Real 4.5-million-row resource measurements: **TBD**.

**Publisher metadata only, not downloaded-byte verification:** The [pinned official train.parquet file](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/blob/08c1fab7f9257bc73679d415d65d644165d351d4/data/train.parquet) reports revision `08c1fab7f9257bc73679d415d65d644165d351d4`, 106 MB and SHA-256 `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d`. The source parquet bytes, exact parquet-to-JSONL exporter, local source/export hashes, dependency versions, and actual public-data results remain **TBD**. A claimed source URI or locally supplied hash does not authenticate origin.

This work removes a foreseeable memory-scaling obstacle but **does not** establish forecast improvement, latent-demand recovery, commercial value, or a higher maturity gate. Preserve positive or negative outcomes after real-data acquisition.

**Cross-platform failure retained:** The first v0.2 CI run (GitHub Actions #40021172407) passed Linux but failed seven Windows tests with `WinError 32` during temporary SQLite database deletion. Root cause: `sqlite3.Connection` as a context manager commits/rolls back but does **not** close the file handle. The candidate now explicitly closes the connection with `contextlib.closing` before deleting the temporary directory. The first connection-close fix was insufficient; see the second Windows failure below.

**Second Windows failure retained:** GitHub Actions #40021290007 passed Linux but failed one Windows negative-path test after the connection-close fix. The outer SQLite selection cursor was still active when the intentional missing-horizon exception occurred, locking the temporary file. The revised candidate explicitly closes the cursor before evaluation; the subsequent GitHub Actions run #40021463498 passed all 29 tests on Linux and Windows (Python 3.13), with the fictional demonstration also passing on both.


## 2026-10-25 — finite-score integrity v0.9

A new [four-test fictional regression suite](test_finite_score_integrity_v09.py) reproduced an evidence defect: **finite** hourly sales and individual errors could overflow intermediate MAE sums or the causal same-weekday median to `Infinity`; Python's default JSON serializer would then emit invalid nonstandard JSON. The [before-fix CI #40213211784](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40213211784) recorded two failing assertions and two engine subtest errors on Ubuntu (Windows cancelled after correction). The corrected evaluator preserves the ordinary-score path, uses overflow-safe fallbacks, and makes both CLIs serialize strictly. [Code-bearing CI #40213275082](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40213275082) passed **67/67 tests on Ubuntu and Windows**, including the fictional demo. See [full v0.9 evidence, limitations and provenance](FINITE_SCORE_INTEGRITY_V09.md) and [registry](EXPERIMENT_REGISTRY.json). **No publisher Parquet was processed, no real-data performance was measured, and maturity remains Research / Architecture.**
