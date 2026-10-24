# FreshRetailNet-50K pinned-parquet export preflight — research candidate v0.3

**Status (2026-10-24):** The *fictional-row conversion core* passed 11/11 standard-library tests locally. **No official Parquet file was downloaded or read.** `pyarrow` was unavailable in the local test environment, so actual Parquet I/O and any forecasting scores remain **TBD**. This is a preparation artifact, not an executed public-data benchmark.

## Decision addressed

The v0.2 SQLite evaluator consumes validated daily JSONL, while the publisher provides Parquet. This exporter bridges the format gap with a bounded-memory row-batch conversion, strict schema checks, immutable-revision declaration, local source/export hashes, deterministic UTF-8 JSONL serialization, exclusive non-overwrite publication and fail-closed cleanup. It does not alter the frozen forecasting/metric logic.

## Official dataset and independently unverified metadata

Publisher: [Dingdong-Inc/FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K), declared CC BY 4.0. Publisher-reported immutable revision: `08c1fab7f9257bc73679d415d65d644165d351d4`; publisher-reported train Parquet SHA-256: `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d` (106 MB). **These values have not been checked against local Parquet bytes.** Upstream paper: [arXiv:2505.16319](https://arxiv.org/abs/2505.16319).

## Reproduce synthetic contract checks

From this directory, run `python -m unittest discover -v -p 'test_parquet_export.py'`. No dependencies beyond Python 3.9+ are required for the 11 fictional tests. The source bytes used by those tests are explicitly *not* a Parquet file. Two independent clean-directory runs and the source/test SHA-256 should be recorded before promotion.

## Run on real publisher data — NOT YET EXECUTED

Install a pinned `pyarrow` version and record it in the environment manifest. Obtain the publisher's train Parquet from the immutable revision; verify the file hash locally. In this directory:

```bash
python parquet_export.py \
  --parquet /path/to/official/train.parquet \
  --expected-sha256 6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d \
  --revision 08c1fab7f9257bc73679d415d65d644165d351d4 \
  --output /path/to/verified_export.jsonl \
  --manifest /path/to/verified_export.manifest.json
python retail_sqlite.py --input /path/to/verified_export.jsonl \
  --source-sha256 <EXPORT_SHA256_FROM_MANIFEST> \
  --source-uri https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K \
  --output /path/to/real_result.json
```

Preserve exact `pyarrow` version, Python/OS versions, official file hash, export hash, source revision, command lines, elapsed time and memory/disk peak as **TBD until observed**. The converter writes only the six evaluator-required fields, not the entire upstream schema. It requires 24-element hourly arrays, binary stock flags and an exact count over indices 6–21. It rejects source mutations during export. The existing evaluator checks duplicates and chronological completeness separately.

## Evidence limits / kill conditions

A locally matching SHA-256 does not independently authenticate the claimed publisher origin. Do not label the exporter as real-data validated until pinned Parquet bytes are actually acquired and processed, schema compatibility is checked, and the output is independently reproduced. Reframe the pipeline if the official schema differs, the pinned hash cannot be reproduced, or the selected cohort has incomplete held-out data. Even a successful export does **not** demonstrate forecasting uplift, latent-demand recovery, causal intervention, deployment or commercial value. Keep retail at **Research / Architecture**.

## 2026-10-24 — exclusive publication negative control

A deterministic fictional-row test exposed a time-of-check/time-of-use (TOCTOU) defect: another writer could create the output or manifest **after** the initial `exists()` check; `os.replace()` then silently overwrote the unrelated file. The corrected exporter uses an atomic same-filesystem hard-link publication (`os.link`), which refuses to replace a destination created during conversion. Two adversarial tests create output/manifest sentinel files mid-stream and require preservation; existing deterministic-output tests must still pass. The manifest is published last as the completion marker and consumers must check its declared hashes. This is **not** a two-file atomic transaction: a process crash between publications can leave an orphan output requiring manual review. No real Parquet I/O or forecasting validation was performed.
