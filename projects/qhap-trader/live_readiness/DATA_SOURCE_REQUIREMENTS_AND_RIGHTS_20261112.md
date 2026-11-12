# QHAP-TRADER — Source, rights, prices and live-API requirements (researched 12 November 2026)

**Decision: DO NOT BUY A FEED OR RUN LIVE-DATA-DRIVEN PAPER TRADING WITHOUT SPECIFIC WRITTEN RIGHTS.** Research-only software remains NO_TRADE; initial hypothetical strategy account ₹10,000, 0 real orders, 0 independently verified forward sessions, no established post-cost edge.

**This is a primary-source evidence register, not an entitlement, legal opinion, Upstox account check, or independent source-data verification.** No market-data API, broker account, credentials, real quotes, payments or market-data provider was contacted.

## Executive finding — distinguish three activities

| Intended activity | What is actually documented | Unresolved binding requirement | Status |
|---|---|---|---|
| A. Personal, private **historical backtest** of cash equities | Upstox developer guide explicitly documents historical OHLC-based equity backtesting. Historical Candle V3 advertises 1-minute bars from Jan 2022, fetched in 1-month chunks | Get current written determination whether this user's API/account terms, NSE upstream rules, non-display/derived-data licensing, storage and *profit-oriented internal strategy testing* permit the exact workflow. Do **not** equate API access with legal rights | TECHNICALLY DOCUMENTED / ENTITLEMENT UNCONFIRMED |
| B. Continuous **live-feed virtual/paper trading** with synthetic fills | Upstox Market Data Feed V3 technically exposes streams; its Analytics Token is read-only. NSE consolidated Data Usage & Sharing Policy PDF **§7.4** restricts supplying data to individuals/entities/platforms/apps engaging in virtual trading or simulation | Require explicit written provider/exchange compliance interpretation. Neither analytics token nor generic “backtesting” guide overrides upstream restrictions or proves permission. Alternative: keep synthetic test fixture entirely detached from actual live prices | BLOCKED PENDING WRITTEN COMPLIANCE DECISION |
| C. Eventual **automated real cash trading** | Upstox says API order placing/modifying/canceling requires registered static IP, Algo Trading App and header X-Algo-Name, effective 1 Apr 2026. SEBI/NSE retail-algo implementation standards also apply | Broker account/API eligibility, risk and order tags, session/kill-switch validation, applicable registration and exchange compliance, independent net edge, separate explicit human authorization before any order | NOT AUTHORIZED / NO ORDER ROUTER |

### Critical policy distinction

The NSE [consolidated source policy PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf), §7.4 (PDF physical page 6), restricts providing data to services/people engaging in virtual trading or simulation. Section 13(i) separately defines research activity for purposes *other than trading or profit*. It is therefore **not** safe to present the NSE's academic/non-commercial researcher route as already available for a proprietary profit-motivated bot.

However the [Upstox official Backtesting guide](https://upstox.com/developer/api-documentation/backtesting/) explicitly illustrates evaluating trading strategies with its Historical Candle Data V3; this supports technical API intent but does **not** resolve exact licensing and caching terms, or the separate virtual-trading restriction. Treat the apparent tension as an **escalation question**, not automatic approval or a categorical ban on all historical analysis. Different proposed uses and contracting chains must be reviewed separately.

The [NSE Non-Display Policy (Mar 2026)](https://nsearchives.nseindia.com//web/mediaattachment/2026-03/Non_Display_Policy_20260323164430.pdf) §1.3 covers automated trading decision calculations, derived internal analytics and algorithmic uses, and §3.1 calls for applicable agreement/undertaking and fees. §3.5–3.6 explicitly distinguish external redistribution and other uses requiring separate fees/agreements. Never assume your ordinary retail market-data login already covers non-display or commercial use.

## Technical minimal viable historical dataset (ONLY once explicitly permitted)

- Market universe: **NSE cash equity / unleveraged long-only**; pinned instrument IDs and ISINs, with delisted/inactive securities or survivorship exclusions documented.
- Granularity: complete exchange-session 1-minute OHLCV for the proposed simple opening-range baseline, not end-of-day snapshots. Upstox V3 advertises Jan 2022 onward for minute units; calls with 1–15-minute granularity are bounded to **one month** per request. Daily history from Jan 2000 is not enough to test the intraday rule.
- Time correctness: Asia/Kolkata session dates, bar timestamp semantics and end-of-bar availability; **never** use the triggering candle's future high/low to fill within the same candle. Track partial/special sessions, auctions, holidays, session-specific eligibility and daylight/UTC conversion.
- Quality: per-symbol minute-count validation, duplicate/missing bars, stale/future timestamps, unadjusted/adjusted corporate actions, split/dividend data handling and source fingerprint/provenance. Reject incomplete days; do not discard losing sessions.
- Reproducibility: before *any unseen licensed data is opened*, publish frozen source commits, strategy/fee versions, symbols, predeclared dates/closures, slippage, execution/fill and stop-gap assumptions. Keep user-authorized raw market data *private* and out of GitHub/AI chat.
- Research design: mandatory **NO_TRADE=₹0** comparator plus simple baseline, conservative Upstox modeled charges, 5/15/50 bps per-side shocks and adverse stop-gap tail, untouched walk-forward periods from several regimes, at least 60 full *genuine* prospective sessions before independent review. A positive backtest cannot certify future profitability, and 60 sessions alone cannot prove positive expectancy. Existing February 2021 ACC/RELIANCE sample is already explored and **not** an unseen holdout.
- Real-time evidence later (if authorized): continuous receive clock, independently identifiable exchange book updates—not just Upstox response-generation time or last-trade time—sequence gaps/reconnects, stable source entitlements, and no fabricated fills. With unverified event provenance, remain NO_TRADE.

## Available products, real pricing and suitability

| Route | Publicly documented product/cost | Fit for this ₹10k experiment |
|---|---|---|
| **Upstox Historical Candle V3** | Official backtesting guide provides cash-equity OHLC route, 1-minute data Jan 2022 onward, API is documented on all Upstox plans. Analytics Token is free, read-only, 1-year validity, and technically supports Historical Data and Websocket without static IP | **First route to clarify** for *private offline historical* backtesting; cost-efficient if expressly allowed. Permission for retention, derivatives/derived metrics and paper/live feed remains unknown |
| **Upstox Sandbox Orders** | Official sandbox is no-real-market and no-cost for supported place/modify/cancel order APIs; sandbox token valid 30 days | Suitable for safe broker-shaped API contract testing, **not proof of genuine market fills or strategy advantage**; no actual orders/capital |
| **NSE Data & Analytics direct historical** | Official domestic tariff effective 1 Apr 2026: Capital Market *historical trade data* ₹1,10,000/year/site; *historical order & trade data* ₹12,50,000/year/site; taxes extra, entitlement agreement mandatory | Disproportionately expensive for this project. These are published institutional product tariffs, **not** quotations for this user's broker account or a 1-minute-OHLC product |
| **NSE direct real-time non-display (Capital Market L1)** | Official domestic tariff: ₹23,90,000/year for enterprise single-site; 15-minute delayed L1 non-display ₹1,40,000/year; tax extra, special terms and agreement | **Not a sensible purchase for ₹10,000 capital**. Do not assume these rates apply to an individual Upstox API customer; broker-provided end-user licensing must be clarified |
| **NSE non-commercial EPR research programme** | Academic/non-commercial research only; formal application to nseri@nse.co.in | **Not presumed eligible** for proprietary profit-seeking QHAP |
| **NSE “prospective/new trading client” tick trial** | Consolidated policy §5 describes **up to six months** of historical tick/order & trade data potentially on free trial, subject to qualifying *commercial entity not trading that segment*, declaration and NSE discretionary process | Not a verified individual retail entitlement; do not claim this is available to the user or a free substitute for licensed research |

**Do not buy any direct NSE feed based on the tariff alone**; no product license, user eligibility, provider agreement, permitted use or quote was verified.

## Official live retail-algo rules (future only)

- [Upstox 1 Apr 2026 announcement](https://upstox.com/developer/api-documentation/announcements/algo-trading-circular/): order placement, modification, cancellation and other trading endpoints require registered **static IP**; one primary/one secondary allowed, and **X-Algo-Name** in order requests. Its announcement says algos **over 10 orders/second** require exchange registration/Algo ID; below this threshold it describes no such registration requirement, but **other** API, broker and exchange obligations still apply. Never interpret the throughput threshold as a complete legal exemption.
- [NSE retail-algo operational guidance](https://www.nseindia.com/static/trade/platform-services-non-neat-decision-support-tools-algorithm-trading) cites the May 2025 implementation standards and April 30, 2026 broker submission circular. [Upstox My Apps](https://upstox.com/developer/api-documentation/appendix/my-apps-support-for-algo-trading-circular/) further describes registered IP management, token invalidation on IP updates and app approval.
- For this project's planned low order rate, obtain **current Upstox compliance confirmation** of whether a tech-savvy retail client-direct API strategy needs a separate strategy/exchange registration and the precise approved app/token/header. No credentials, real orders or real funds until separate authorization.
- Independently verify operational risk and economic gates: broker actual executed contract-note fee schedule, debit balance, settlement and partial fills, reject/cancel reconciliation, idempotent recovery, emergency halt, hard ₹10k capital ceiling, single mock position ≤₹2,500, ₹4k cash reserve, max proposed risk ₹50/trade, hard locks, end-of-session squareoff and independent human go/no-go.

## Required **written** answers — Upstox first, NSE escalation

Send only abstract product/use descriptions and public policy URLs; **no access tokens, account IDs, order logs or raw market data**. Official contact:
- Upstox: support@upstox.com (https://upstox.com/contact-us/) and https://community.upstox.com/ for Developer API discussions.
- NSE Data & Analytics: marketdata@nse.co.in / +91-22-26598385 (https://www.nseindia.com/static/nse-data-and-analytics/contact-us).

**A. Upstox:**
1. Does the user's own Upstox Analytics Token/Historical Candle V3 entitlement expressly permit *private, non-displayed, profit-oriented, off-market historical strategy backtesting* on 1-minute NSE cash-equity candles? Please identify governing terms, contract/license version, data-source restrictions and effective date.
2. May the user **temporarily cache or locally retain** OHLCV/corporate actions and derived features, research notebooks, hashes and aggregate *non-reconstructable* performance metrics? For how long; may they be processed on private cloud or shared with independent reviewer? Are algorithmic AI training and third-party model submission separately restricted?
3. Does NSE's Data Usage & Sharing Policy **§7.4** restriction on virtual trading/simulation prohibit a single user's private historical backtest as described by Upstox's own Backtesting guide? Is **live WebSocket–driven synthetic paper trading** separately prohibited? Please provide written policy interpretation and the specific authorized alternative, if any.
4. Is a separate NSE **non-display** agreement/fee required for these **specific personal uses**, or already covered in the broker's end-user agreement? What are exact charges (if any), account/plan requirements and cancellation rules?
5. Are 1-minute candles timestamped at period start or close? Are historical prices adjusted for splits/bonuses? How can corporate-action details, instrument delistings, trading halts, exchange-specific regular/auction sessions, missing minutes and feed-origin timestamps be verified?
6. Does a permitted historical backtest allow public GitHub publication of **only code and aggregate outcomes**, without raw quotes, original market data or identifying hashes? Are derived aggregate performance numbers restricted?
7. What are the current **client-direct retail algo** requirements for future self-hosted, under-10-orders/sec cash-only automated execution, including Algo Trading App approval, registered primary/secondary IP, X-Algo-Name, broker review and kill switch? No live enabling is requested now.

**B. NSE Data, if Upstox cannot give adequate rights determination:**
1. Does private offline historical intraday strategy backtesting by a prospective individual retail trader fall within NSE Policy §7.4's virtual-trading/simulation restriction, or is there a permitted licensed internal non-display research category? Is a provider-written case-by-case exception actually possible?
2. Are there user-end-subscription terms/fees distinct from published enterprise non-display rates, possibly via an NSE-authorized vendor? Specify exact permitted **1-minute** historical product with multi-regime availability, entitlement scope, internal storage, derived statistics and price.
3. If live-data-driven paper simulation is disallowed, confirm whether **historical-only** algorithm evaluation (without simulated order submission through a service), or fully synthetic market data, is acceptable. Do not provide or download NSE market data before the response.
4. What independent source proofs and time/reference details would make the historical and prospective integrity audit sufficient for this proposed personal research use?

## Next action rule

1. **Today:** preserve the research methodology and continue only no-real-data synthetic integration tests; do **not** fetch Upstox candles or start streaming for this research until acceptable terms are determined.
2. **After provider responses:** review versioned evidence privately. If explicit private historical backtesting is authorized, download *only* permitted 2022+ minute OHLC in monthly batches into secure user-local storage, run immutable source verification, and preregister all untouched holdouts.
3. If rights are denied, unclear, unaffordable or require prohibited synthetic simulated trade uses: **remain NO_TRADE**; do not pivot to unlicensed scraped CSVs, clone/exchange mirrors, leaked historical data or token workarounds.
4. Only after independently reproduced net-after-cost edge and prospectively witnessed complete permitted sessions should a **separate** broker/compliance live-readiness review begin. Never automatically initiate orders.

## Primary sources (retrieved and reviewed 2026-11-12)

1. NSE consolidated Data Usage & Sharing Policy PDF §5, §7.4, §9, §13: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf
2. NSE Non-Display Policy March 2026: https://nsearchives.nseindia.com//web/mediaattachment/2026-03/Non_Display_Policy_20260323164430.pdf
3. NSE Domestic Data Tariff effective 1 April 2026: https://nsearchives.nseindia.com//web/mediaattachment/2026-04/Download_Pricing_file_-_Domestic_clients_20260424122229.pdf
4. NSE Data for Research (updated 4 Nov 2026): https://www.nse.in/static/research/initiatives-data-for-research
5. Upstox Official Backtesting: https://upstox.com/developer/api-documentation/backtesting/
6. Upstox Historical Candle Data V3: https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/
7. Upstox Analytics Token: https://upstox.com/developer/api-documentation/analytics-token/
8. Upstox Sandbox: https://upstox.com/developer/api-documentation/sandbox/
9. Upstox Algo Registration & Static IP, effective 1 Apr 2026: https://upstox.com/developer/api-documentation/announcements/algo-trading-circular/
10. Upstox support and NSE Data official contact: https://upstox.com/contact-us/ and https://www.nseindia.com/static/nse-data-and-analytics/contact-us
