# QHAP-TRADER — Paper Risk Contract & Validation Gates

**Version:** initial research specification, 2026-11-03  
**Status:** Proposed settings; not implemented, connected, certified or backtested.  
**Control principle:** safety/market-data/risk checks run independently of AI. Failure defaults to **NO TRADE**.

## Proposed paper account

| Constraint | Research default | Mandatory meaning |
|---|---:|---|
| Initial simulated equity | ₹10,000 | No transfer/deposit or real order |
| Largest single position | ₹2,000 | Gross unleveraged purchase value |
| Simultaneous positions | 3 | At most ₹6,000 gross exposure |
| Minimum uncommitted cash | ₹4,000 | Reserve applies before each paper fill including fees |
| Budgeted loss per trade | ₹50 | Size using stop distance and estimated slippage/fees |
| Daily mark-to-market loss lock | ₹100 | Once reached, no new entries for remaining session |
| Weekly mark-to-market loss lock | ₹300 | Once reached, no new entries for rest of trading week |
| Peak-to-trough simulated equity drawdown lock | ₹800 | Stop strategy until explicit review |
| Leverage, shorts, derivatives, overnight | 0 | Long-only cash at inception |

The loss figures are **decision/lock thresholds, not guaranteed worst-case losses**: gaps, illiquidity, outages and fees can exceed intended stops even in real execution. Paper fills must simulate these hazards rather than assume guaranteed exit prices. Risk controls should consider realized and unrealized P&L plus costs; clocks and cap resets must be unambiguous.

## Intraday session control — IST

- Exchange trading calendar is authoritative. No trading on a holiday, suspended instrument or special session unless separately tested.
- 09:15–09:25: observations only; no strategy entries.
- 09:25–14:45: permitted paper entry window when all gates pass.
- After 14:45: no fresh entries.
- By 15:00: mark all positions flat in the paper ledger under conservative exit assumptions. Any unresolved exit or unrealistic price is a **simulation failure**, not an assumed successful square-off.
- NSE's 2026 Closing Auction Session applies to cash stocks with derivatives; continuous trading ends at 15:15 for such symbols. Our earlier 15:00 cutoff is a research safety margin, not an NSE requirement. Confirm instrument/session membership daily.
- Broker-specific compulsory square-off deadlines would be a separate future constraint; **no broker is configured**.

## Pre-decision gate order

1. **System health:** approved paper mode only, reproducible configuration, UTC/IST clock agreement, valid calendar, no replay gap or clock skew.
2. **Instrument quality:** eligible symbol, no halt, verified price and adjusted/unadjusted convention, acceptable liquidity and bid/ask proxy.
3. **Model quality:** data timestamp precedes decision; regime in-domain; recent calibration/drift monitors healthy; no prompt injection from untrusted news/text.
4. **Economic quality:** estimated *net* edge remains positive at conservative friction and 2× friction sensitivity; freeze assumptions before evaluation.
5. **Position/risk:** all sizing and loss locks pass. Risk sizing uses expected stop loss **plus** slippage, fees and adverse gap reserve; never use predicted win probability to bypass limits.
6. **Schedule:** entry inside window; remaining time supports intended holding horizon and conservative exit before 15:00.
7. **Paper execution only:** send to mock interface. No module exports a live broker submit action.

All rejection causes should be persisted, including model uncertainty and unavailable data. No emergency "force trade" command; only explicit human-approved configuration revision with an audit trail.

## Required tests before any claims

- Missing/stale bar, duplicated timestamp, daylight/timezone edge and symbol halt → **no trade**.
- Target reached and stop reached inside same 1-minute bar → unfavorable fill or bounded uncertainty, never optimistic automatic profit.
- Signal from bar at 10:30 → earliest order simulation after that bar is complete.
- Fee / spread stress flips expected edge → abstain.
- Daily or weekly loss lock, drawdown lock, reserve breach, overlapping positions, out-of-hours entry → reject.
- 15:00 exit failure, data-provider outage, partial fill, rejected order → visible exception and halt.
- Same pinned history and config → identical deterministically replayed outcomes.
- Controlled deliberately leaky feature → test suite must detect or reject leakage.
- AI produces malformed or overconfident action → deterministic risk gate vetoes it.

## Promotion criteria (research only)

**G0 — Architecture:** docs, risk spec, legal/data source review. **Current stage.**

**G1 — Correctness:** deterministic test suite passing, complete event ledger, instrument/session rules and fee engine independently checked.

**G2 — Historical evidence:** sufficiently long authorized intraday history across regimes, preregistered comparisons, strictly out-of-sample net-of-cost performance and robustness to 2× modeled costs. No promotion based on synthetic-market returns.

**G3 — Forward paper:** at least 60 observed trading sessions with frozen version, full rejected-signal ledger, no unexplained data or risk failures, a documented independent review, and sufficient trades to meaningfully assess uncertainty. Sixty sessions alone are not statistical proof.

**G4 — External readiness decision:** only after separate written authorization, broker selection, current SEBI/NSE retail algo framework review, permission/registration requirements (as applicable), approved API and licensed data verification. Even passing G4 would **not** activate live orders automatically.

**Any failed gate → remain in paper/no-trade mode.**

## Explicit non-goals

- No daily-profit target or promised bank-account credit.
- No grid/martingale loss recovery, uncontrolled averaging down, derivatives or borrowed funds.
- No API key storage, credential handling, exchange/broker rule workarounds or hidden live-order path.
- No use of LLM-generated text as a substitute for market data, transaction records or compliance review.

## Relevant official sources

- SEBI February 2025 retail algorithmic trading framework: https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html
- SEBI September 2025 implementation timeline extension: https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html
- NSE algorithmic-trading procedures: https://www.nseindia.com/static/trade/empanelled-algo-providers-exchange
- NSE cash-stock Closing Auction Session: https://www.nseindia.com/static/products-services/closing-auction-session
