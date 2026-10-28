# Retail v1.9 — TRAIN-only 2025 cohort eligibility (2026-10-28)

**Evidence boundary:** this package can verify a preregistered TRAIN-only cohort. It does **not** open or download FreshRetailNet-LT evaluation labels, make forecasts, score a model, or validate latent demand. Maturity remains **Research / Architecture**. The v1.5 superiority gate remains **FAILED**.

## Predeclared question

Does the independently byte-verified FreshRetailNet-LT v1.0 TRAIN split contain at least **512 distinct, nonduplicate store/product series**, each with a valid **90-day uninterrupted daily record** from **2025-04-15 through 2025-07-13** inclusive? This is a necessary eligibility condition for the frozen v1.8 prospective transfer, not a claim of predictive value.

## Source and reproducibility

- Publisher: [Dingdong-Inc/FreshRetailNet-LT](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-LT), declared CC BY 4.0; revision `01c3bb306415e09d3ccd2fe762f33eb3aeb2affd`.
- TRAIN expected **315,398,578 bytes**, SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`. v1.8 previously verified publisher TRAIN/EVAL bytes, but v1.9 downloads **TRAIN only**.
- Script: [freshretail_lt_train_cohort_v19.py](freshretail_lt_train_cohort_v19.py); [ten fictional adversarial tests](test_freshretail_lt_train_cohort_v19.py); [GitHub workflow](../../../.github/workflows/retail-lt-train-cohort-v19.yml). Python 3.13, `pyarrow==20.0.0` in hosted run.
- Only `store_id`, `product_id`, `dt`, `hours_stock_status`, and `stock_hour6_22_cnt` are read. No target `sale_amount` or `hours_sale` is accessed; no EVAL path is an argument.
- Require nonnegative integer keys, canonical daily dates, 24 binary status flags, stockout count matching positions 6–21, no duplicate days, exactly 90 dates per eligible series. Reject any TRAIN row dated on/after 2025-07-14. An invalid or duplicated series cannot enter the cohort.
- Rank eligible keys by SHA-256 of `retail-lt-v18-20261028|store_id|product_id`, then freeze first 512. No EVAL-derived selection or replacement is permitted. Emit aggregate counts and a SHA-256 of the selected keys, **never the raw selected IDs or source rows**.

## Stop / advance rules

If fewer than 512 complete valid TRAIN series exist, record **STOP_INSUFFICIENT_ELIGIBLE_TRAIN_SERIES**, cohort hash **TBD**, and **do not** loosen the window, retune the selection, substitute incomplete series, or score evaluation labels. A schema mismatch, unexpected future TRAIN row or failed source hash aborts before any claim. Any change to the predeclared design must become a *new exploratory protocol*, not a retroactive repair.

If 512 qualify, the output only establishes a **frozen training-only cohort**. Next separately seal the unchanged four model predictions with a timestamped digest *before* evaluation labels are parsed, verify all seven future dates without replacement, and execute the predeclared paired whole-store day-weighted uncertainty analysis. Forecasting performance, revenue, lost-demand ground truth, product readiness and independent validation remain **TBD**.

## Four-lens interpretation

**Hiring manager:** inspect executable provenance, negative-result handling and clean-runner test evidence. **Technical reviewer:** challenge the strict 90-day requirement, identifier stability, date/status validation and the future-label firewall. **Innovation leader:** this tests transportability to a later public calendar, not algorithmic novelty. **Founder:** no measured inventory or commercial impact, so no pilot/product claim.

**Privacy / IP:** public publisher data only, no employer data, no contact tracking, no raw rows in GitHub. Publisher-byte identity does not independently authenticate the publisher. No patentability statement.
