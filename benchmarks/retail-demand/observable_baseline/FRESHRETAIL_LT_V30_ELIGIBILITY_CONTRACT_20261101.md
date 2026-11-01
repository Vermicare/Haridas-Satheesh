# Retail v3.0 — publisher eligibility-mask contract (2026-11-01)

**Status: VERIFIED fictional software contract, NOT an execution on publisher EVAL.** Stage remains **Research / Architecture**. No official score, leaderboard claim, latent-demand recovery, customer or commercial outcome.

## Why this changes the next experiment

The [publisher's live evaluation notes](https://dingdong-inc-freshretailnet-lt-leaderboard.static.hf.space/index.html) require **full target coverage before scoring** and then apply `psd >= 0 AND stock_hour6_22_cnt == 0`. The publisher defines `psd` as the store/product mean raw daily sales over **2025-06-02 through 2025-07-13**, precomputed in its public scoring reference. EVAL-period stockout status is a **scoring-only answer field** and must never enter forecasting inputs. The earlier v2.7/v2.8/v2.9 full-target coverage and digest results do **not** establish mask equivalence or performance.

## New executable boundary

- [v3.0 contract](freshretail_lt_eligibility_contract_v30.py) and [16 adversarial fictional tests](test_freshretail_lt_eligibility_contract_v30.py) require complete exact-key coverage through the unmodified [v2.7 gate](freshretail_lt_full_target_gate_v27.py) **before** mask aggregation.
- The scorer-only input permits exactly `store_id, product_id, dt, stock_hour6_22_cnt`; it **rejects** evaluation sales labels, hourly sales, hourly stock-status arrays and unexpected fields.
- `psd` must be independently supplied in a **separate** one-to-one series reference. Missing, extra, duplicated or nonfinite references fail closed; no implicit zero or mean-imputation is permitted.
- A fictional four-row fixture exercises **eligible**, **excluded-psd**, **excluded-stockout** and **excluded-both** cases. Malformed counts, negative/out-of-range counts, missing fields, missing/duplicate targets, incomplete predictions, nonfinite psd and noncanonical keys are rejected.
- The result contains aggregate totals and per-day category counts only. It explicitly reports `eval_sales_labels_read=false`, `eval_stockout_mask_read=true`, `publisher_reference_equivalence=TBD`, `metrics=TBD`, `official_leaderboard_comparable=false`. No raw row IDs or predictions are published.

## Reproduction and verified hosted evidence

From `benchmarks/retail-demand/observable_baseline`:

```bash
python -B -m unittest -v test_freshretail_lt_full_target_gate_v27 test_freshretail_lt_eligibility_contract_v30
```

A new [read-only two-OS workflow](../../../.github/workflows/retail-lt-eligibility-v30.yml) pins Python 3.13 and never downloads publisher data or contacts external services.

The existing [Retail synthetic-contract workflow #41327299853](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41327299853) at final code head `3dd5e37839e3e362eb66398c22a8a6764a9856c5` passed **282/282 tests on Ubuntu and 282/282 on Windows**, including all **16 new** tests per OS. Both original job logs were independently fetched and inspected. This verifies **fictional software behavior only**; it does not prove reference equivalence. The separate v3.0 workflow's own execution outcome is **TBD** until independently inspected. See [machine-readable registry](FRESHRETAIL_LT_V30_ELIGIBILITY_CONTRACT_REGISTRY.json).

## Remaining gap and preregistered next step

1. Acquire the publisher's **precomputed psd reference** with an exact version, byte digest, and independently documented provenance; verify whether `psd` values/keys match the pinned 70,000-target EVAL snapshot.
2. Freeze the publisher's actual metric aggregation convention (including per-day vs pooled WAPE/WPE) against its reference implementation; **do not guess**.
3. Only after freezing, score the already SHA-pinned **historical-only** 70,000-row prediction file and a predeclared strong comparator in private ephemeral storage. Publish aggregate-only eligible/excluded counts, per-day metrics, uncertainty, and explicit exploratory status because EVAL labels are public.
4. Kill/reframe leaderboard/superiority claims if reference keys or metric definitions cannot be reconciled, if label leakage is found, or if strong comparator advantages fail. Reframe as observed-sales forecasting/partial identification if latent demand is not identifiable.

**Four lenses:** hiring manager—traceable software contract; technical reviewer—fail-closed full-target and mask semantics but reference parity TBD; innovation leader—falsifiable next scoring gate, no novelty claim; founder—no demonstrated business value.

**Preserved:** frozen v2.1 results, v2.4/v2.5 negative partial-identification controls, v2.8 full-target digest, v2.9 two-host reproduction, and WBI frozen synthetic evaluator. No stage advancement, merge, release, employer data, external action or outreach.
