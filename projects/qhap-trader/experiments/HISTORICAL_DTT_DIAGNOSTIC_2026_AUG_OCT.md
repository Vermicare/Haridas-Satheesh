# DTT historical-data diagnostic — negative / inconclusive result

**Recorded:** 2026-11-03. **Status:** Exploratory, unverified independent data source. **Do not promote DTT to an active trading model.** This is a prediction-of-movement study, **not** a backtest of profitability.

## Research question

Does the initial Decision-Threshold Tomography (DTT) hypothetical policy-switching measure add information about large **future five-minute absolute price movement** beyond a simpler past-volatility baseline?

**Finding: No demonstrated improvement.** A fixed-weight combination slightly underperformed the baseline in the chronological October holdout.

## Data source and retrieval fingerprints

Source: https://github.com/technovusin/nifty50-historical-data — third-party one-minute **NIFTY 50 INDEX** candles, OHLCV, timestamps in India Standard Time. Not independently reconciled to official NSE market data. Index is not itself a cash equity one can purchase.

- August 2026: 7,875 bars, GitHub blob 2c4cd9a549faaa604c9dc64650241b25f561463c
- September 2026: 7,875 bars, GitHub blob 912de3a5c4ce8374a6463436597fe614e55832a3
- October 2026: 7,500 bars, GitHub blob b2791d11cf0ee89d57bbb33c9cb8f6dfcd969f14
- Overall: **23,250 one-minute index bars; 62 market sessions**. No session excluded or prediction window dropped for missing minutes in this sample.
- Raw third-party market data has **not** been redistributed. Check upstream exchange and data rights before republishing or commercial use.

## Methodology frozen for this diagnostic

At five-minute intervals from 09:35 to 14:40 IST, use known prices and time-correct historical VWAP to simulate **eight equal-weight hypothetical threshold policies**, NOT observed real traders. Four buy-above thresholds: opening-range high, previous ten-bar high, cumulative volume-weighted average price, upward round 50-point level. Four exit-below thresholds: opening-range low, previous ten-bar low, VWAP, downward round 50-point level.

Shock the observed close price by -20, -10, +10 and +20 basis points. **DTT** equals the fraction of the resulting 32 hypothetical policy decisions that switch state.

Baseline = sum of absolute past five one-minute close-to-close percentage changes in basis points + half the current bar high-low range in basis points.

Combined score = baseline standardized using training mean/standard deviation + 0.5 × DTT standardized using training mean/standard deviation. The 0.5 coefficient was illustrative, **not fitted or tuned**. Nothing here measures real trader intentions.

Outcome = future sum of absolute one-minute returns during the next five minutes. "Large movement" event threshold = **75th percentile of this future movement in August–September training data**, not a profit threshold.

Chronological split:
- Train/reference: August–September 2026; **42 sessions, 2,604 observations**.
- Holdout: October 2026; **20 sessions, 1,240 observations**.
- Day-block bootstrap: **500 seeded October day resamples** to evaluate combined-minus-baseline AUC uncertainty.

This experiment was not independently preregistered before the authors had seen some 2026 market context, so the holdout is chronological but **not certified untouched**.

## Actual observed results

| October holdout | Simple baseline | DTT only | Combined |
|---|---:|---:|---:|
| ROC AUC — large future *absolute* 5-minute movement | **0.6994** | 0.4560 | 0.6902 |
| Top-decile share classified as large movements | **94.35%** | 70.97% | **94.35%** |

- Training event threshold: **8.6973 basis points** (SUM of five future minute absolute changes; not a five-minute net return).
- October events exceeding that threshold: **71.61%**, compared with 25% by construction in the training reference. **Material apparent regime shift.**
- Combined minus baseline AUC: **−0.00924**.
- 500-sample day-block bootstrap 95% interval: **[−0.0210, +0.0031]**, includes zero.
- AUC is not probability of a winning trade. High event rates are not profit rates. The full DTT pre-market hypothesis was NOT tested since no pre-open snapshots were available.

## Key limits

1. No individual equity, broker executions, entry/exits, bid-ask spread, Indian taxes, slippage, market impact or 10,000-rupee account simulation. **Profitability is unknown**.
2. NIFTY 50 is a calculated index; supplied volume fields are unaudited and do not represent an investable order book.
3. No actual trader psychology or private orders were measured. The DTT population consists of fictional rules.
4. Only three months and 20 held-out days; no other regime/multiple-security validation.
5. No separate placebo policy ensemble, matched-capacity multivariable control or independently untouched prospective sample in this pilot.
6. October regime shift limits transportability; within-day serial dependence remains despite using five-minute nonoverlapping windows and day-level resampling.

## Reproduce locally without data redistribution

Download the three original month CSVs only through authorized means. Run the research-only, local Node.js script:

~~~sh
node dtt_2026_index_replay.mjs NIFTY50_1min_2026-08.csv NIFTY50_1min_2026-09.csv NIFTY50_1min_2026-10.csv
~~~

See [reproducer](dtt_2026_index_replay.mjs). It has no broker or network connectivity. Its input hashes and output metrics should be recorded on each run.

## Decision and follow-up

**Verdict: FAIL to demonstrate incremental predictive value.** Preserve this negative result. Next, obtain verified licensed minute bars for actual shares plus separate pre-open/order-flow information if permitted. Freeze hypotheses before subsequent test periods, challenge against ordinary volatility/liquidity/time controls and threshold-randomization placebos, and evaluate **net-of-cost paper trading** only after data and simulation correctness pass.

Do not make public profitability or world-first claims from this experiment.
