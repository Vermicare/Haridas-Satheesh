# QHAP-TRADER — Counterfactual Intraday Trading Intelligence

**Status:** Research Program / Architecture — documentation only (2026-11-03)  
**Market:** Indian equities, NSE cash segment; liquid unleveraged long-only instruments at inception  
**Account:** ₹10,000 **simulated**, zero live capital deployed  
**Broker:** none; no order-routing connection  
**Mode:** offline historical replay → forward paper trading → external review. **Live execution is disabled.**

> **Research question:** Can an evidence-gated intraday decision engine identify and skip low-quality trades, and generate a repeatable **net-of-cost** advantage over simple rules and no-trade alternatives on genuinely unseen market days?

This is **not** a promise of daily income, an operating bot, an approved trading algorithm, or a verified profitable strategy. No historical intraday market-data corpus, running backtest, trained model, or forward-paper ledger has been verified for this project yet.

## Why this is different from another "AI predicts the next candle" bot

QHAP-TRADER is designed around **selective abstention** and **counterfactual auditing**, not a standalone buy/sell prediction:

1. **Market-state fingerprint:** describe current volatility, trend, liquidity, spread, time-of-day, index co-movement and news/event uncertainty using only information available at the decision timestamp. Unknown or out-of-distribution state is a reason to abstain.
2. **Independent strategy challengers:** compare simple opening-range, VWAP/mean-reversion and trend-continuation baselines with an optional calibrated machine-learning model. An AI layer earns promotion only by improving prospective net results over simpler models.
3. **Counterfactual Decision Ledger (CDL):** persist the frozen pre-trade decision and its alternatives: trade, wait, do nothing. Later replay both taken and rejected signals using the same feasible execution assumptions. Do not claim unknowable real-world counterfactual fills or causal effects.
4. **Execution-aware edge filter:** no position if conservative modeled spread, slippage, fees and uncertainty erase the hypothetical edge. Measure returns **after** all trading costs; rerun at double modeled friction.
5. **Independent safety controller:** hard limits overrule predictions and can stop the system. An explanation from AI is not trading authorization.
6. **Evidence-first promotion:** log every experimental variant, monitor regime drift, use untouched time-split holdouts, and publish failed as well as successful tests. Avoid selecting the best historical equity curve from repeated attempts.

**Claimed novelty boundary:** this is our proposed *combination* and engineering emphasis, not a claim that abstention, ensembles, counterfactual analysis, or execution-aware trading were invented here or that they confer an edge.

## In-scope / out-of-scope

| Initially in scope | Explicitly out of scope |
|---|---|
| NSE cash-equity intraday study; highly liquid shares and only liquid ETFs | Futures, options, crypto, leveraged positions |
| Long-only simulated orders; intraday flat by design | Short selling or overnight positions |
| Time-correct 1-minute bars with provenance; finer book data only when licensed | Unlicensed data scraping, synthetic prices presented as real |
| Deterministic backtest and forward paper execution | Broker authentication, API order submission, unattended real-money trading |
| Calibration, regime detection and rejection logs | LLM forecasts treated as authoritative trade signals |

## Decision loop

```text
Licensed historical / permitted delayed market data
  -> data-provenance & freshness gate
  -> market-state / regime fingerprint
  -> baseline strategy candidates + optional AI challengers
  -> expected net edge & uncertainty bounds
  -> counterfactual trade / wait / abstain comparison
  -> INDEPENDENT hard risk gate
      -> REJECT and record reasons
      -> or PAPER ORDER SIMULATOR
  -> execution/fee ledger + mark-to-market
  -> post-session outcome audit / frozen experiment registry
```

"Wait" and "no trade" are first-class, measurable outcomes. No pathway from this design to a broker's live order API exists in the initial architecture.

## Market clock (Asia/Kolkata)

NSE cash continuous trading normally begins at **09:15 IST**. In 2026, the NSE Closing Auction Session applies to cash equities on which derivatives are available; their continuous phase ends at **15:15**, while non-CAS cash securities normally continue to **15:30**. Instrument-specific sessions and holidays must come from the exchange calendar.

**Conservative research policy, not an exchange rule:** skip 09:15–09:25 opening noise; permit new paper entries **09:25–14:45**; require flat simulated positions by **15:00**; never carry overnight. Exchange sessions and broker square-off deadlines are distinct, so reassess this schedule before considering any broker.

## Project documents

- [Behavioral microstructure, pre-market agents and autonomous paper operation](AGENT_AUTONOMY_BLUEPRINT.md)
- [Research invention proposal: Decision-Threshold Tomography (DTT)](INVENTION_DECISION_THRESHOLD_TOMOGRAPHY.md)

- [Offline paper replay prototype and five synthetic safety tests](prototype/README.md)
- [Design, hypotheses and differentiated AI research](DESIGN_AND_RESEARCH.md)
- [Risk contract, replay quality and release gates](RISK_AND_VALIDATION.md)
- [Main portfolio index](../../PROJECT_INDEX.md)

## Work sequence

1. Confirm authorized data supply, instrument universe, corporate-action handling and survivorship-free history.
2. Build a versioned, deterministic replay simulator with explicit fill and fee assumptions.
3. Run rule-only baselines and no-trade comparator **before** adding AI.
4. Implement decision-ledger abstention and conservative execution uncertainty.
5. Add optional calibrated regime / rejection models as measured challengers.
6. Perform time-purged, forward-only evaluation, stress fees and liquidity, and keep an untouched holdout.
7. Collect **at least 60 complete forward paper-market sessions** with frozen versions, then independently inspect failures.
8. Only after documented evidence, separately evaluate compliance, broker rules and any future authorization. **There is no pre-approved live phase.**

## Regulatory & data boundaries

India's retail algorithmic-trading framework and NSE member / client-direct-API implementation requirements apply to any future retail automated order execution. A future broker integration must be broker-supported and independently checked against current SEBI, NSE and broker requirements; do not bypass API controls, algorithm approval or data-vendor rights. This repository contains no credentials.

**Background / primary references (checked November 2026):**
- SEBI's intraday cash-equity loss study: https://www.sebi.gov.in/media-and-notifications/press-releases/jul-2024/sebi-study-finds-that-7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses_84948.html
- NSE Closing Auction Session: https://www.nseindia.com/static/products-services/closing-auction-session
- NSE retail algorithmic-trading arrangements: https://www.nseindia.com/static/trade/empanelled-algo-providers-exchange
- NSE historical market-data products: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- Bailey & López de Prado, Deflated Sharpe Ratio: https://doi.org/10.2139/ssrn.2460551

**Evidence claim:** design established; **strategy performance and implementation remain unverified**.
