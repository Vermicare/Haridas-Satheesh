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


## 2026-10-24 — downstream checksum-to-ingestion provenance negative control (v0.4)

**Reproduced failure:** The in-memory `retail_gate.py` and disk-backed `retail_sqlite.py` each hashed a JSONL input *before* ingestion but did not verify that the bytes stayed unchanged while reading. Two fictional-only adversarial tests altered one held-out observed-sales value after the first checksum and before ingestion. Both original evaluators accepted the changed data while retaining the **old** input hash (2/2 expected-rejection tests failed before the fix). This is an evidence-attribution failure, **not** a measured forecasting effect.

**Correction:** Both evaluators now rehash the source after ingestion/cohort selection and fail closed with `EvidenceError` when the bytes differ. The frozen forecasting and scoring functions are unchanged. In two local CPython 3.13.5/Linux runs against the archived harness, **44/44 tests passed**. The newly published test and in-memory source have matching local and GitHub blob identities; the SQLite change was verified in the GitHub branch and cross-platform CI.

**Independent CI:** [GitHub Actions run #40074990302](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40074990302) passed **44/44 tests on Ubuntu and Windows (Python 3.13)**; both jobs executed the fictional demo. Published source/test Git blobs: in-memory `c9c834d9a77c1e1c6a4ee82b3dbec5031ed9ab42`, SQLite `1dcf72818a40bceb1f9d98ef5719e113912b9429`, mutation tests `c145bcdb69e2296c88dd0663e872fb86dbc252d4`. Reproduce with `python -m unittest discover -v` from this directory.

**Limits:** A pre/post hash comparison does not independently authenticate publisher origin, prevent a malicious actor from restoring identical bytes between checks, or prove any real Parquet conversion or forecast uplift. Publisher-pinned data acquisition, locally verified Parquet SHA-256, measured resource use and actual-data scores remain **TBD**. Maturity remains **Research / Architecture**; no merge or release is justified by this synthetic integrity gate.

## 2026-10-24 — external publisher-pin declaration negative control (v0.5)

**Before-fix failure reproduced in GitHub CI:** The exporter accepted an arbitrary 40-character Git revision and an arbitrary matching local source hash while still declaring the official FreshRetailNet publisher source. Two new **fictional-only** negative controls failed as expected on Ubuntu/Python 3.13 ([CI #40108245246](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40108245246): 45/47 passed, 2 expected-rejection failures). The synthetic injection control passed. The Windows job was cancelled after the corrective commit, so the before-fix evidence is Linux-only.

**Correction:** Non-synthetic exports now require *both* the exact publisher-pinned revision `08c1fab7f9257bc73679d415d65d644165d351d4` and the publisher-reported train SHA-256 `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d`, in addition to checking the actual local file bytes against that hash. Fictional tests can inject alternate revisions/hashes only with `synthetic=True`, and their manifests explicitly say `FICTIONAL_TEST_ONLY`. Forecasting logic is unchanged.

**Evidence boundary:** This closes an incorrect **source declaration** acceptance path, not publisher-origin authentication. A caller can still provide mismatched in-memory batches directly to `export_batches`; only the documented CLI binds Parquet reading to the specified file. The official Parquet has not been acquired here, `pyarrow` integration is untested, and all actual-data forecasting/decision metrics remain **TBD**. Do not advance maturity or merge solely on these tests.

## 2026-10-25 — canonical ingestion schema negative control (v0.6)

**Before-fix failure, independently observed in CI:** The downstream `retail_gate.parse_row` converted `store_id` and `product_id` to strings and parsed only the first ten characters of `dt`. It therefore silently accepted fictional records with string, boolean, negative, or floating-point identifiers and dates containing timestamps or arbitrary suffixes. This contradicted the strict exporter contract and could collapse distinct source identities or disguise noncanonical dates. The 8 new regression tests produced **8 failing assertions/subtests in a 55-test Ubuntu run** before correction (GitHub Actions [#40139601095](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40139601095)); Windows was cancelled by the corrective commit. The one valid-row control passed.

**Correction:** In-memory and SQLite benchmarks share the same `parse_row`. It now requires nonnegative integer IDs (excluding booleans), a strictly canonical `YYYY-MM-DD` date without suffix, and rejects malformed dates before cohort selection. The frozen forecasting and scoring algorithms are unchanged.

**Verified after correction:** [GitHub Actions #40139612476](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40139612476) passed **55/55 tests on Ubuntu and Windows (Python 3.13)**, including all 8 new fictional controls and the 1,000-series cross-engine comparison. Changed source: `retail_gate.py`; new controls: `test_strict_ingest_schema.py`. An isolated local prototype also passed one valid and seven adversarial cases; it is not a substitute for the GitHub CI evidence.

**Limitations:** All newly tested rows are fictional; the publisher Parquet has **not** been acquired or parsed here, and no forecasting uplift, stockout-demand recovery, intervention value, or real-data compatibility is established. Stage remains **Research / Architecture**. Next: acquire the pinned official train Parquet, verify publisher-reported SHA-256 against downloaded bytes, export via the documented CLI, and independently reproduce the frozen benchmark. If actual upstream IDs or dates violate this contract, record the mismatch and revise the mapping explicitly rather than silently coercing.


## 2026-10-25 — finite observed-sales evidence gate (v0.7)

**Reproduced failure (fictional only):** the previous exporter accepted 16 individually finite `1e308` hourly sales values whose business-hour sum overflowed to `Infinity`. Both JSONL and SQLite evaluators accepted the same record and returned a report instead of rejecting it. A `10**400` integer hourly sale triggered an uncaught `OverflowError` in downstream validation rather than a controlled `EvidenceError`. The [before-fix Ubuntu CI](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40159020949) ran 59 tests with **3 failing assertions/subtests and 1 uncaught error**; the Windows job was cancelled. These are adversarial fictional values, not observed publisher records.

**Correction:** `parquet_export.normalized_row` and `retail_gate.parse_row` now reject any nonfinite business-hour aggregate and treat unrepresentably large integer inputs as structured validation failures. The in-memory and SQLite engines share the corrected parser. An ordinary large but finite (`1e300`) control remains accepted. Existing forecast formulas and scoring metrics were not changed.

**Verified final-head CI:** [GitHub Actions #40159084816](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40159084816) passed **59/59 tests** on Ubuntu and Windows with Python 3.13, including four new fictional negative/control tests. The before-fix failure remains preserved for review.

**Boundary:** this is numerical evidence integrity, not measured forecasting accuracy. The official 106 MB pinned train Parquet was **not downloaded or parsed**, no actual-data metrics were produced, and no maturity advancement is warranted. The remaining high-value gate is unchanged: acquire exact pinned bytes, independently hash, run `pyarrow` export, reproduce the frozen chronological benchmark, and retain negative results.
