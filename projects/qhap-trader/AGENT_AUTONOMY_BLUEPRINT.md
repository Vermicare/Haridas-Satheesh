# QHAP-TRADER 2.0 — Autonomous Intraday Research and Behavioral-Microstructure Blueprint

**Date:** 2026-11-03  
**Status:** Architecture / Research Program. Not a deployed agent network or a verified profitable trading strategy.  
**Execution boundary:** ₹10,000 **simulated** long-only, cash-equity paper trading; **no broker**, no real orders, no leverage, no automatic live-trading promotion.

## Research thesis

Instead of asking "what price will the next candle reach?", ask:

> Which observable crowd-behavior hypotheses are plausible before the market opens, what would confirm or falsify them after the open, and is there enough *net-of-friction* evidence to justify a trade instead of waiting or abstaining?

The point is not to claim we know the mental states or private orders of other investors. Crowd psychology must be treated as a **noisy, testable inference** from legally obtained observable market and information signals.

Features and hypotheses below are proposed for research; they have not demonstrated Indian intraday predictive power. Multiple agents can increase false discovery and correlated errors unless they use genuinely different inputs/hypotheses and a common rigorous testing standard.

## Before the market opens: hypotheses, not predictions

### Previous evening
- Frozen permitted universe, corporate calendar, results, announcements and relevant global factors.
- Historical volatility, overnight gap distributions, prior close and prior liquidity; all strictly timestamped.
- Pre-register up to a small number of *conditional plans* (e.g., strong gap + failed opening range -> do nothing or test reversal; sustained breakout + liquid confirmation -> candidate continuation).
- Timestamp and archive plans **before** seeing the market open. Compare with a no-plan baseline.

### 08:00–09:00 IST
- Check for event/news changes, exchange holidays, corporate actions, unusual risk.
- Produce a ranked **watchlist, not orders**.
- Distinguish public signals from speculation. Language-model summaries may contain errors or stale information; link to primary timestamps.

### 09:00–09:15 IST: actual pre-open session
- When licensed data is available, observe indicative equilibrium price / quantity and subsequent final discovery, changes in indicative imbalance, gap vs prior close and unusual attention. Snapshots may be tentative, not executed final flow.
- Evaluate possible "expectation versus opening reality" gaps.
- The NSE's 2026 pre-open process has evolving order-entry restrictions and a system-driven random closure; never treat pre-open indications as guaranteed fills.

### 09:15–09:25 IST
- No new strategy entries in the initial policy; observe actual volume, direction, opening-range behavior and volatility.
- Distinguish continuation, reversal and ambiguous conditions. In ambiguous or low-quality states, abstain.

### 09:25–14:45 / 14:45–15:00 IST
- Compare conditions against frozen conditional plans.
- Size simulated long-only trades within independent cash, position and loss rules.
- No entries after 14:45; intended flat by 15:00, with explicit exception if realistic exit cannot be simulated.
- The initial cutoff is stricter than the exchange trading window and avoids the 2026 Closing Auction Session for eligible stocks.

## Behavioral hypotheses to falsify

| Hypothesis | Observable proxy | Alternative explanation / caution |
|---|---|---|
| Attention-driven chase | News bursts + unusual volume + unusually positive returns | Event fundamentals, institutional buying, misleading sources |
| Crowd anchoring | Failure to sustain a prior close, round price or day high | Market-maker inventory, liquidity migration |
| Panic / stop clustering | Rapid downside acceleration, high volume, volatility expansion | Genuine negative information; **no actual stop book visibility** |
| Herd persistence | Synchronized index/sector/constituent momentum | Broad macro shock; hindsight constituent selection |
| Failed breakout / trapped chase | Opening range breakout then prompt failure on confirmed bars | Ordinary noise; no inference of individual traders' P&L |
| Post-news disagreement | High volume, whipsaw and widening spread | Price discovery under uncertainty |
| Time-of-day effects | Opening/midday/close differences in volatility and participation | Seasonal biases; changing market structure |

**Research caution:** these are hypotheses, not causal psychological labels. Without account-level data, the system cannot identify traders' motives or positions. Strong apparent relationships may vanish out of sample.

## Agent architecture (separation of duties)

1. **Research Planner** (evening and morning): converts verified public information into timestamped conditional hypotheses and a watchlist.
2. **Behavior Analyst** (during session): maintains time-correct attention / reversal / volatility-regime features with uncertainty; can publish *proposals* only.
3. **Strategy Challengers**: separate opening-range, VWAP reversion and trend candidates, plus a rule-only control; no implicit permission to trade.
4. **Counterfactual Skeptic**: examines trade, wait, do-nothing alternatives using one frozen execution policy and pessimistic costs.
5. **Execution & Cost Simulator**: immutable paper-only order interface; next-bar or event-driven simulated fills with spread, uncertainty, charges and non-fills.
6. **Risk Guardian** (**non-LLM deterministic service**): enforces allowed instruments, sessions, size, cash, risk stops, stale-data veto and kill switch; veto is not overrideable by other agents.
7. **Monitoring / Incident Agent**: supervises heartbeat, time drift, feed freshness, exceptions, incomplete fills, and generates alerts; it cannot promote a failed day to PASS.
8. **Audit and Experiment Agent** (after market): immutable decision ledger and comparison across frozen variants, including rejected trades; recommends experiments for offline review.
9. **Release Gate** (**non-LLM**): no model promotion during an ongoing session. Versioned human acceptance plus independent validation is required; **live execution remains absent**.

These are **logical responsibilities**; they do not require nine paid language-model APIs or nine competing chatbots. A single Python application with isolated modules, a small deterministic state machine and one optional LLM research service is the recommended first implementation.

## Suggested software architecture

```text
  AUTHORIZED TIMESTAMPED DATA (CSV/replay first)
                |
      provenance & session gate
                |
      pre-market hypothesis store
                |
       deterministic feature engine
                |
    regime / psychology proxy modules
                |
       independent strategy tests
                |
  counterfactual + transaction-cost challenger
                |
      deterministic RISK GUARDIAN
             /          \
         reject        paper order
             \          /
      immutable decision/event ledger
                |
      reconciler + independent watchdog
                |
        daily audit and alerts

  LLM RESEARCH SIDE-CAR (optional):
      summarize data, propose hypotheses, explain failures
      NO credentials, no live order API, no risk-override path
```

**Fail-closed design:** disconnected data, stale timestamps, unexpected exchange sessions, system crashes, corrupted state, mismatched account reconciliation, or absent scheduled closing data cause a halt and prominent alert. A watchdog can detect failure but cannot guarantee real-world exits during network or broker outages.

## Unattended operation model

- Application runs as a standalone, restarted service on a suitable always-on computer or cloud instance; hardware selection occurs only after data and compute needs are measured.
- A local Raspberry Pi 5 can host research and paper operations if a reliable legal data source, persistent storage, backups, monitored connectivity and clock sync are available. A Pi is not inherently a reliable live trade-execution environment.
- Before each session: version-pin data rules, strategy weights, universe and risk parameters; run preflight checks. If not all PASS -> remain paper NO-TRADE.
- During session: deterministic service handles seconds/minutes; watchdog runs independently and sends only material incidents.
- End of session: immutable event log, simulated P&L, rejected-candidate audit and daily report.
- Human role in paper mode: review alerts and periodic quality reports, **not** manual monitoring of each simulated tick. Strategy changes apply at a later session after verification.

A ChatGPT conversation or periodic ChatGPT automation is **not** a low-latency, continuous market feed, broker order router, or substitute for process supervision.

## Evaluation: do not optimize win percentage in isolation

Primary: out-of-sample **net expected return per unit of risk**, sensible drawdown and tail-loss constraints. Secondary: win rate, profit factor, average win/average loss, downside volatility, turnover, opportunity cost, fill realism and trade count. Compare with transparent rule-only baselines and NO TRADE.

Tests must include:
- Leakage and look-ahead (including date-aware news timestamps and cross-sectional normalization);
- Survivorship / selection bias, data provider changes and market halts;
- Pre-registered time-split and purged evaluations, multiple-testing corrections, untouched holdout;
- Brokerage/Indian statutory fees and taxes at audited effective schedules; stress at 2x;
- Disconnections, stale feed, exchange calendar changes, partial fills, missed exits;
- Statistical confidence in psychology proxies, ablation tests of each module;
- At least **60 prospective paper sessions**, with additional observations if uncertainty remains high.

### Staged implementation

**S0 — Now (documentation):** research hypothesis registry, architecture, hard paper-only boundary, source contracts.

**S1 — First executable:** deterministic single-instrument CSV replay, test-only baseline, local event ledger, integrity checks. This is *software correctness evidence*, not a market result.

**S2 — Historical realism:** authorized quality intraday dataset, fees and slippage, time-correct cross-security features, validated benchmark engine.

**S3 — Agent and psychology experiments:** independent features, opponent/rejected-alternative ledger, shadow challengers; compare against S2.

**S4 — Unattended *paper* service:** scheduled start/stop, recovery state machine, watchdog, exceptions and report. No broker order interface.

**S5 — Live feasibility review only:** separate request and explicit approval, current SEBI/NSE framework, compliant broker/data licensing, independent controls. **Not authorized and not automatically enabled by preceding gates.**

## Feasibility limits

- ₹10,000 unleveraged cash equity may be too small for frequent day trading once costs and integer share sizes are considered. **No profit frequency or positive edge is assumed**.
- No AI can know other traders' intentions directly from price bars; research uses weak proxies.
- More agents do not imply better financial performance. Costs, evidence and veto authority matter more than agent count.
- The system should be able to automatically decide **not** to trade most sessions if evidence is insufficient.
- Avoid F&O, leverage, short selling, doubling down and promised daily payouts in the initial project.

## Evidence and policy references

- NSE pre-open session: https://www.nseindia.com/static/products-services/equity-market-pre-open
- NSE Closing Auction Session: https://www.nseindia.com/static/products-services/closing-auction-session
- NSE data licensing and policy: https://www.nseindia.com/static/market-data/nse-data-policy
- NSE paid real-time data products: https://www.nseindia.com/static/market-data/real-time-data-subscription
- NSE retail algo operational framework: https://www.nseindia.com/static/trade/empanelled-algo-providers-exchange
- SEBI retail algorithmic-trading circular: https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html
- SEBI retail cash intraday study: https://www.sebi.gov.in/reports-and-statistics/research/jul-2024/study-analysis-of-intraday-trading-by-individuals-in-equity-cash-segment_84946.html
- Barber & Odean (2008), *All That Glitters*: https://doi.org/10.1093/RFS/HHM079
- Barber & Odean (2013), *The Behavior of Individual Investors*: https://doi.org/10.1016/B978-0-44-459406-8.00022-6
- Bailey & López de Prado, *Deflated Sharpe Ratio*: https://doi.org/10.3905/jpm.2014.40.5.094
