# QHAP-TRADER — First individual-equity DTT diagnostic

**Date analyzed:** 2026-11-03  
**Status:** NEGATIVE / EXPLORATORY. **No incremental DTT predictive value demonstrated.**  
**Trading deployment:** NONE. No executable equity trading system, broker, live orders, or financial-performance claim.

## Purpose

Independently challenge the previously negative August–October 2026 NIFTY 50 INDEX study using **actual stock-level historical bars** rather than an index. This is still **not** a test of trading profits or of real investors' psychology.

## Source and study design

- Public third-party historical minute-bar data: [gsidhu/nse-intraday-data](https://github.com/gsidhu/nse-intraday-data), individual files for ACC and RELIANCE, February 1–16, 2021.
- 12 trading sessions per symbol: February 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16 (24 **symbol-sessions**, 12 distinct days).
- Train/reference: February 1–9 (first 7 days), 399 nonoverlapping five-minute observations **per symbol**.
- Later chronological holdout: February 10–16 (last 5 days), 285 observations **per symbol**.
- 684 observations per symbol; **1,368 observations combined**. Only 10 distinct training dates and holdout dates together; within-day dependence is substantial.
- Observed source files had the required 09:30–09:39 bars and candidate windows; no symbol session excluded. Source may omit the 09:15 opening minute, so the study deliberately defines an *09:30–09:39 reference range*, **not** the true NSE opening range.
- Data was **not** independently checked against official exchange records, corporate actions, or license terms. No third-party raw candles have been copied into this repo.

### Exploratory features

At 09:55, 10:00, ... 14:35, on each day, use the currently closed minute bar and past bars only:

- Baseline = sum of absolute changes of the prior five 1-minute closes (basis points), plus half of the current bar's high–low range in basis points.
- DTT = fractional switches in 8 equally weighted **fictional** policies under fixed -20, -10, +10 and +20 basis-point price perturbations. Four hypothetical upper triggers (09:30 reference high, trailing 10-bar high, intraday cumulative close-volume-weighted price proxy, upward ₹10 grid); four lower triggers (reference low, trailing 10-bar low, intraday price proxy, downward ₹10 grid).
- DTT describes **the simulated policy ensemble**, not actual traders' order flow, sentiment or positions.
- Combined = training-standardized baseline + **0.5** × training-standardized DTT. The 0.5 weight is illustrative, not optimized to the holdout.
- Label = sum of **absolute 1-minute close-to-close changes over the NEXT five minutes**, classified "large" if at least the train/reference 75th percentile **within the same symbol**.
- Evaluation measure = ROC AUC, the ranking ability to identify this future absolute movement. **Not probability of making money, not price direction, not a strategy return.**

## Observed results — later five-day holdout

| Stock | Observations | Baseline ROC AUC | DTT-only AUC | Combined AUC | Combined − baseline |
|---|---:|---:|---:|---:|---:|
| **RELIANCE** | 285 | **0.6683** | 0.3983 | 0.6250 | **−0.0433** |
| **ACC** | 285 | **0.6713** | 0.4088 | 0.6485 | **−0.0227** |

Training large-move cutoff: RELIANCE 31.8006 bp; ACC 50.0451 bp (sum of future five absolute 1-minute returns). Holdout event prevalence: RELIANCE **25.26%**, ACC **16.14%**.

The two securities **both show worse holdout ranking when this DTT formulation is added**. Five distinct holdout days are too few to draw stable statistical conclusions; the securities share market conditions, so these are **not independent replications**.

The original index pilot also reported negative incremental DTT AUC: [NIFTY 50 2026 study](HISTORICAL_DTT_DIAGNOSTIC_2026_AUG_OCT.md). That study and this one examine related price-based constructs and cannot establish a useful psychological or behavioral trading model.

## Evidence boundaries

1. **No trading P&L or win-rate test.** No marketable bid/ask, actual next-bar fills, transaction fees, stamp duty, Goods and Services Tax, Securities Transaction Tax, slippage, broker costs, portfolio capital, or risk stops.
2. **Short, historical pilot:** just 12 days and two stocks; no liquidity-selection methodology or survivor-universe control.
3. **Third-party bars unaudited:** source code licenses are not equivalent to exchange market-data distribution permissions.
4. **No preregistered independent holdout:** this retrospective experiment followed an earlier negative result and used a related design; the last five days are chronological only.
5. **Incomplete real DTT thesis:** no actual pre-opening indicative prices, imbalance changes or order-book confirmations, and no observed investor intentions.
6. **Multiple comparisons / shared days:** the stock results are not independent significance tests. No p-values or certainty claims.
7. **Market state/volatility effects:** absolute movement may be mostly explained by recent volatility, and DTT's current signed switching mass may be too noisy.
8. **Prototype rule grid** at ₹10 increments is arbitrary; optimizing its width on this holdout would be overfitting.

## Reproducibility

- Input: the public third-party repository's original local file hierarchy (24 files).
- [Standalone offline reproducer](equity_dtt_feb2021_pilot.mjs) — Node.js 20+, no external packages and **no network or trading API**.
- Run: `node equity_dtt_feb2021_pilot.mjs /path/to/nse-intraday-data`.
- The reproducer records input file SHA-256 checksums and result metrics; the source GitHub blob identifiers for the retrieved files were observed during analysis. A repeat must independently compare source version and data integrity.
- **Execution provenance:** Numerical results were calculated in two in-session scripts after fetching these files from the GitHub connector. The checked-in standalone CLI reproducer was written to allow independent verification; **the committed CLI itself was not separately executed in this session**. Treat exact script reproduction as pending until it is run against saved copies.

## Decision

**DTT status: QUARANTINED as an unproven behavioral feature.** Do not promote into active trading or claim financial advantage. Focus next on correctness and net-of-cost baseline paper strategies with licensed, quality-controlled equity data, then evaluate entirely new preregistered behavioral features on later untouched sessions.

Maintain a NO-TRADE fallback and a deterministic risk controller. No autonomous real-money trading.
