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

## Verified hosted result — 2026-10-28

[Hosted run #40682609113](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40682609113) and [separate hosted run #40682619596](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40682619596) both **succeeded** on the same source revision and code-bearing head `444fc9dd0e7b423103a292a741d3f04fb02cbfdb`. Both ran **10/10 fictional adversarial tests on Ubuntu and 10/10 on Windows** and downloaded only the pinned TRAIN file. The Python 3.13.16 / PyArrow 20.0.0 real-data pass produced:

| Aggregate TRAIN-only observation | Verified value |
|---|---:|
| Original TRAIN bytes / SHA-256 | 315,398,578 / `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3` |
| Earlier rows outside the frozen 2025 window | 6,895,143 |
| Rows inside frozen 90-day window | 974,406 |
| Distinct series with any rows in window | 13,255 |
| Complete valid 90-day series | **7,552** |
| Duplicate / invalid-stock-status rows | **0 / 0** |
| TRAIN-only cohort frozen | **512 series** |
| Frozen cohort SHA-256 | `dc128d3bed90035214c80529bf58e685ad7d49c717d95bd10c30c2b9407ca016` |
| Evaluation labels opened / forecast results | **No / TBD** |

**Independent artifact check:** the first uploaded ZIP (artifact `12814240520`) has SHA-256 `4a95fdf4fc6a1e3935b3589fa4af21135349f2670f47d4ed4633b7b412468585`; its sole JSON member has SHA-256 `e6cead2de3f940635b3860fb528bf633af91d54a7142b84204fe160e9a546132` and Git blob `533aae9c66d89fd26d1e9978fbdd88b2c5c9d3b9`. The [committed aggregate result](FRESHRETAIL_LT_V19_TRAIN_RESULT.json) was reread and matches that blob **byte-for-byte**. The second artifact (ID `12813118806`) independently reproduced **all substantive counts, the source fingerprint and the cohort digest**; its JSON differs only in `provenance.git_checkout` (PR merge checkout vs branch head). Raw source rows and cohort IDs were not published.

**Decision:** the predeclared TRAIN-only eligibility gate **PASSES**. This is **not** a forecasting superiority result or evidence of a real-world benefit. Do **not** inspect evaluation labels until all four frozen model predictions have been sealed with provenance and a reproducible hash; reject missing future dates without replacing series. The previous v1.5 superiority failure is preserved. Stage **Research / Architecture**, unchanged.
