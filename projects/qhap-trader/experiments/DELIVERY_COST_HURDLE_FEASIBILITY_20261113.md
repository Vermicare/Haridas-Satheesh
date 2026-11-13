# QHAP-TRADER — Fixed tiny-delivery-order cost hurdle (13 November 2026)

**Research-only, no orders, no price forecast, no strategy win.** This is a predefined arithmetic screening exercise after the user's 204-day RELIANCE swing development replay lost money on five hypothetical trades. It does not change or optimize that rejected strategy, reuse its inspected price bars, or claim independent trading edge.

## Why this experiment

The user limits a single position's **total buy cash cost, including indicative fees, to ₹2,500** within ₹10,000 simulated initial capital. Standard delivery orders have important fixed brokerage, demat sell-day charges and GST. Hence a strategy can have positive gross price movement yet fail economically after costs. Verify the economic hurdle first; do not respond by increasing allowed risk.

## Fixed grid and formula

Run from repository root with Node 22+: `node projects/qhap-trader/live_readiness/equity_delivery_cost_hurdle.mjs`. Optional test: `node --test projects/qhap-trader/live_readiness/test_equity_delivery_cost_hurdle.mjs`.

The price references ₹250, ₹500, ₹1,000, ₹1,500, ₹2,000, ₹2,500 are **abstract synthetic share prices**, NOT RELIANCE market quotes. The function purchases a whole number of shares, requiring `quantity × modeled adverse buy fill + indicative buy charges <= ₹2,500`, then solves for the next hypothetical raw sell-open reference at which net proceeds after modeled adverse sell fill and delivery charges just cover total buy outlay. One executed buy order and one sell order are assumed; split fills, dividends, tax implications, price limits, market impact, and corporate actions are not certified. Friction 1×, 2×, 3× uses the repository's existing `hypotheticalNextOpenExecution` assumptions; no calibration uses historical samples.

| Synthetic share price | Whole shares at 1× | Break-even future raw price rise at 1× | At 2× | At 3× |
|---:|---:|---:|---:|---:|
| ₹250 | 9 | 3.8624% | 4.3546% | 4.8491% |
| ₹500 | 4 | 4.2571% | 4.7502% | 5.2457% |
| ₹1,000 | 2 | 4.2571% | 4.7502% | 5.2457% |
| ₹1,500 | 1 | 5.4412% | 5.9371% | 6.4355% |
| ₹2,000 | 1 | 4.2571% | 4.7502% | 5.2457% |
| ₹2,500 | 0 | Unaffordable | Unaffordable | Unaffordable |

**Fees caveat:** References the [Upstox public charge table](https://upstox.com/brokerage-charges/) and the repository's existing `indicativeDeliverySideFees` **as of November 2026**, NOT exact 2024 tariffs, any personal Upstox subscription/contract note, or audited charges. ₹2,500 reference price is unaffordable when one share plus purchase fees exceeds the ₹2,500 total budget. Economic break-even is not a trade target or a probability statement.

## What this does not resolve

- The inspected 204-day 2024 RELIANCE sample is still **development, not independent holdout**. Five hypothetical losing trades mean the existing agent WATCH is rejected.
- Regulatory eligibility, source rights, independent corporate actions, exact historical costs, account-dependent fees, executable fills and net strategy advantage are not verified.
- The module provides **no connection to Upstox**, broker credentials, trading endpoints, model calls, or network requests. Mandatory `NO_TRADE` remains unchanged.
- A cost-feasible hypothetical trade is not a profitable predictive strategy. Future candidates require a **frozen rule written before genuinely unseen data**, separate multi-regime evaluation, adequate sample uncertainty assessment, permission for data use, and independent review.

**Next gate:** identify a frozen economic design with target movement plausibly above the modeled after-cost threshold **before** an untouched historical or forward observation is inspected. Do not fit to the 204 known dates. No real money and no auto-promotion.
