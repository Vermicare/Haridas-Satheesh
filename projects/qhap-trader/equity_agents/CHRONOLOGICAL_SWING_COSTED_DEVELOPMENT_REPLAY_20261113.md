# QHAP NSE chronological development replay — 204 historical daily bars

**13 November 2026.** User independently completed one read-only Upstox Historical Candle V3 daily download for RELIANCE 2024-01-01 through 2024-10-24, stored **204 daily candles** outside GitHub, and confirmed the 9-agent audit passed. The final-date research watcher abstained (NO_TRADE). This is not a backtest or realized financial result.

The new OFFLINE-only program runs the already implemented 9-agent research WATCH criteria **chronologically** on those local daily bars, forming each research watch from **previously closed bars** and assuming any hypothetical fills occur at the next observed trading-session open.

## Current-public-fee-only pro-forma assumption — NOT 2024 actual bills

Official Upstox reference https://upstox.com/brokerage-charges/ provides current 2026 standard NSE delivery brokerage ₹20 **per executed order**, DP ₹20 **per scrip sold per day**, delivery STT 0.1% buy and sell, stamp duty 0.015% on buy, NSE transaction charges 0.00307% (from 1 March 2026), SEBI ₹10/crore, and GST 18% on certain fees. These are **November 2026 publicly listed values**, not a date-correct historical fee schedule for 2024. Customer contract note, personal plan, IPFT/ancillary fees, charge rounding, dividends and corporate actions still require verification.

The new program intentionally labels results CURRENT 2026 DELIVERY COSTS APPLIED PRO FORMA TO 2024 PRICES — **not historical Upstox net-return calculations**. Overnight gap and executable book orders cannot be certified from daily OHLCV.

## Windows local commands — no token, network, or data upload

From your existing PowerShell clone:

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main

node --test --test-reporter=tap .\projects\qhap-trader\live_readiness\test_nse_swing_costed_chronological_replay.mjs

$source = Join-Path $env:USERPROFILE 'QHAP-TRADER-PRIVATE\equity_daily\development-RELIANCE-2024-01-01-to-2024-10-24.json'
node .\projects\qhap-trader\live_readiness\nse_swing_costed_chronological_replay.mjs --private-development-file "$source"
~~~

The program reads this one locally stored PRIVATE_REPLAY JSON file. It does not contact Upstox, any exchange or model provider, and it prints no raw candle/price rows. It publishes only synthetic research results and sanitized model aggregate figures. No real or paper order submissions.

## Policies and baselines

- **Agent WATCH counterfactual**: use only the first 80+ already closed daily bars to evaluate prior history, hypothetically enter at NEXT day's open when researchWatch true, one whole-share long-only position under ₹2,500 **including fees**, virtual starting cash ₹10,000, hold five recorded sessions, exit at a later observed daily open, never exit and re-enter same session. Force flatten at the final observed open as a purely hypothetical research convention, not an actual executable order. This counterfactual does NOT override the mandatory real-money risk guardian finalDecision NO_TRADE.
- **Passive same-budget**: buy once at the first eligible next open, exit at last observed open, same ₹2,500 order budget and ₹10,000 unleveraged initial cash, no dividend reinvestment.
- **NO_TRADE**: no hypothetical transactions, ₹0 modeled P&L.

Compare 1×, 2×, 3× illustrative slippage/spread/uncertainty execution stress while holding published brokerage/transaction taxes constant. Output contains gross price movement, assumed fixed/variable delivery charges, execution drag, hypothetical rupees net, trades and modeled return on initial virtual ₹10k. A positive number is still only an exploratory developmental result and **not** a green light for real trading.

## Integrity and model limitations

- The 204 days belong to **already inspected development**, not 60+ fresh untouched independent holdout dates in three regimes. A strategy cannot be optimized here and then called independently successful.
- The model uses next-observed-open *hypothetical* fills and daily closing marks. It cannot verify order book depth/queue, exact fills, dividend adjustments, full capital gains tax, exchange holidays, original source entitlement or all relevant Upstox charges and rounding.
- The code has no trade execution endpoint, brokerage client, external model endpoint, paid API call, backfilling of missing bars or scheduled bot. Human's earlier Sandbox test showed simulated ACKs only and is not used here.
- Negative results must be preserved without optimizing 1,000 variants to make them look successful.

No QHAP project email may be sent without explicit user prior approval for that email; unrelated outreach automations are unchanged.
