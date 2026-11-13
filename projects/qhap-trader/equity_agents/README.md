# QHAP-TRADER — Corrected intent: Claude-style agents for NSE equity, not cryptocurrency

**13 November 2026.** User clarified: "I didn't mean literal crypto — I meant its style." They mean coordinated specialists that exchange evidence, debate alternatives, challenge assumptions, and obey independent risk controls in the existing **NSE cash-equity / Upstox QHAP project**. Literal crypto issue #80 is now CLOSED AS MISUNDERSTANDING; corrected equity research task is issue #81. The earlier crypto prototype is historical research-only, not the active development priority; do not connect crypto accounts or model services.

## Best money-making hypothesis to test, not a proven winner

For a ₹10,000 initial research account, I favor TESTING **low-turnover, unleveraged cash-equity / exchange-traded-fund swings over days to weeks**, rather than repeated minute-level RELIANCE transactions. The earlier real Upstox Jan 2025 and 84-day July 2022/23/24/25 minute replays show all FAST/ONE/TIME_MOMENTUM_GATE strategies lost after indicative costs; NO_TRADE won. This does NOT imply swing trading will work.

Upstox's 2026 published pricing matters: **equity delivery ₹20 brokerage per executed order** and **₹20 DP charge per scrip sold per day**, plus delivery STT 0.1% buy and sell, stamp/GST/exchange/SEBI and realistic spread/slippage. Equity intraday has different rates: min(₹20,0.1% of each executed order). On a tiny ₹2,500 delivery position, fixed brokerage/DP can absorb much of a small profitable price movement before taxes. Primary source: https://upstox.com/brokerage-charges/ . User's effective plan/contract-note charges are not independently verified. Eligible listed-equity STCG generally has a 20% Section 111A tax rate, subject to legal conditions, on realized gains; not an exchange fee. Official: https://www.incometaxindia.gov.in/w/capital-gain .

The 2024 SEBI study reported 71% of FY2022-23 individual cash-intraday traders lost money; trading more often is not evidence of a better chance: https://www.sebi.gov.in/media-and-notifications/press-releases/jul-2024/sebi-study-finds-that-7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses_84948.html .

The aim is independently replicated **after-all-costs, risk-adjusted positive expectancy**, not guaranteed monthly or daily cash income, fast compounding or excessive agents/indicators.

## What is implemented in this PR

[Original code: ../live_readiness/nse_swing_interdependent_agent_network.mjs](../live_readiness/nse_swing_interdependent_agent_network.mjs) is an OFFLINE deterministic nine-role **interdependent research decision graph**, not actual Claude paid model inference or an unattended market service. Only NSE_EQ keys and a local 80–260 DAILY bar research replay (or synthetic data) are allowed; no order routing or network.

              Private point-in-time daily-data integrity
                               |
           +-------------------+---------------------+
           |                   |                     |
      Trend researcher    Downside/gap critic   Liquidity/cash critic
           |                   |                     |
           +----------+--------+---------+-----------+
                      |                  |
                 News checker      Cost auditor
                 (unknown,          (hypothetical,
                 never invent)       no contract note)
                      |                  |
                      +-------> Adversarial skeptic
                                    |
                              Research coordinator
                                    |
                         NON-OVERRIDABLE RISK GUARDIAN
                                    |
                         WATCH/ABSTAIN -> NO_TRADE

Every node has evidence-family tags, references to its input dependencies, and a chained SHA-256 hash with an exported verifier. **One shared daily price stream is ONE correlated source, not independent confirmation from multiple analysts**. Risk guardian always vetoes paper and real order submission until actual licensed data, profitable after-cost edge, exchange/corporate-action checks, broker rights and explicit live authorization independently qualify. Printed result always has finalDecision NO_TRADE, zero paper and real orders, zero network/model calls and realOrderRoutePresent false. Positive trend may be a WATCH hypothesis only; no investment signal is generated.

News agent cannot invent earnings facts; cash agent checks whole-share feasibility under illustrative ₹2,500 position cap and daily liquidity proxy, not order book depth; fee agent receives user-provided estimate including sell DP charge, and notes contract-note verification is absent. SHA-256 is integrity checking, not a signed market-data attestation or evidence of profitable trading.

## Run offline (Node.js 22+)

From your Windows PowerShell Git clone:

    cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
    git pull --ff-only origin main

    node --test --test-reporter=tap .\projects\qhap-trader\live_readiness\test_nse_swing_interdependent_agent_network.mjs

    node .\projects\qhap-trader\live_readiness\nse_swing_interdependent_agent_network.mjs --synthetic-demo

This runs **only synthetic daily prices** and outputs a research audit, not a historical Upstox backtest.

Optional future user-local daily replay, AFTER actual permitted data preparation:

    node .\projects\qhap-trader\live_readiness\nse_swing_interdependent_agent_network.mjs --private-replay "C:\Users\Admin\QHAP-TRADER-PRIVATE\your-private-daily-evidence.json"

Private JSON fields: instrumentKey NSE_EQ|12charISIN, symbol uppercase, sourceClass PRIVATE_REPLAY, asOfDate YYYY-MM-DD; dailyBars array of 80–260 ordered objects {date,open,high,low,close,volume}; costAssumptions with estimatedBrokerageAndTaxesRoundTripRupees, slippageBpsPerSide, spreadRoundTripBps, uncertaintyReserveBps, sourceScheduleIndependentlyVerified boolean. The module does not yet convert minute data to daily bars, validate a complete exchange calendar or normalize corporate actions; NEVER invent missing bars. Keep private user-local sources out of GitHub and model prompts.

Our pre-existing three-provider separate research council already supports **independent model responses and one judge** in synthetic offline mode; its optional online OpenRouter mode costs money and requires distinct user approval and API key. A later workflow can provide that council with **public, sanitized, permitted** news/research briefs, never private licensed price data/keys or any order authority.

## Next phase requirements

1. Primary-sourced **cash delivery** Upstox fee model and effective-date tables, documented DP/taxes, actual billable account plan, gap/stamp/rounding, and a realistic small-capital transaction threshold. Not an intraday fee approximation.
2. Permitted corporate-action-adjusted NSE equity/ETF daily data, point-in-time universe/calendar/source audits. Use already inspected 84+5 days as DEVELOPMENT ONLY. Precommit distinct new hypothesis and untouched future periods before inspection, plus >=60 independent dates and >=3 independently verified regimes.
3. Real independent critique from optional Claude/GPT/Gemini model agents (manual paid opt-in, public-only evidence). Evaluate 1/3/5 versus deterministic benchmark with model cost/latency, multiple-testing penalties, forward-paper NO_TRADE and buy-and-hold.
4. Later isolated **paper portfolio engine** with next observable event, cash, realistic positions, partial fills, gap risk, restart reconciliation, corporate actions and reporting. This code currently DOES NOT execute or simulate any orders.
5. Live brokerage/exchange API review and individual explicit user approval after proven after-cost net edge; never deploy an LLM agreement as execution authority. No risk override.

QHAP-only project user rule: NO send/reply/forward/resend email without specific per-email prior approval, other projects' outreach workflows unaffected. Real orders remain **zero** and **disabled**.


## 2026-11-13 — Real 204-day chronological swing results: current WATCH failed

The user ran the already-merged cost-stressed, offline, chronological
daily replay against their private Upstox RELIANCE 204-bar source
(2024-01-01 through 2024-10-24; SHA256
472f6080a0b6ca8a253bd49231af420f708e2b4c0c0f834ef684c04fd578efe7).
Only sanitized aggregated outcomes were shared; 98 audited decisions while
flat, 5 WATCH-initiated hypothetical round trips, ZERO net winners.

At 1x/2x/3x assumed execution stress, nine-agent swing P&L was
−₹442.4580 / −₹478.9865 / −₹515.5149, passive same-position
−₹195.2920 / −₹201.9775 / −₹208.6631, NO_TRADE ₹0 in
all scenarios. At 1x gross was already −₹35 before ₹370.9324
public-Nov2026 fee-model charges and ₹36.5256 execution drag.
**Reject this specific WATCH rule as a live candidate.**
These remain 2024 DEVELOPMENT samples with 2026 public fee assumptions,
not date-correct actual account returns, and are NEVER an untouched holdout.

See [falsification report](../experiments/RELIANCE_UPSTOX_204DAY_SWING_DEVELOPMENT_FALSIFICATION_20261113.md)
and [sanitized evidence JSON](../experiments/evidence/RELIANCE_UPSTOX_204DAY_SWING_DEVELOPMENT_20261113.json).
The pure [development evidence reviewer](../live_readiness/review_daily_swing_development_evidence.mjs)
has mandatory NO_TRADE and cannot authorize broker orders, even for
a development win. Do not retune on these same bars to claim unseen gains.
