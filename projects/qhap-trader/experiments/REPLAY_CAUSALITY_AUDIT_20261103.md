# QHAP-TRADER: intraday replay causality audit and regression

**Date:** 2026-11-03  
**Status:** Confirmed simulator bug fixed on research branch; **eight automated synthetic tests passed on GitHub Actions**. Revised historical exploratory sample outputs match previous numbers, but **no validated trading profitability exists**.

## Confirmed defect: 14:55 look-ahead

The first `costed_intraday_pilot.mjs` checked the **high/low of the 14:55 one-minute candle before deciding whether to execute a scheduled exit at the same candle's opening price**. At the opening timestamp, that minute's later range is unknowable. The original branch could retroactively label a 14:55 stop or target instead of the scheduled opening exit.

Reproduced synthetic case (not market data):
- Rule triggers at 14:30, entry at the 14:31 opening.
- The 14:55 candle **opens at ₹101**, later reaches high ₹110 and low ₹90.
- **Before:** the simulator classified the exit as `STOP` at 14:55; illustrative simulated net **−₹21.702654**.
- **After:** it classifies the known-at-open forced exit as `TIME`; illustrative net **−₹3.478815**.
- These are synthetic calculations, not real historical P&L.

**Fix:** At 14:55, choose the time-based opening exit *before* inspecting high/low for stop/target. For earlier candles, keep stop-before-target pessimism when both are touched.

Additional correctness changes:
- Trading-week loss buckets now reset on the actual Monday date, not February dates 1/8/15/22.
- The approximate ₹50 per-trade position-risk sizing now increases its per-share slippage cushion with the configured slippage instead of using one fixed 1.3% denominator. Real fills can lose more than intended due to gaps and illiquidity.

## Verified CI

GitHub Actions [QHAP-TRADER Offline Paper Tests, run #41693339038](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41693339038), executed on the review branch:
- Job **Synthetic replay invariants**: completed / success.
- `node --test projects/qhap-trader/experiments/test_costed_intraday_pilot.mjs`: **8 tests, 8 pass, 0 fail**.
- Verified from the decoded job log, not merely presence of a workflow file.
- Includes new case `14:55 opening exit cannot be selected from later 14:55 high/low`.
- This confirms selected **synthetic program invariants**, not live-order correctness, data authenticity, or market profitability.

## Recheck of original 2021 ACC and RELIANCE experimental figures

After fixing the engine, retrieved the same **24 third-party stock-day source text files** (12 February 2021 days for each of two symbols) through GitHub. Evaluated the exact original and branch-corrected `runPilot` functions on the same source contents and paper cost settings.

| Stock / simulated strategy | Slippage, basis points per side | Original net ₹ | Corrected net ₹ | Delta ₹ |
|---|---:|---:|---:|---:|
| ACC breakout baseline | 5 | −3.613323 | −3.613323 | 0 |
| ACC DTT veto | 5 | −22.784561 | −22.784561 | 0 |
| ACC breakout baseline | 15 | −22.987469 | −22.987469 | 0 |
| ACC DTT veto | 15 | −31.688167 | −31.688167 | 0 |
| RELIANCE breakout baseline | 5 | +17.168397 | +17.168397 | 0 |
| RELIANCE DTT veto | 5 | −34.806530 | −34.806530 | 0 |
| RELIANCE breakout baseline | 15 | −27.294151 | −27.294151 | 0 |
| RELIANCE DTT veto | 15 | −60.705623 | −60.705623 | 0 |

All eight variants produced the same trade counts and session ledgers in this particular historical sample. **The bug is real but was not activated in the selected historical trade paths.** Do not generalize this invariance to other market days or data.

### Execution provenance and limits

- Historical computation used in-session execution of the exact original and corrected **pure replay function bodies fetched from GitHub** with retrieved source texts. This is stronger than comparing published summaries but **does not constitute a separate local full-directory Node CLI reproduction**.
- Original core file GitHub blob at comparison: `2c4740c2813857580009dd5da3b4d822c9787ab3`; corrected research branch blob: `13c3e9d8857f22610435e9c9b1f2d4ee03888d0f`.
- Data: [gsidhu/nse-intraday-data](https://github.com/gsidhu/nse-intraday-data); file-level GitHub blobs were compared for both equities. **Underlying one-minute OHLCV accuracy, data licensing, corporate-action treatment and original exchange timestamps remain unaudited**.
- No original 2021 fees were reconstructed; [cost scenario](COSTED_INTRADAY_REPLAY_FEB2021.md) uses a published 2026 brokerage-style schedule. No real broker was selected.
- One-minute bar replay cannot establish actual bid/ask spreads, order-book depth, fill probability or real stop-loss execution.
- No genuine unseen data test. These securities and days are development samples examined in multiple iterations. Small +₹17.17 simulated result is fragile, not a strategy return forecast.

## Remaining high-priority acceptance tests

1. Independent local **Node CLI historical reproduction** with source SHA-256 and output snapshot; compare to this table.
2. Audited current and historical exchange/broker fee schedules, including rounding, GST treatment and cash reservation at time of entry.
3. Missing data at the intended exit timestamp, partial fills, adverse opening gaps, market halts and rejected order states.
4. Separate no-trade and rule-only comparator on newly procured **licensed, authenticated individual-equity data**, with untouched chronological holdout and pre-registered success criteria.
5. Weekly loss and drawdown locks under deterministic large-loss fixtures. The existing small historical sample did not exercise those limits.
6. A standing paper monitor may be considered only after all safety/control gates pass. **No broker connectivity or live deployment.**

**Verdict:** A verified causal execution defect was removed; the historical experimental verdict **remains unchanged**: no demonstrated net-of-cost trading edge and no DTT promotion.
