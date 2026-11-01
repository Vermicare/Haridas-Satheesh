# Retail Demand Intelligence — observable-sales prebenchmark v0.1

**Stage:** Research / Architecture (unchanged). **FreshRetailNet TRAIN-only smoke and official 90+7 held-out 512-series comparison completed 2026-10-26; second clean hosted run matched all 13 aggregate/cohort checks. Latent demand and intervention evidence remain TBD.** This directory contains a tested, dependency-free evaluation harness and a separate fictional demo. The one-series public TRAIN-only smoke is **not** the publisher's official held-out benchmark or proof of latent-demand recovery.

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

## v1.2 — first official 90+7 held-out publisher execution (2026-10-26)

[GitHub Actions #40342565683](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40342565683) **passed** on the frozen code-bearing commit with both publisher Parquet SHA-256s verified, **10/10** fictional contract tests passed, and **512 TRAIN-selected series** evaluated against the official seven-day holdout. On **2,183 in-stock eval days** (1,401 censored days excluded), day-weighted MAE was **last-observed 0.478562**, **seasonal naive 0.485180**, **causal stockout-history 0.479906**. Correction was **1.09% better than seasonal naive** but **0.28% worse than last observed**. Series-level paired bootstrap macro-delta 95% interval **[−0.042840, +0.012164] crosses zero**. This is mixed/uncertain observational evidence, **not proven correction superiority, latent demand recovery or revenue uplift**.

[Predeclared protocol](OFFICIAL_HOLDOUT_V12_PROTOCOL.md) · [Verified execution and limitations](OFFICIAL_HOLDOUT_V12_EXECUTION_2026_10_26.md) · [Permanent aggregate registry](OFFICIAL_HOLDOUT_V12_RESULT.json) · [Executable evaluator](official_holdout_v12.py). The earlier train-only one-series negative result remains preserved and is not directly comparable. Stage remains **Research / Architecture**; no merge/release/deployment. Next: independent rerun, store-clustered uncertainty and stronger daily baseline on the same cohort.

**Reproducibility update (2026-10-26):** [Second hosted runner #40362197198](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40362197198) reproduced the unmodified v1.2 aggregate results and cohort (13/13 checks). The first attempt [#40362031480](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40362031480) failed on publisher pinned-revision HTTP 404; the successful rerun used publisher `main` bytes **only after matching both original pinned SHA-256s**. See [failure, provenance and replication boundaries](OFFICIAL_HOLDOUT_V12_REPRODUCTION_2026_10_26.md). This is not an independent model implementation or a claim of stockout correction superiority.


## v1.3 — post-hoc store-cluster uncertainty sensitivity (2026-10-27)

[GitHub Actions #40380214505](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40380214505) **passed** with 17/17 tests and matching original publisher train/eval SHA-256s. On the **unchanged 512-series official held-out cohort**, 374 distinct stores were scored. The paired store-cluster bootstrap 95% interval for correction-minus-seasonal series-macro MAE was **[−0.042818, +0.013460]**, still crossing zero; the original series-bootstrap interval was [−0.042840, +0.012164]. This post-hoc robustness check does **not** establish superiority, latent demand, inventory impact, independent model validation or product maturity. The original day-weighted last-observed baseline still beats correction.

[Executable v1.3](cluster_sensitivity_v13.py) · [Seven fictional/negative-control tests](test_cluster_sensitivity_v13.py) · [Post-hoc protocol](STORE_CLUSTER_SENSITIVITY_V13.md) · [Verified execution and artifact integrity](STORE_CLUSTER_SENSITIVITY_V13_EXECUTION_2026_10_27.md) · [Byte-identical aggregate result](STORE_CLUSTER_SENSITIVITY_V13_RESULT.json). **Stage remains Research / Architecture; draft PR #9 unmerged.** Next: freeze a stronger daily-count comparator and broader dependence sensitivity; do not tune on this held-out result.

## v1.4 — stronger post-hoc weekday-median comparator (2026-10-27, stacked research)

[GitHub Actions #40397695520](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40397695520) **passed 22/22 tests** and matched both original publisher Parquet SHA-256s, the unchanged 512-series cohort, and the original v1.2 scores. On the same 2,183 in-stock held-out days, a fixed training-only last-four-uncensored-same-weekday median achieved **0.463962 day-weighted MAE**, compared with last-observed **0.478562** and stockout correction **0.479906**. Its paired store-cluster 95% intervals against both methods **cross zero**; this baseline was selected **after seeing the original holdout**, so the result is exploratory, **not a new independent confirmatory test or demonstrated superiority**.

[Executable comparator](weekday_median_v14.py) · [12 adversarial tests](test_weekday_median_v14.py) · [protocol and decision](WEEKDAY_MEDIAN_V14_PROTOCOL.md) · [verified aggregate](WEEKDAY_MEDIAN_V14_RESULT.json) · [provenance](WEEKDAY_MEDIAN_V14_PROVENANCE.json). **Stage unchanged.** Next: truly unseen chronological/external split with the methods frozen in advance, store/product dependence, and decision-value evaluation. No latent-demand or commercial claims.


## v1.5 — preregistered unseen-store series transfer on same dates (stacked draft PR #19)

[Protocol](STORE_DISJOINT_V15_PROTOCOL.md) · [executable](store_disjoint_v15.py) · [fictional selection/decision tests](test_store_disjoint_v15.py) · [publisher-pinned CI](../../../.github/workflows/retail-store-disjoint-v15.yml).

This experiment selects 512 TRAIN-only series from **stores completely absent** from the original 512-series cohort and applies the unchanged v1.2 and v1.4 forecasters. The primary gate requires a lower weekday-median day-weighted MAE **and** a paired store-cluster 95% interval entirely below zero versus last-observed. **Results: TBD until verified.** It uses the **same publisher evaluation dates** already inspected for other stores, so it cannot independently confirm temporal generalization. A genuinely new chronological/external holdout and decision-value test remain required. Stage unchanged; no raw dataset is committed.


**v1.5 verified outcome:** [GitHub Actions #40445663158](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40445663158) passed **33/33 tests** and both publisher hashes. The 512-series new cohort covered **293 stores with zero overlap** and 2,092 in-stock evaluation days. MAE: stockout correction **0.499880**, seasonal naive **0.514213**, weekday median **0.516406**, last observed **0.536860**. The **predeclared weekday-vs-last-observed primary gate failed** because the paired store-cluster interval **[−0.063019, +0.033285]** crosses zero. A secondary weekday-minus-correction interval **[+0.000875, +0.043310]** suggests store heterogeneity, not general or temporal superiority. [Detailed execution and exact artifact integrity](STORE_DISJOINT_V15_PROTOCOL.md) · [aggregate](STORE_DISJOINT_V15_RESULT.json) · [provenance](STORE_DISJOINT_V15_PROVENANCE.json). No stage change; next is a genuinely unseen time period or external dataset.
