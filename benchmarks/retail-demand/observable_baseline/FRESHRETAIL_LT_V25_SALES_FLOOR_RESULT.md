# Retail LT v2.5 — conditional observed-sales-floor sensitivity (verified negative decision)

**Date:** 2026-10-29. **Stage:** Research / Architecture, unchanged. **Design:** post-hoc sensitivity on the *already inspected* public 2025 evaluation set; **not** a new blinded or confirmatory test. **Decision:** full-period latent-demand MAE ranking remains **UNIDENTIFIED** under the additional, unverified assumption that recorded business-hour sales are a lower bound on latent demand for the identical target period.

## Why this experiment matters

The previous v2.4 nonnegative-demand-only paired absolute-error bounds included both signs because 1,818 of 3,584 future days were stockout-censored. v2.5 asks a narrower conditional question: if the dataset's recorded sales for a censored day really satisfy `latent demand >= observed sales` on that *same* target, does that identify which frozen forecast has lower full-period MAE? This assumption has **not** been independently validated against the publisher's sales, returns, substitutions, business-hour and inventory semantics. No missing demand is imputed; no arbitrary upper demand cap is chosen. These are **sharp logical bounds conditional on the assumption**, not statistical confidence intervals.

## Frozen-source, independently inspected result

[Completed final-code-head PR workflow #40924685434](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40924685434), source head `c8b0ddc08e2dfcedd6981df0726947ec9c6d63e4`, checkout merge `f5b8eef8a3fc5adc4b99dfa9843b56e2c28e366d`, used CPython 3.13.17/Linux for the public-data scorer. The Ubuntu and Windows fictional-contract jobs used CPython 3.13.17 and 3.13.16 respectively: **42/42 tests per OS** (12 v2.4 + 11 floor engine + 7 v2.5 transfer + 12 v2.3 selftests). All three job logs were independently inspected. Both exact publisher Parquet hashes and the frozen TRAIN-only prediction seal were checked before the reported public evaluation. The previous 2024 v1.5 FAIL, 2025 v2.1 narrow PASS and v2.2 strongest-comparator INCONCLUSIVE are preserved.

**Denominator:** 512 frozen series / 374 stores; 3,584 future days, **1,766 observed in-stock** and **1,818 stockout-censored**; **1,729 censored days have a positive recorded-sales floor**. Candidate A = training-only weekday median. The paired difference is **MAE(A) − MAE(B)**; a negative interval entirely below zero would identify A as better, while an interval entirely above zero would identify B as better.

| Comparator B | v2.4 nonnegative-only full-period interval | v2.5 conditional sales-floor interval | Identified ranking? |
|---|---:|---:|---|
| Causal stockout-history baseline | [−0.118096401, +0.108565430] | **[−0.046500140, +0.070014369]** | **NO — crosses zero** |
| Last-observed baseline | [−0.415067383, +0.335589704] | **[−0.175996512, +0.260968890]** | **NO — crosses zero** |

The interval widths shrink **48.60%** and **41.79%**, respectively, *only conditional on the lower-bound assumption*. Narrower uncertainty is not a forecast improvement, a statistical significance test, or evidence of measured latent demand. The observed-only differences remain −0.009671291 and −0.080647792; they do not determine the full-period ranking.

## Independent artifact and consistency audit

The v2.5 [aggregate-only ZIP artifact #12920657262](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40924685434/artifacts/12920657262) was downloaded and independently SHA-256 verified: `dcb10422ce94946980d3df5dd629525e2611f7e8fe7eebf391786a4cb44dfbf6`. Its sole JSON member SHA-256 is `db925976c15fd49d6466acdad5db7221b6abd2f9b4ccca557380448197ccabfa`. The same run's v2.4 [ZIP #12920617414](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40924685434/artifacts/12920617414) was independently verified: ZIP SHA-256 `87ade5be920eaa38753472ceaf557846c2bf6e44321d46f11817025fc19491cb`, member SHA-256 `399073647ce3802735c31b8ba275071154fba8b2689ad17835fbf7a2f65862c8`. The two parsed JSONs agree on frozen forecast SHA-256 `5c21bce8c9a436ecc0d3173128b0812e4408cc025558faedc2ed0e3497a54e20`, denominators, and original v2.4 bounds. Both v2.5 intervals are nested within the originals and include zero. No raw publisher rows, series IDs or personal data were published. The hosted ZIPs are scheduled to expire **2026-11-12**; their hashes do not preserve the bytes.

Reproduce using [the v2.5 conditional engine](retail_sales_floor_bounds_v25.py), [frozen-source transfer](freshretail_lt_sales_floor_v25.py), [exhaustive-grid tests](test_retail_sales_floor_bounds_v25.py), [transfer tests](test_freshretail_lt_sales_floor_v25.py), and [existing workflow](../../../.github/workflows/retail-lt-stockout-bounds-v24.yml) on this **unmerged draft branch**. The workflow downloads publisher bytes to an ephemeral runner and emits only aggregate JSON. Source provenance, runtime and unknowns are also recorded in the [registry](FRESHRETAIL_LT_V25_SALES_FLOOR_REGISTRY.json).

## Four-lens decision / next evidence gate

**Hiring manager:** reproducible negative conclusion, not inflated forecast success. **Technical reviewer:** check source semantics, frozen prediction seal, censoring assumptions and paired estimand. **Innovation leader:** no novelty or patentability claim. **Founder:** no inventory, revenue, user or deployment evidence.

**Largest gap:** the business-hour sales-as-demand-floor assumption is unverified; the observed data do not identify full-period model ranking. **Next decisive experiment:** obtain independently documented source/target semantics (including returns, substitutions and censoring), then preregister an external or genuinely blinded temporal cohort with a strongest-simple-baseline matched estimand and measured decision costs. **Kill/reframe:** if the floor assumption is invalid, withdraw v2.5 conditional interpretation; if external full-period ranking stays unidentifiable, reframe toward robust decisions under partial identification, not a superior latent-demand predictor. No maturity advancement, merge, release, external commitment or efficacy claim.
