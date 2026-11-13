# QHAP-TRADER — Provider rights clarification draft (13 November 2026)

**UNSENT. For human approval only.** This is not permission to contact a provider, obtain data, use credentials, or run a live feed. No customer/account identifiers, tokens, source data, quotes or private strategy parameters belong in GitHub.

## Proposed inquiry to Upstox support (support@upstox.com)

Subject: Written clarification: retail API historical backtesting versus virtual paper simulation, NSE cash equities

Hello Upstox API/market-data compliance team,

I am assessing a small, private, non-distributed, profit-oriented research project using NSE cash-equity data with a hypothetical ₹10,000 long-only account. Before accessing or storing any market data, could you please provide a written, account-independent interpretation of the applicable Upstox terms and upstream NSE licensing requirements for these **separate** uses?

**A — Historical analysis:** Locally downloading Upstox Historical Candle V3 minute OHLCV, privately retaining/caching it, calculating strategy indicators, and running offline historical backtests for a potential future personal trading strategy. Are these uses permitted under an ordinary retail Analytics Token? Are non-display, derived-data, exchange agreements, storage limits, fees, or other approvals required? Please cite the controlling clauses and whether this differs for intraday data.

**B — Forward virtual simulation:** Reading real-time Upstox market data into a private, non-displayed program that generates hypothetical orders/fills, performance reports and risk signals, with **no real orders**. Is this allowed under ordinary retail access? How does NSE Data Usage and Sharing Policy §7.4 (virtual trading/simulation) apply, and is a separate written NSE/provider permission or non-display agreement required? If prohibited, is there a specifically permitted alternative product/usage class?

**C — Future automated real trading (information only):** Please identify the current requirements for a retail individual using an Upstox Algo Trading App: static-IP registration, X-Algo-Name, exchange/broker algo registration and approval, rate limits, and risk controls. We are **not requesting trading access or credentials**.

Please distinguish what your team can authorize from what requires NSE or another rights holder, and provide written references to current terms, costs (if any), and retention/redistribution restrictions. We will not infer a license from API technical availability or a generic backtesting example.

Thank you.

## Conditional follow-up to NSE marketdata@nse.co.in (also UNSENT)

Please clarify whether an individual retail user may use broker-supplied NSE cash-equity historical 1-minute candles for local private profit-oriented strategy backtesting, versus real-time data for private virtual/paper order simulation, and whether each separately triggers NSE non-display/data-sharing agreements, fee schedules, or an outright restriction. In particular, how does consolidated Data Usage and Sharing Policy §7.4 interact with broker-distributed end-user data and the March 2026 Non-Display Policy? Is the broker authorized to determine the user's permitted scope, or must NSE issue written approval? Please identify controlling clauses and the appropriate compliance channel. This is a policy inquiry only, not a request for market data or an account.

## Evidence acceptance and safe handling

1. Human approves any outbound contact separately; **this document itself sends nothing**.
2. Independently identify the responder and official organizational domain; preserve date, full clauses/links, use category, authorized subject, retention, data derivation, costs and expiry in **private** evidence. Do not upload personal account correspondence, credentials, tokens or licensed data to this repository.
3. A generic support reply, technical API access, a self-asserted permission flag or a synthetic signature does not establish upstream NSE authorization. Conflicting/ambiguous answers stay **BLOCKED** pending qualified clarification.
4. Historical backtesting rights never imply forward real-feed paper simulation rights; neither implies trading API permission. The 60-session target remains **zero independently verified** until legitimate prospective data and independent review exist.
5. Default research action remains **NO_TRADE**, no broker connection, no data fetch, no orders, no payments and no auto-resume.

References: [Upstox Backtesting guide](https://upstox.com/developer/api-documentation/backtesting/), [NSE Data Usage & Sharing Policy](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf), [NSE March 2026 Non-Display Policy](https://nsearchives.nseindia.com//web/mediaattachment/2026-03/Non_Display_Policy_20260323164430.pdf), and existing [rights research](DATA_SOURCE_REQUIREMENTS_AND_RIGHTS_20261112.md). These are previously recorded primary-source references, not new authorization.
