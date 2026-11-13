# QHAP-TRADER — Actual Upstox multi-year development falsification (2026-11-13)

> **Decision: RETIRE FAST / ONE / TIME_MOMENTUM_GATE AS LIVE-RELEASE CANDIDATES; KEEP NO_TRADE.** The user independently ran local, authenticated, *read-only* Upstox V3 history import and the existing offline replay against previously downloaded **RELIANCE one-minute** rows. Every tested trade policy lost money after **illustrative** fees and all three slippage stresses (5, 15, 30 basis points per side). This is **development evidence** only, not a frozen unseen holdout, broker P&L, or investment advice.

## Provenance and scope

- Data origin: user-local **Upstox Historical Candle V3** (NSE cash equity); 4 user-selected **July 2022, 2023, 2024, 2025** months, fixed instrument key `NSE_EQ|INE002A01018`; one read-only month-limited GET per month. No token, raw candles, order identifiers or secret values shared or pushed to GitHub.
- Private importer: `projects/qhap-trader/live_readiness/upstox_v3_multiwindow_development.mjs` at merged PR #76. Local command gave `DEVELOPMENT_MULTIYEAR_BATCH_LOCAL_ONLY_COMPLETE`, four requests completed, 32,576 raw 1-minute candle rows saved privately, **84 candidate-complete stock-days** with private combined date-only manifest. No real orders or accounts touched.
- Per-month sources: July 2022 **7,875 candles, 21 candidates**, 0 absent weekdays; July 2023 **7,826 candles, 18 candidates**, 0 absent weekdays; July 2024 **8,250 candles, 22 candidates**, **one absent weekday**, July 2025 **8,625 candles, 23 candidates**, 0 absent weekdays. **Do not infer all originally observed dates were complete.** The development manifest includes only candidate-complete days; `excluded: []` in replay is a property of that prefiltered manifest, not proof of fully representative exchange coverage.
- NSE official 2024 capital-market trading holiday circular dated Dec 12, 2023, reference NSE/CMTR/59722 lists **2024-07-17 (Muharram/Moharram)** as a trading holiday: https://nsearchives.nseindia.com/content/circulars/CMTR59722.pdf . This likely explains the one absent July 2024 weekday, but local private audit's actual absent date **has not been independently inspected here**. Do not silently replace with an invented flat session.
- Upstox V3 reference: https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/ . Data availability and completeness are user-reported from sanitized local results, not independent exchange original time-and-sales, corporate action entitlement evidence, clock attestation or executable bid/ask book.
- Engine: `projects/qhap-trader/experiments/intraday_clock_replay.mjs` at current `main` when user ran; **hypothetical ₹10,000 per symbol-day resets**, not one compounded ₹10,000 account; 1-minute OHLC cannot certify fills/queue and potential intra-bar path risk. Offline simulation returns `sourceRightsVerified:false`, `exchangeBookPriceExecutable:false`, `brokerRoutes:0`, `realTrades:0`.
- User reported verbal approval from Upstox for private historical backtesting and read-only live hypothetical paper trading. This is **user-attested verbal permission**, not independently confirmed written exchange licensing and not real-money broker authorization. No Upstox emails may be sent from QHAP without user approval.

## Aggregate development results: 84 candidate-complete dates (modelled INR, non-compounded)

| Policy | Round trips | 15bps winning trades | Net @ 5 bps/side | Net @ 15 bps/side | Net @ 30 bps/side |
|---|---:|---:|---:|---:|---:|
| FAST | 503 | 24 | −₹1,792.63 | **−₹3,499.93** | −₹6,092.41 |
| ONE | 84 | 7 | −₹286.12 | **−₹573.82** | −₹1,031.67 |
| TIME_MOMENTUM_GATE | 3 | 0 | −₹14.59 | **−₹25.61** | −₹42.14 |
| NO_TRADE | 0 | 0 | ₹0.00 | **₹0.00** | ₹0.00 |

At 15bps/side, FAST's **24/503** winning trades (4.77%); ONE's **7/84** (8.33%); TIME_MOMENTUM_GATE **0/3**. This is not a statistical estimate of next-day win rate because market-year selection was exploratory and only a few disconnected July windows were inspected.

### Economic hurdle analysis (15bps per side)

| Policy | Gross modeled price movement | Charges | Slippage drag | Combined friction | Combined friction / round trip | Gross / round trip | Net / round trip |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAST | −₹68.15 | ₹847.30 | ₹2,584.52 | ₹3,431.82 | ₹6.82 | −₹0.14 | −₹6.96 |
| ONE | +₹1.98 | ₹142.44 | ₹433.46 | ₹575.90 | ₹6.86 | +₹0.02 | −₹6.83 |
| TIME_MOMENTUM_GATE | −₹3.60 | ₹5.48 | ₹16.53 | ₹22.01 | ₹7.34 | −₹1.20 | −₹8.54 |

Some displayed rounded components differ from the net sums by a few paise owing to independently rounded aggregations and path-sensitive calculations; do not try to backsolve confidential trades from totals. In particular, **even the near-zero-cost raw gross opportunity is absent in FAST and TIME_MOMENTUM_GATE**, and ONE's gross ₹1.98 across 84 hypothetical trades is nowhere near friction-covering. Increasing frequency worsens the economic challenge; any new hypothesis must explicitly model execution spread, slippage and fees before promotion.

### Brokerage model needs a primary-source replacement

The existing offline simulator applies `min(₹20, 0.03% of buy notional) + min(₹20, 0.03% of sell notional)` for its **illustrative Zerodha-like brokerage** plus current-date stylized charges; **this is NOT Upstox's contract-note model**. Upstox's official standard fee schedule currently advertises **equity intraday ₹20 per executed order or 0.1% of notional, whichever is lower**, and currently published NSE exchange transaction charge tiers include historical-date changes. Official schedule: https://upstox.com/brokerage-charges/ . An exact apples-to-apples historic contract-note or current Upstox account rate, statutory rounding, taxes, historical venue exchange tiers and execution mode have **NOT** been independently established for these results. Do not re-label historical outcomes `REAL_UPSTOX_NET_PROFIT`.

Because even our *lower* illustrative brokerage scenarios lose at all tested slippage settings, a proper Upstox model is unlikely to rescue these precise versions, but we must **actually calculate**, not assert an exact revised P&L without order-level prices and fees.

## Fail-closed release decision

- **REJECTED FOR LIVE PROMOTION**: FAST, ONE, TIME_MOMENTUM_GATE as configured; retain immutable historical developmental aggregate outcomes for falsification, not selection of the least-negative strategy.
- **RETAIN**: NO_TRADE risk gate (₹0 modeled P&L on days when no orders are attempted). Sandbox API place/modify/cancel acknowledgements have been verified by user on their Windows machine but are **not** independently verified terminal order states or actual fills.
- **Do not retune these strategies on the 84 dates** and present the same observations as independent out-of-sample success. These **84 dates are now known development evidence**. Also Jan 6–10, 2025 five-day sample is already observed and ineligible for untouched holdout.
- **Engineering lane**: audit actual Upstox fee model, execution limit, and loss/position accounting with no production order API. Improve read-only forward paper capture with event-time/freshness/halts/position locks. Do not confuse simulated sandbox acknowledgements with live trading rights.
- **Strategy research lane**: define and version a new, *economically plausible* hypothesis and decision timestamps **before** accessing any future evaluation dates. Pre-register unseen calendar windows and minimum 60 distinct exchange session dates spanning at least three independently validated market regimes; quarantine any missing source/holiday/partial days and include them in audit counts. Positive net-of-all-costs and day-block confidence evidence across regimes/2x–3x friction are required before strategy promotion. **No guaranteed daily profits** and no automatic real-money order release.
- **User-facing honesty**: User's stated goal is eventual autonomous live cash-equity trading, but broker integration and statistical edge are independent gates. Do not enable real orders on this negative evidence.

## Integrity / reproducibility

This report is intentionally constructed from **sanitized, aggregate stdout pasted by the user in the chat**; neither original market prices nor credentials nor private local audits were accessed by the assistant. The user-local combined private development manifest path is `QHAP-TRADER-PRIVATE/manifests/development-multiwindow-RELIANCE-2022-07_to_2025-07.json`. No source bar CSV, market-derived tick, user token or full file-system identity is committed here.

**No real-money orders, no QHAP emails, no market-data upload.**
