# FreshRetailNet-LT v3.1 — publisher baseline pooled-metric arithmetic preflight (2026-11-02)

**Evidence classification:** fictional-only local software tests plus direct inspection of public publisher baseline source. **Stage:** Research / Architecture, unchanged. **Official EVAL scoring:** not performed. **Browser pre-evaluator equivalence:** TBD.

## Decision-changing source reconciliation

The publisher's [FreshRetailNet-LT leaderboard](https://dingdong-inc-freshretailnet-lt-leaderboard.static.hf.space/index.html) specifies full 70,000-target coverage, then eligibility `psd >= 0 AND stock_hour6_22_cnt == 0`, and WAPE/WPE/MAE/MSE. Direct inspection of publisher's `Dingdong-Inc/frn-baseline` at commit `e1791eac10c49ebedba1c1440ce229d0c542a6ab` found:

- `demand_forecasting/TFT/predictTFT.py`, Git blob `26ab9f2f71bb565ae9208918866370a46c7879e2`: `cal_metrics()` sets `target_dates=['all_days']`, filters `psd>=0` then `stock_hour6_22_cnt==0`, and computes **pooled** WAPE = sum(abs(pred−actual))/sum(abs(actual)), WPE = sum(pred−actual)/sum(abs(actual)), MAE = mean(abs(pred−actual)), MSE = mean((pred−actual)^2). This is **not** an unweighted mean of seven daily WAPE ratios.
- `demand_forecasting/SSA/ssa_forecasting.py`, Git blob `dfd8797e0accc0a86d8a2c5859866c6db2f60e8f`, also computes pooled WAPE/WPE/MAE/MSE over stockout-free rows, but does not explicitly apply the TFT `psd>=0` filter in its `evaluation()` function. This is a source-level difference; **the leaderboard's separate pre-evaluator remains the authoritative protocol**.

## Independent fictional contract

The executable `freshretail_lt_pooled_metric_contract_v31.py` computes pooled metrics only on eligible fictional rows, exposes per-day diagnostics separately, and rejects malformed dates, missing/extra fields, negative/nonfinite predictions or labels, invalid stockout counts, no eligible rows and zero pooled actual-sales denominator. It does not load publisher EVAL, compute `psd`, check full-target coverage, or substitute for the v3.0 mask contract.

**Fictional counterexample:** day 1 actual=1, prediction=0; day 2 actual=9, prediction=9. Pooled WAPE is **0.1**, whereas the unweighted average of day-specific WAPE values is **0.5**. Pooled WPE is **−0.1**, MAE **0.5**, MSE **0.5**. The two excluded fictional rows (negative psd and stockout) are not performance claims.

**Local execution:** CPython 3.13.5 on Linux (exact patch/build TBD), `python -B -m unittest -v test_freshretail_lt_pooled_metric_contract_v31.py` -> **15/15 PASS**. Code Git blob SHA-1 `f9c0a2d79b1346f71f54a447d6a2491006c1fa77`; tests Git blob SHA-1 `ece9626af204e5ae89cc9db467424fb837768364`. [GitHub Actions #41337999653](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41337999653) at code-bearing head `800f28e89cc0fcd2bd5b6546cc54810e569a3526` **passed 15/15 tests on Ubuntu 24.04 and 15/15 on Windows 2022**; both job logs were independently inspected, including the `OK` summaries. The exact source/test blobs match the locally tested files. Browser parity and real-data scoring remain **TBD**. This note must be amended if source differs on a newer publisher revision.

## Gate, decision and four lenses

**Strongest evidence:** publisher baseline's pooled `all_days` code and locally tested fictional arithmetic. **Largest gap:** exact browser/maintainer scoring-reference implementation and pinned precomputed psd source, then scoring of the already frozen 70,000 historical-only predictions against a strong comparator. **Next experiment:** independently authenticate publisher scoring-reference bytes, pin evaluator revision and reference `psd` keys, and prove parity on a small publicly documented test vector before privately running exploratory EVAL scoring. **Kill/reframe:** if browser and baseline differ, follow browser reference and preserve discrepancy; never claim leaderboard parity without an exact reference match. EVAL labels are public, so any result is exploratory, not unseen confirmation.

**Hiring manager:** detects a material metric-aggregation ambiguity. **Technical reviewer:** source SHA, precise arithmetic, negative controls and unverified browser parity. **Innovation leader:** no novelty/patentability claim. **Founder:** no forecasting advantage, customer, revenue or product performance demonstrated. No outreach, release, deployment, employer or personal data.
