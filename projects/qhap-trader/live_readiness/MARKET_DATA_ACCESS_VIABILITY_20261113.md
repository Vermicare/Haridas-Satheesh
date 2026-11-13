# QHAP-TRADER — verified lawful data-access routes (13 November 2026)

**RESEARCH ONLY — NO_TRADE, zero new licensed market bars, zero real orders and no measured trading edge.** This is an independent public-source decision memo, not an exchange licence or legal opinion.

## Most important new finding: NSE has a narrowly approved historical strategy-testing route

The NSE [consolidated Data Usage and Data Sharing Policy](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf), **PDF p.4, §5.1**, expressly contemplates supplying historical tick-by-tick/trade data to *qualifying prospective or new trading clients* so they can test strategies and decide whether to trade Indian markets.

- NSE may approve up to **six months of historic order/tick/trade data as a free trial** for that population. The requester must apply; NSE must authorize and instruct NSE Data to provide it.
- Historic access beyond six months and up to **twelve months** requires additional written senior approval. None is guaranteed.
- **§5.2 requires a declaration that the client is not presently trading the Indian market / market segment for which they request the trial**. No eligibility or not-trading status has been established for the user; do NOT make a false declaration.
- Contrary to an overly restrictive previous note, the text of this section does **not expressly require every applicant to be an incorporated commercial entity**. NSE alone decides actual individual-eligibility requirements.
- This **does not** provide the multiple-year three-regime pristine historical holdout demanded by our precommitted research protocol. At best, if granted, it can help lawful source/provenance and restricted-sample engineering.

Crucial difference: **§7.4 of the same PDF, p.6** restricts supplying data to entities/apps/individuals engaged in **virtual trading or simulation**. Its companion [member circular NSE/COMP/56426 (20 Apr 2023)](https://archives.nseindia.com/content/circulars/COMP56426.pdf) restricts gaming/virtual trading with live exchange feeds. This is a real blocker for an **external live-feed paper-fill service**. But **§5.1 shows lawful, limited and specifically approved historical strategy tests can exist**. The right interpretation is *different written entitlements for distinct activities*, not blanket permission and not a blanket ban on every private retrospective analysis.

NSE's separate [academic research](https://www.nse.in/static/research/initiatives-data-for-research) programme is academic and non-commercial, not presumed applicable to a profit-seeking investment strategy.

## Source shortlist — verified coverage, not legally approved

| Source | Published 1-minute NSE cash history or native testing | QHAP decision |
|---|---|---|
| **Upstox V3** | Since **January 2022**; one-month query windows for 1–15 minute intervals; free read-only Analytics Token | **FIRST CHOICE** when use-specific account/broker licence, storage and corporate-action rights are verified. Existing support #9970397 only automatic acknowledgement at latest check |
| **DhanHQ** | Up to **5 years** of intraday 1/5/15/25/60-minute OHLCV; **₹499 + GST every 30 days**, automatic ledger renewal; Dhan advertises historical backtesting and an isolated API sandbox | **BACKUP** for genuine multi-year history; end-user contract/retention and NSE non-display/virtual trading scope not verified. Non-sensitive detailed licensing inquiry **sent** to official API support apihelp@dhan.co, personal Gmail message/thread 1a1d40001f6842b7. No subscription/account |
| **Zerodha Kite Charts/Streak** | Broker chart equity 1-minute bars since **2015**; native Chart-to-Backtest powered by Streak supports 1-minute timeframes and certain indicators | **OPTIONAL BROKER-NATIVE QUALITATIVE CROSS-CHECK**, not an exact executable copy of custom QHAP opening-range and fee logic, nor independent return certification. Kite Connect terms separately forbid virtual/mock trading apps; do not scrape chart pixels or use API outside terms |
| **Tick Data** | Vendor advertises NSE historical tick quotes/trades, 1-minute bars, corporate actions/symbol mapping **since 2012**; leased dataset, price by sales quotation | Long-history paid alternative only if genuinely affordable and express market-data/retention rights are verified |
| **TrueData REST API** | Default 1-minute bar history **six months**; extended archive only described as future add-on in published knowledge base | **INSUFFICIENT** for multi-year historical holdout without separate confirmed product and rights |
| **Global Datafeeds REST API** | Default 1-minute NSE cash bar backfill **three months** | **INSUFFICIENT** for a multi-year retrospective; a vendor's optional future after-hours CSV collection does not invent years of history |
| **NSE directly** | Paid historical trade/order data through an application and agreement; §5 prospective free trial under strict requirements | Direct paid product economically disproportionate to ₹10k hypothetical capital. Free trial conditional and too short alone for three-regime study |
| **Upstox Algoverse** | Broker-native paper/backtest features marketed predominantly for **index/stock futures and options** | Does **not** match QHAP's NSE *cash-equity* long-only frozen evaluation or authorize external feed-driven simulated trading |

For any provider, "available since YEAR" does **not guarantee** every instrument, special session, corporate-action adjustment, delisting and minute is available or valid. NSE daily public bhavcopy lacks minute-level fill chronology and cannot validate this intraday strategy.

## Specifically separable evidence rights

**A. Retrospective private trading-strategy research**: historically timestamped cash-equity 1-minute OHLCV under an explicit provider/end-user research entitlement; written retention/derived-statistics/cloud/GitHub terms; official exchange session and auction/calendar coverage; valid raw vs adjusted bars. It may be a legitimate route once authorized, distinct from live virtual trading.

**B. Native broker chart backtest**: may be conducted in the licensed platform's own interface under its offered terms, but does not automatically supply QHAP reproducible raw data, exact fees, source hashes or unchanged strategy semantics.

**C. Live exchange-data-fed synthetic fills**: independent §7.4 issue. An API token (even read-only), payment, stale delayed stream or broker promotional page does NOT prove that a separate automated paper-fill application is allowed.

**D. Sandbox only**: independent broker API request/response and failure-path tests using fixtures with no actual licensed prices. Safe engineering but cannot establish forward trading edge or fill quality.

## Exact prerequisites before a purchase or data download

1. Verify the **specific person/account and purpose** are covered in dated NSE/broker/vendor terms and any separate non-display/virtual-use contract.
2. Confirm **full coverage** of at least three truly independent market regimes and 60 genuinely uninspected cash-market trading dates; instrument IDs/ISINs including delistings; source quality, holidays/auctions and timestamp availability.
3. Confirm **local retention, redistribution, source hashes and derived aggregate outcome** rights; no raw data or credentials in GitHub/AI chat.
4. Confirm **actual total charge and auto-renewal/cancellation**, including any exchange market-data subscription or additional non-display fees. A monthly ₹499 DhanHQ quote is not a legal waiver; no new subscription has been activated.
5. Before seeing any protected new returns, freeze actual unchanged strategy, strategy/simulator Git SHA after #65/#66, sources, cost model and exception-calendar version, baseline/NO_TRADE, holdout dates and uncertainty intervals. Previously seen Feb2021 ACC/RELIANCE and NHPC short stream are **development only**.
6. Real **net-of-cost after-fee** evidence must pass separate adverse-friction, regime and day-block uncertainty checks. A passing synthetic unit test is not a statistically significant edge. 60 future complete independent sessions also need separate real allowed source/use and validation.
7. Future actual orders remain separately blocked pending account, authorized broker app, static IP, applicable registration, risk/security/reconciliation and **explicit human approval**.

## Provider inquiries actually sent (no credentials/data/payment)

- **Upstox:** support ticket #9970397, via personal Gmail on 12 Nov; latest check only auto-ack. Request contrasts private historical use versus live virtual-paper use.
- **NSE Data & Analytics:** sent to official marketdata@nse.co.in on 13 Nov, thread 1a1d3fac0043ec6d; includes licensing clause §7.4, individual fees and permitted source questions. On reply, separately ask how **§5.1/§5.2 prospective trading-client trial** eligibility applies, without making any unverified declaration.
- **DhanHQ:** sent to official apihelp@dhan.co on 13 Nov, thread 1a1d40001f6842b7, explicitly asks 5-year cash-equity coverage, personal profit-oriented historical use, local retention, licensing and monthly payment/cancellation. No sign-up/subscription.

**Never auto-send duplicate follow-ups or transfer keys, account documents or private prices to a provider.** Existing hourly QHAP task monitors responses.

## Primary reference URLs (consulted 13 November 2026)

- NSE consolidated policy, §5 prospective client trial, §7.4 simulation restriction: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf
- NSE member circular COMP/56426: https://archives.nseindia.com/content/circulars/COMP56426.pdf
- NSE direct historical products: https://www.nse.in/static/market-data/eod-historical-data-subscription
- NSE non-commercial EPR: https://www.nse.in/static/research/initiatives-data-for-research
- Upstox V3 historical candles: https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/
- Upstox read-only token: https://upstox.com/developer/api-documentation/analytics-token/
- Upstox Algoverse: https://upstox.com/algoverse/
- DhanHQ historical window: https://dhan.co/support/platforms/dhanhq-api/what-timeframe-data-is-available-through-dhan-s-historical-data-apis/
- DhanHQ recurring price: https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/
- Dhan official contact: https://dhan.co/customer-service/
- Dhan sandbox/backtesting: https://dhan.co/blog/trading-strategies/how-to-start-algo-trading-on-dhan/
- Zerodha chart data depth: https://support.zerodha.com/category/trading-and-markets/charts-and-orders/charts/articles/historical-data-on-kite-charts
- Zerodha own CTB tool: https://support.zerodha.com/category/trading-and-markets/charts-and-orders/charts/articles/backtest-on-kite-charts
- Zerodha API terms: https://kite.trade/terms/
- Tick Data licensed NSE coverage: https://www.tickdata.com/equity-data/national-stock-exchange-of-india
- TrueData API 6-month default: https://feedback.truedata.in/knowledge-base/article/historical-data-availability-through-rest-api
- Global Datafeeds NSE CM 3-month default: https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/introduction/type-of-data-available/
