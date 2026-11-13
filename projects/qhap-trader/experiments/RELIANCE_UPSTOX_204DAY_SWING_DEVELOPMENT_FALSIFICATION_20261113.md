# QHAP NSE — 204 real daily bars, swing WATCH failure: development record

**13 November 2026. Current swing candidate: REJECT for real-money promotion; NO_TRADE remains enabled.** Source is the user's privately downloaded Upstox V3 NSE RELIANCE daily historical data from 2024-01-01 through 2024-10-24. The user ran the chronological nine-role counterfactual research replay locally, then supplied only its sanitized aggregate JSON, no raw candles or secrets.

## Evidence and provenance

- 204 daily price bars saved ONLY on user's Windows machine outside GitHub. User-reported private source SHA-256: 472f6080a0b6ca8a253bd49231af420f708e2b4c0c0f834ef684c04fd578efe7 (not authenticated exchange provenance).
- After 80-bar development warmup, 98 audited flat-position agent decisions, five research WATCH decisions, **five hypothetical round trips and zero net winning trades**.
- Model: virtual ₹10,000 cash, maximum ₹2,500 TOTAL order budget per one position including fees, five trading-session hold, hypothetical NEXT observed daily opening fills. NO actual market or paper order.
- These 204 provider days are **inspected development only**, not an untouched 60+ session, independently characterized three-regime holdout. This was not a real-money account or certified trading statement.

## Cost-stress comparison

| Scenario | Nine-role WATCH strategy | Passive same-size holding | NO_TRADE | Agent minus passive |
|---|---:|---:|---:|---:|
| 1x | **−₹442.4580** | −₹195.2920 | ₹0 | −₹247.1660 |
| 2x | **−₹478.9865** | −₹201.9775 | ₹0 | −₹277.0090 |
| 3x | **−₹515.5149** | −₹208.6631 | ₹0 | −₹306.8518 |

At 1x, **gross open-to-open movement −₹35.0000**, **2026 public-fee-model charges ₹370.9324**, and **assumed adverse execution drag ₹36.5256**. Total illustrative loss −₹442.4580 and ending cash ₹9,557.5420, equivalent to −4.4246% of initial virtual account cash. Combined fees plus friction ₹407.4580 = **92.09% of the loss**. The gross movement was *negative even before costs*, so reducing brokerage alone would not turn these five particular counterfactual trades profitable.

**DO NOT TUNE THESE SAME DAYS TO MAKE A POSITIVE BACKTEST OR CLAIM FUTURE PROFITS.** The full aggregate-only evidence JSON is saved at [evidence/RELIANCE_UPSTOX_204DAY_SWING_DEVELOPMENT_20261113.json](evidence/RELIANCE_UPSTOX_204DAY_SWING_DEVELOPMENT_20261113.json). Independent small pure review program at [review_daily_swing_development_evidence.mjs](../live_readiness/review_daily_swing_development_evidence.mjs) rejects the current live candidate, fails closed on manipulated P&L, and refuses live promotion even if a different development aggregate happens to be positive. This is not a real-order risk engine; QHAP has no real order route.

## Fee/data limitations and why this cannot be certified 2024 broker P&L

Official [Upstox current brokerage schedule](https://upstox.com/brokerage-charges/) confirms standard NSE equity delivery brokerage ₹20 **per executed order**, DP sale charge ₹20 **per scrip/day**, delivery STT 0.1% each side, buy stamp 0.015%, SEBI ₹10/crore, GST 18% on brokerage+transaction+demat+IPFT, and an NSE transaction rate **0.00307% from March 2026** versus **0.00297% from October 2024 to February 2026**. The 2026 model is applied PRO FORMA to 2024 historical candles. Historical account-specific rates, contract-note rounding and IPFT/other charge nuances are unverified; no actual dated Upstox contract note was inspected. The final NAV/exit-price fills and order book cannot be proved from daily candles.

The [NSE Reliance bonus circular](https://nsearchives.nseindia.com/content/circulars/FAOP64621.pdf) confirms the 1:1 bonus ex-date October 28, 2024 is beyond the chosen October 24 endpoint, but earlier dividends/other actions, data-adjustment methods, source rights, full exchange session calendar and overnight gaps remain independently unverified. Passive holdings omit actual dividends and corporate-action compensation. Neither hypothetical P&L is a realized account statement or an investable guaranteed return.

The nine agents are currently deterministic software roles, not nine live Claude/GPT model accounts. Trend/volatility/liquidity are derived from the same historical candle source and not independent price evidence.

## Next research gates

- Reject current 20/60 moving-average plus five-session WATCH as live-release candidate, while retaining its fixed version as a falsified **development benchmark**. Preserve earlier rejected FAST/ONE/TIME_MOMENTUM_GATE intraday evidence (84 July cross-year and five Jan2025 provider data days).
- Build exact official, effective-dated NSE cash-equity Upstox delivery charges plus source calendar/corporate-action audit, and confirm with an actual user-authorized plan/contract note when available. Avoid copying 2026 fees onto 2024 without labeling.
- New economic hypothesis needs clearly different, lower-turnover, more diversified liquid cash equity/ETF evidence with conservative full portfolio/account sizing, not simply more research-agent votes. Freeze new rules and prospective windows BEFORE touching truly unseen dates; compare against NO_TRADE and passive holding after real costs. Multiple tests, time-series purging and drawdown uncertainty matter.
- Only after independent positive after-cost results: separate zero-money forward paper, account reconciliation and conservative risk. No actual live orders, secrets, paid LLM calls, automated broker execution or QHAP emails were involved.

**QHAP email rule:** user approval is needed for each QHAP-specific send, reply, forward or resend. Other outreach projects unaffected.
