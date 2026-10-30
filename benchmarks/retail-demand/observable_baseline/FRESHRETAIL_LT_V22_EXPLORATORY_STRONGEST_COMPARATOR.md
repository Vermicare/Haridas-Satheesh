# Retail v2.2 — exploratory strongest-simple-comparator sensitivity (2026-10-29 IST)

**Decision: INCONCLUSIVE versus causal stockout history.** The weekday-median method's small descriptive MAE advantage does **not** exclude zero under a matched paired whole-store bootstrap interval. This is a **post-hoc analysis of already opened public 2025 labels**, not a new confirmatory test. **Maturity: Research / Architecture unchanged.**

## Why this changes the interpretation

The separate [v2.1 preregistered primary gate](FRESHRETAIL_LT_V21_TEMPORAL_TRANSFER_RESULT.md) passed **weekday median versus last-observed**. It did **not** test superiority over the stronger causal-stockout-history baseline with a matching interval. v2.2 tests that specific gap without changing any v2.1 forecast, selected series, source bytes, primary decision or the **FAILED** 2024 v1.5 result.

The [v2.2 executable](freshretail_lt_secondary_v22.py) reconstructs the frozen 512-series TRAIN-only forecast commitment **before opening EVAL**, verifies both publisher file digests, independently recalculates the unchanged v2.1 primary decision, then computes per-series paired absolute-error sums against the stronger comparator on **the same 1,766 observed in-stock days**. Whole-store resampling retains every product within each store (2,000 percentile-bootstrap draws; seed 20261029). No store/product identifiers, individual forecasts, original rows or residual arrays are uploaded.

## Verified outcome

| Quantity | Observed |
|---|---:|
| 2025 frozen selected series / scored stores | 512 / 374 |
| Observed in-stock days | 1,766 |
| Stockout-censored days excluded | 1,818 of 3,584 (50.73%) |
| Weekday-median MAE | 0.567264 |
| Causal-stockout-history MAE | 0.576935 |
| Exploratory weekday minus causal MAE | **−0.009671291** |
| Matched paired whole-store 95% percentile interval | **[−0.027864692, +0.010120075]** |
| Leave-one-store-out difference range | [−0.013108671, −0.006834943] |
| Interval excludes zero? | **NO** |
| v2.1 preregistered weekday vs last-observed | **PASS — preserved** |
| 2024 v1.5 primary gate | **FAIL — preserved** |

**Interpretation:** The weekday method has a slightly smaller point error, but superiority to the stronger comparator is **not established**. The leave-one-store-out point differences all favor weekday; this does not override the resampled interval spanning zero. The interval is **descriptive and post-hoc**, not multiplicity-adjusted or confirmatory.

## Reproduction and evidence

- [GitHub Actions run #40774565289](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40774565289) succeeded at code-bearing head `47feca726dd7581a3064fb0ae2ede226d877e911`: **26/26 fictional tests on Ubuntu and 26/26 on Windows** (15 existing + 11 new), followed by pinned-data Ubuntu v2.1 and v2.2 execution. Both final-head test logs and the data job were inspected.
- [Exploratory aggregate ZIP artifact](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40774565289/artifacts/12854936334) independently downloaded, ZIP SHA-256 **`8e32cd8dcf53c6dc3dd77ae0df05408e54d044dd1edc8d2b985157e46afb4d65`**, matching GitHub metadata. Contains one JSON aggregate; inspected values match the job log.
- [Preserved v2.1 aggregate ZIP](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40774565289/artifacts/12855310638) independently downloaded and rehashed: ZIP SHA-256 **`ff94c99ff28b2480d0ab299a066c07a276f1ea423f38e9b029d5b7ed07c80058`**, matching metadata; unchanged v2.1 PASS and original prediction commitment confirmed.
- Source Git blob `6ff48485af45fa490180a8b9ac72a37f21f75a4b`; tests `b11789d557ddacd3367bd62cef02449d64c380d9`; workflow `ebbba61e772aedaf967425c9e387c400ebb3183f`. Runtime: Python 3.13.17, Linux for publisher scoring; 3.13 on both hosted operating systems for fictional tests; PyArrow 20.0.0. The dataset's revision, TRAIN/EVAL SHA-256 and prediction seal are pinned in [the registry](FRESHRETAIL_LT_V22_EXPLORATORY_REGISTRY.json).
- Reproduce after acquiring the pinned publisher files, from this directory: `python -B -m unittest -v test_freshretail_lt_score_v21 test_freshretail_lt_secondary_v22`; then `python -B freshretail_lt_secondary_v22.py --train /private/train.parquet --eval /private/eval.parquet --output /new/aggregate.json`. Output refuses overwrite. No employer data or external actions.

## Decision-changing external benchmark constraint

The [publisher's FreshRetailNet-LT leaderboard](https://dingdong-inc-freshretailnet-lt-leaderboard.static.hf.space/index.html) explicitly says its July 14–20 evaluation labels are **public**, not hidden, and that submissions must cover **all target records** before the scoring mask is applied. This 512-series selected-cohort experiment **does not** qualify as a full leaderboard submission or blinded validation. A separate genuinely unseen publisher or independently locked future cohort is still required. The benchmark's recovery task also cannot observe true unmet demand during actual stockouts.

## Four-lens review and next gate

**Hiring manager:** the result demonstrates a reproducible willingness to challenge a positive result. **Technical reviewer:** inspect store-level paired resampling, label firewall, fixed denominators and unadjusted post-hoc interval. **Innovation leader:** no established new demand-recovery method or novelty claim. **Founder:** no measured lost demand, inventory decision improvement, deployment or customers.

**Next decisive experiment:** lock a genuinely blinded or different-publisher cohort, compare against the **strongest** simple baseline before opening labels, report store-cluster uncertainty and censoring sensitivity, and define a costed inventory-decision metric. Reframe any superiority or latent-demand narrative if that comparison fails. No maturity advance, release, external commitment or patentability claim.
