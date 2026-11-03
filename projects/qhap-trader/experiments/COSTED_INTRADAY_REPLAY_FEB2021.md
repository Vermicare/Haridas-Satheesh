# QHAP-TRADER — First costed intraday stock replay

**Recorded:** 2026-11-03  
**Stage:** Software feasibility + exploratory historical demonstration. **Not an out-of-sample profitability result, not investment advice, not an active bot.**  
**Decision:** Keep the baseline experimental. **Do not promote the DTT filter**; it reduced net results on both securities under both modeled slippage settings.

## Question

Can a simple, long-only Indian equity intraday rule make money after simulated fills, brokerage, taxes and slippage on a small historical sample—and does adding the earlier, unvalidated DTT hypothetical switching-mass veto improve those outcomes?

The answer on this small sample is **not consistently**: one stock produced a tiny positive net simulation at low slippage, but it turned negative with higher slippage. The DTT veto did worse than the rule-only baseline on both stocks.

## Data and qualification

- **Source:** third-party public [gsidhu/nse-intraday-data](https://github.com/gsidhu/nse-intraday-data), February 1–16, 2021 stock 1-minute OHLCV files for **ACC** and **RELIANCE**. The files have **not** been independently verified against official NSE market records or corporate action history. Data rights must be checked before use beyond this research; its code repository's software license does not establish downstream redistribution rights for exchange data.
- **Observations:** 12 trading days for each stock (Feb 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16). The test had 24 *symbol-sessions* but only **12 distinct days**, **not** 24 independent market days.
- Intraday source candles may omit 09:15; this replay requires a complete minute sequence **09:30 through 15:00** and deliberately uses a 09:30–09:39 **proxy range**. It is **not** an authentic 09:15 opening-range breakout test.
- The same securities and days were previously examined for a DTT AUC diagnostic, so this is an **exploratory development-set evaluation**, not fresh untouched historical holdout. Any positive result must be independently retested.
- No pre-open auction snapshots, bid-ask quotes, consolidated corporate actions, full order book or actual trader psychology observations were used.
- **Each stock is a separately simulated ₹10,000 account**. Do not sum results or imply both are simultaneously traded under one ₹10,000 account.

## Frozen illustrative paper rules for this pilot

1. Compute reference high/low from 09:30–09:39 candles; begin candidate detection at 09:40.
2. Trigger a **long-only** candidate when a completed minute close crosses **from at/below to above** the reference high. Use **the next minute's opening price** to simulate entry; at most one position per stock per session.
3. Buy simulated **integer shares**; position market value capped at ₹2,000; reserve at least ₹4,000 of simulated cash; use an illustrative ₹50 per-trade sizing budget. No leverage, shorts, derivatives or overnight positions.
4. After entry, use a 1% protective stop and 1.5% take-profit anchored to the simulated slip-adjusted buy price. If stop and target are both reachable within a one-minute candle, **stop executes first** by assumption; unfavorable gap open uses the worse opening price. This cannot guarantee actual fill prices.
5. Force a simulated exit at the 14:55 candle open at the latest; do not open new positions after a 14:30 signal. Any missing minute from 09:30 to 15:00 rejects the entire symbol-session.
6. Baseline: use all qualifying crossovers. DTT-veto variant: ignore a candidate when the **hypothetical eight-policy DTT switching mass** is at least **0.10**, and allow later candidates to qualify. The DTT filter can therefore change timing; this is a policy comparison rather than an exact trade-matched ablation.
7. Paper equity is updated after each day; code also includes a peak-to-trough drawdown lock and a simplified calendar-week loss lock. These were **not challenged** by the sample's small observed losses. The implementation does not reproduce complete real exchange/order failures or live risk management.

## Cost model (2026 reference rates applied to February 2021 candles)

**This is a cross-period sensitivity scenario, not historically accurate 2021 fees.** A broker has **not** been selected.

- Intraday brokerage: lesser of ₹20 or **0.03% per executed order**.
- NSE transaction charges: **0.00307%** of buy+sell turnover.
- SEBI turnover fee: **0.0001%** of buy+sell turnover.
- GST: **18%** of brokerage + exchange charges + SEBI fee.
- Stamp duty: **0.003%** on buy notional.
- Equity intraday securities transaction tax: **0.025% on sell notional**, approximated with nearest-rupee rounding for each paper sell.
- Two slippage scenarios: **5** and **15 basis points per side** on the buy and sell fill prices. A single-bar replay cannot confirm real slippage or market impact; additional failed-fill, latency, partial-fill and gap modeling remains necessary.
- Example references: [Zerodha published charges](https://zerodha.com/charges/), [NSE statutory charges](https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies), [Zerodha STT rounding](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated).

**Not included:** point-in-time 2021 broker/tax revisions, market-impact calibration, partial fills, exchange auction eligibility, broker square-off penalties, price-limit circuits, capital-gains income-tax treatment, data subscription costs or live API infrastructure costs.

## Results: hypothetical net P&L per independently simulated ₹10,000 account

| Symbol | Strategy | 5 bps/slippage side — trade count | 5 bps net P&L | 15 bps/slippage side — trade count | 15 bps net P&L |
|---|---|---:|---:|---:|---:|
| ACC | Opening proxy breakout | 9 | **−₹3.61** | 9 | **−₹22.99** |
| ACC | Breakout + DTT veto | 4 | **−₹22.78** | 4 | **−₹31.69** |
| RELIANCE | Opening proxy breakout | 5 | **+₹17.17** | 5 | **−₹27.29** |
| RELIANCE | Breakout + DTT veto | 3 | **−₹34.81** | 3 | **−₹60.71** |
| Either | NO TRADE control | 0 | ₹0 | 0 | ₹0 |

At 5 basis points/side:
- ACC rule-only had 4 winning and 5 nonwinning closed paper trades, **₹9.23 gross** and **₹12.84 modeled fees** → **−₹3.61 net**.
- ACC DTT-veto: 1 win / 4 entries → **−₹22.78 net**.
- RELIANCE rule-only: 2 wins / 5 entries, **₹24.99 gross** and **₹7.82 modeled fees** → **+₹17.17 net**.
- RELIANCE DTT-veto: 0 wins / 3 entries → **−₹34.81 net**.
- All the above include modeled slippage in gross P&L, and stated broker/statutory charges deducted afterwards.
- These **are not** daily income rates, estimates of true expected returns or evidence of an investable strategy. The positive ₹17.17 is particularly fragile to slippage.
- A win percentage with as few as three to nine trades is not a meaningful estimate of future success.

## Reproducibility and provenance

- [Offline Node.js test runner](costed_intraday_pilot.mjs): reads only source text files supplied locally in the published third-party directory structure, standard-library-only, outputs a complete per-stock/per-trade journal and source-file SHA-256 fingerprints, no network or broker connections.
- [Synthetic invariant test file](test_costed_intraday_pilot.mjs): Node.js built-in test runner, run with `node --test test_costed_intraday_pilot.mjs`.
- Run pilot from this directory using `node costed_intraday_pilot.mjs /path/to/nse-intraday-data 5`, repeat with `15` for slippage stress.
- Direct in-session checks: **seven synthetic invariant tests passed** on the exact replay core extracted from the committed first version, including no-trade, next-bar timing, ambiguous-bar stop priority, missing-minute fail-closed behavior, costs and slippage stress.
- Historical numbers were calculated in-session using the same pure replay function extracted from the committed file and the third-party GitHub connector content; the independently packaged CLI and Node test file have **not yet been executed with a local full-data checkout**, so **independent CLI reproduction remains pending**. Do not claim completed continuous integration until verified.
- Source-file GitHub blob references were observed on ingestion. The standalone runner will record original bytes' **SHA-256** on independent reproduction.
- **Raw third-party candles intentionally excluded from this repository.**

## Current evidence gate and next research

**G1: Prototype calculations function on synthetic tests.** Some elementary invariants tested. Full simulator correctness and fee reconciliation to an independent official broker calculator are **not yet confirmed**.

**G2: Net profitability — FAIL / INSUFFICIENT EVIDENCE.** No out-of-sample, multiple-regime, independent historical proof of positive post-cost expectancy. DTT must stay **QUARANTINED**.

Next:
1. Independently execute committed runner and tests; archive checksums, environment and complete outputs.
2. Obtain authorized, high-quality intraday individual-equity data across **multiple years and regimes**, including verified corporate actions and trade calendars. Preserve point-in-time universe membership.
3. Audit current and historical broker/statutory charges and broker order semantics with a trusted reference calculator. Add bid-ask, partial fills, realistic adverse gaps and order rejection; stop-price fills cannot be guaranteed.
4. Preregister later untouched chronological evaluation *before model/feature tuning*, compare NO TRADE, simple breakout, VWAP control and any new behavioral veto with consistent sizing and equal trade-selection opportunity sets.
5. Paper-forward observe at least 60 complete sessions, but recognize that duration alone does not establish edge. **Never** promote to live trading automatically.

**Bottom line: the positive low-friction result for one stock does not survive slippage stress; the proposed DTT veto made this illustrative replay worse.**
