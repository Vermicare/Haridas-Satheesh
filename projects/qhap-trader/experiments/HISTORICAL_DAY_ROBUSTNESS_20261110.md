# QHAP-TRADER — Historical day-block robustness and fragility audit (2026-11-10)

**Result:** Historical strategy findings are too fragile to justify trading. This is an audit of already-inspected development data, NOT an untouched-data or prospective profitability test.

## Verified execution

- [GitHub Actions historical audit #42875490082](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/42875490082): SUCCESS.
- New Node diagnostics: 14 tests passed, 0 failed.
- Original pinned third-party source Git blobs: 24/24 matched from gsidhu/nse-intraday-data at pinned upstream SHA c95d7f187c2a317ca6a2287148cf10c50a80e928.
- Original replay historical net results: 8/8 snapshots reproduced under 5 and 15 basis points per side.
- Source text was fetched temporarily into the runner; NO original OHLCV bars were committed or uploaded.

**The dataset is 12 distinct dates** (Feb 1–16, 2021), for ACC and RELIANCE (24 symbol-days). Each security has its own simulated INR 10,000 account; do not combine the accounts into one investment result.

## Method

The new [day-level robustness script](historical_day_robustness.mjs) checks full dates, instrument keys, SHA-256 input fingerprints, all 12 ledger days for each stock, per-trade net arithmetic, and the existing summary.

It applies a deterministic 10,000-repetition **day-block bootstrap**: resample full market dates as units with replacement, preserving zero-trade days. This avoids the obviously incorrect assumption that individual minute bars within one day are independent experiments. It estimates a descriptive 95% percentile interval for a hypothetical sum over 12 resampled historical dates. The interval is NOT a probability of future returns, a forecast interval, statistical proof of an advantage, or a forward result.

The script also calculates leave-one-date-out total P&L, policy differences using paired calendar dates (NOT same trades), and sensitivity to 5-versus-15-bps-per-side friction. It does not optimize strategy thresholds or refit any model.

**Extra limitation:** The bootstrap reuses fixed daily historical ledger outcomes. It does not recompute exposure, portfolio sizing or risk locks on each resampled path; thus it is a fragility diagnostic, not a full path-dependent Monte Carlo trading simulation.

## Results in INR (each stock separate INR 10,000 hypothetical account)

| Symbol | Policy | Slippage/side | Historical net | Leave-one-day-out range | 10k day-bootstrap 95% sum interval |
|---|---|---:|---:|---:|---:|
| ACC | Baseline | 5 bps | −3.61 | [−27.39, +16.94] | [−115.97, +110.50] |
| ACC | DTT veto | 5 bps | −22.78 | [−46.56, −2.24] | [−93.12, +50.77] |
| ACC | Baseline | 15 bps | −22.99 | [−45.02, −0.61] | [−133.90, +90.25] |
| ACC | DTT veto | 15 bps | −31.69 | [−53.72, −9.32] | [−107.63, +44.06] |
| RELIANCE | Baseline | 5 bps | +17.17 | [−9.36, +39.07] | [−65.91, +103.95] |
| RELIANCE | DTT veto | 5 bps | −34.81 | [−34.81, −12.91] | [−84.11, 0.00] |
| RELIANCE | Baseline | 15 bps | −27.29 | [−50.88, −3.45] | [−111.54, +56.78] |
| RELIANCE | DTT veto | 15 bps | −60.71 | [−60.71, −36.86] | [−132.06, 0.00] |

The only original positive result, RELIANCE baseline at 5 bps/side (+INR 17.17), **turns negative after omitting one particular date** and also under the 15 bps/side scenario (−INR 27.29). All the day-bootstrap intervals touch or cross zero. The DTT-veto policy had lower observed original net outcomes than baseline for both symbols at both friction levels.

DTT minus baseline paired **day-level** differences: ACC −19.17 (5 bps), −8.70 (15 bps); RELIANCE −51.97 (5 bps), −33.41 (15 bps). They do NOT measure a causal matched-trade effect because trade selection and entry timing may differ.

**NO_TRADE = INR 0** is the mandatory comparator. It beats 7 of the 8 stock/policy/slippage point results.

## Evidentiary boundaries and next steps

- The stock/days have already been examined during development. There is **NO new pristine holdout** and no credible independent estimate of net profitable expectancy.
- Date dependence, sample selection, market regime shift and source integrity are not resolved by bootstrapping only 12 days.
- Third-party data rights and authenticity against NSE exchange records remain unverified. The 2021 data uses illustrative 2026 fees and is not historically accurate to 2021 costs.
- Bid-ask, market impact, partial fills, real broker executions, platform uptime, and historic session exceptions remain unverified.
- Strategy tuning on these same 12 days would worsen selection bias. **Quarantine the DTT veto** unless separately preregistered and tested using genuinely unseen, licensed historical data.

Next: obtain authorized minute data from **new years and regimes**, preregister frozen strategies, include NO_TRADE and simple baselines, model Indian fees/fills conservatively, then establish monitored read-only prospective session data before 60+ days of forward paper observation. None of this authorizes real orders.

## Reproduction and safety

From repo root on Node.js 22+:

    node --test projects/qhap-trader/experiments/test_historical_day_robustness.mjs
    node projects/qhap-trader/experiments/historical_day_robustness.mjs /path/to/qhap-5.json /path/to/qhap-15.json

The linked GitHub Actions workflow reproduces both pre-existing historical JSON outputs from temporarily downloaded **pinned and hash-checked** third-party source files. It never redistributes the raw data. No Upstox token, billable model call, financial order, real money, or trading account is used.
