# QHAP-TRADER — Research Design and AI Differentiation

**As of:** 2026-11-03  
**Maturity:** hypothesis and specification, not implementation or demonstrated trading edge.

## The main invention candidate: Counterfactual Abstention Engine (CAE)

**Goal:** estimate whether a candidate trade is *worth executing after realistic costs*, whether to wait for better liquidity/information, or whether to do nothing. A forecast of next-bar direction is not enough.

For candidate action `a`, define an exploratory decision score:

```text
score(a, state) =
  lower-confidence-bound(estimated gross payoff | available state)
  - conservative total execution costs(a)
  - model/regime uncertainty penalty(a)

Choose TRADE only when:
  (1) score(TRADE) > max(score(WAIT), score(NO_TRADE)) by a
      preregistered threshold,
  (2) the independent risk & data gates all pass,
  (3) the signal belongs to a prospectively validated regime.

Otherwise choose WAIT or NO_TRADE.
```

This is a **design objective**, not a calibrated probability estimate. WAIT must be defined with a precommitted re-evaluation horizon. NO_TRADE has no exposure and a baseline return of zero before opportunity cost. Unobserved market impact and fill uncertainty must remain explicit. Confidence intervals can be severely unreliable under sparse, dependent intraday observations; no statistical certainty is implied.

### The Decision Ledger (core differentiator)

Every candidate, including ones rejected, records before any future prices arrive:

- Timestamp (IST plus UTC), source, market session and security master revision.
- Market-state fingerprint, feature data-cutoff, eligible universe and liquidity data.
- Proposed direction, quantity, horizon, stop/target, expected edge and cost distribution.
- Strategy/model version, uncertainty, score of TRADE/WAIT/NO_TRADE.
- Risk-gate result, final chosen action and machine-readable rejection reason.
- Hash of immutable experiment configuration and data snapshot identifiers.

**After** the horizon ends, attach outcomes from the historically possible alternatives using one predeclared replay/fill policy. The ledger must never retroactively revise its own prediction. The counterfactual outcome is a *simulated alternative*, not proof of what a broker would have filled.

### Four distinct intelligence modules

| Module | Job | Auditable failure mode |
|---|---|---|
| Regime Fingerprint | Determine whether current state resembles training evidence | Out-of-distribution, stale or inconsistent state → abstain |
| Challenger Council | Compare opening-range breakout, VWAP reversion, intraday momentum and optional ML | No consistently better net result than transparent baselines → retire AI |
| Execution Skeptic | Stress-test participation, spread/slippage, latency, fees, order type and plausible non-fills | Edge disappears at realistic friction → reject |
| Counterfactual Auditor | Replay rejected and selected opportunities under frozen rules | Hindsight leakage, multiple testing, unstable parameters → quarantine experiment |

Language models may summarize anomalies, research hypotheses and create session reports; they do **not** directly place orders or alter risk limits.

## Preregistered hypothesis tracks

**H0 — No trade (control).** Many periods have no defensible edge. Fewer trades may improve *net* results by lowering costs, but this is unproven.

**H1 — Baseline opening-range breakout.** Test a fixed first-15-minute range using after-range signals and next-bar fills, with volatility/liquidity filters. Compare against an unfilted rule. Avoid trading during the initial observation window.

**H2 — VWAP reversion, regime conditional.** On selected non-trending liquid sessions, test deviations from a causally computed VWAP using only known bars. Evaluate failure during persistent trends.

**H3 — Continuation after index confirmation.** Use contemporaneously available index and constituent moves, time-of-day and liquidity constraints. Reject if effect disappears under delayed execution.

**H4 — Selective abstention.** Add a train-only rejection or uncertainty model atop the best baseline. Verify whether rejects help *out of sample* without just reducing sample size to a lucky few trades. Compare trade count, net profit per candidate, opportunity cost, and worst-day loss.

**H5 — Regime drift sentinel.** Detect changes in calibrated error and feature distributions; suppress rather than auto-retrain during the session. Daily review determines whether further experiment is justified.

These hypotheses are **to be tested, not asserted as profitable**. Track all unsuccessful variants to avoid reporting only the winning ones.

## Realistic data and simulator contracts

- Use contractually permitted historical **intraday** quotes/trades or 1-minute bars with correct adjustment policy, corporate actions, symbol changes, market-calendar and session labels; keep provenance, license and timestamps.
- An end-of-day-only dataset **cannot** validate a minute-level intraday strategy. Synthetic datasets are for software tests, **not** evidence of market profitability.
- For 1-minute closed-bar signals, fill no earlier than the next available bar, with pessimistic gap and stop/target ordering; unknown within-bar sequence should resolve against the strategy or be interval-bounded.
- Evaluate spread, brokerage, exchange fees, Securities Transaction Tax, regulatory fees, stamp duty, Goods and Services Tax, order rejection, slippage, partially filled orders and latency. **Broker is not selected; cost parameters are placeholders pending actual brokerage and applicable statutory schedules.**
- Avoid look-ahead, future constituent selection, leakage from same-day normalization, market-session mixing, survivorship bias and unauthorized data acquisition.
- Support deterministic replay with seeded synthetic tests for code correctness, then licensed real historical replay for market evidence.

## Evidence protocol

1. Freeze research questions, selected instruments and fee assumptions before opening the final evaluation window.
2. Split strictly by trade date and chronology; retain an untouched chronological holdout. Where labels overlap, use an appropriate purge/embargo based on the maximum target horizon.
3. Walk-forward re-train only on previously available days; compare rule-only vs AI and with-vs-without abstention using the **same** opportunities and fill model.
4. Log the complete strategy search and compute multiple-comparison-aware metrics where sample sizes permit (e.g., deflated Sharpe / probability of backtest overfitting as *diagnostics*, not magic certifications).
5. Stress fees at base and 2x; latency and partial fills; top-winner removal; low-liquidity and abrupt-volatility periods; randomized execution pessimism.
6. Examine gross and net returns, turnover, win/loss distribution, expected shortfall, maximum drawdown, exposure time, number of rejected signals, calibration by regime and out-of-sample confidence intervals.
7. Use **at least 60 forward paper sessions** after frozen strategy selection. A minimum duration is not sufficient proof if sample size is inadequate.
8. Only claim an observed edge when robust to realistic costs, a suitable simple-strategy comparator, and adverse perturbations. Publish the null result if not.

**Null result handling:** reject an AI feature if complexity, costs, false positives or drawdown worsen forward results; maintain the stable rule baseline or no-trade outcome.

## What would make this intellectually differentiated?

The output is not merely a signal. It is a **versioned, falsifiable decision with a rejected-alternatives record**, a verified trading-clock boundary and a measured uncertainty budget. The aim is to learn when a trading model *should not act*. These are established research ingredients combined into a disciplined architecture; no proprietary discovery or market advantage has yet been demonstrated.

## Initial implementation packages (proposed, not created)

```text
qhap_trader/
  data/                 # provenance and calendar normalization
  replay/               # deterministic event and fee ledger
  strategies/           # transparent rule baselines
  regime/               # optional statistical/ML challengers
  counterfactual/       # rejected-alternative evaluation
  risk/                 # independent veto, no broker imports
  reporting/            # evidence tables and validation reports
tests/                  # leak checks, fill ordering, risk-stop cases
```

## References

- NSE trading session and Closing Auction Session: https://www.nseindia.com/static/products-services/closing-auction-session
- NSE historical data licensing: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- NSE real-time market data: https://www.nseindia.com/static/market-data/real-time-data-subscription
- SEBI intraday trader loss study: https://www.sebi.gov.in/media-and-notifications/press-releases/jul-2024/sebi-study-finds-that-7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses_84948.html
- Bailey & López de Prado, *Deflated Sharpe Ratio*: https://doi.org/10.2139/ssrn.2460551
- Bailey et al., *Probability of Backtest Overfitting*: https://scholarworks.wmich.edu/math_pubs/42/
