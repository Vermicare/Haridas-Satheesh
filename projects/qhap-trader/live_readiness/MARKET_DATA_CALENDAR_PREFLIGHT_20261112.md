# QHAP-TRADER — Official calendar and market-data rights preflight (12 November 2026)

**Operating decision: NO_TRADE. No use of unverified source data.**

This is an independently reviewed **public-document transcription and
a synthetic metadata-only research gate**, not an exchange-issued API,
calendar subscription, broker certification, user license, permission to use
NSE data for virtual trading, or actual approved data ingest.

## Official public references checked

1. NSE [2026 market holidays and timings](https://www.nseindia.com/resources/exchange-communication-holidays?apiversion=v2)
   — Equity public holiday table; contains the special 15 January election
   closure and the 24 November / 25 December 2026 closures.
2. NSE [Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy)
   — actual use, retention, redistributions and other conditions are defined
   in the relevant executed agreements, not by mere public URL access.
3. Upstox [Market Data Feed V3 documentation](https://upstox.com/developer/api-documentation/v3/get-market-data-feed/)
   — documentation describes the provider-side feed and timestamps. A recent
   response timestamp alone cannot certify independent book-event freshness
   or legal permission for hypothetical trading research.

These are **references to check**, not a right to download, replay or trade.
Check current notices, calendar amendments, special sessions, instrument
eligibility and required permission for every intended use. A provider-issued
analytics token is not equivalent to a right to retain data, perform paper
simulations or redistribute data, and no live trading credentials are
requested here.

## 2026 official equity holiday transcription

The pinned table covers **only calendar year 2026**. Dates:
2026-01-15, 01-26, 03-03, 03-26, 03-31, 04-03, 04-14, 05-01, 05-28,
06-26, 09-14, 10-02, 10-20, 11-10, **11-24**, and **12-25**.
All are public reported equity non-trading dates. Weekends are ordinary
non-regular sessions; special sessions or emergency closures require separate
official schedule evidence. Being an unlisted weekday is **not** proof
that a specific security had a lawful continuous session.

The forward research manifest in PR #56 allows synthetic planning of at
least 60 weekdays. A planned range beginning 16 November 2026 necessarily
runs into 2027. **This repo has not pinned a verified official 2027
equity calendar**. Until independently checked and versioned, the new overlay
returns BLOCKED for all plans that rely on any outside-2026 date, even if
they correctly exclude the 24 November and 25 December holidays. That does
not forbid creating a paper-only protocol; it forbids treating such a
declaration as independently calendar-verified evidence.

If an unexpected holiday or trading halt occurs, do **not** silently delete
the date after viewing outcomes. Record the exception, source/date of the
official notice, reason and its impact, and produce a separately frozen
amended plan subject to independent review. Preserve previous versions.

## Offline engineering boundary

[market_data_calendar_preflight.mjs](market_data_calendar_preflight.mjs)
provides three main checks:

- inspectPinned2026EquityDate: weekday/2026-public-holiday/year-scope audit.
- auditPinned2026CalendarAgainstPlan: recomputes the existing prospectively
  frozen manifest fingerprint and checks its weekday closure declarations
  against the pinned 2026 list; 2027+ is unverified.
- auditDeclaredMarketDataRights: strictly redacted metadata receipt with
  provider class, I1 NSE equity granularity, intended non-display research
  **and paper-simulation rights**, local retention, redistribution posture,
  contract/reference digests, dates and external-review record.
  Unknown, denied or missing rights and dates outside the claimed agreement
  fail closed. Even a perfectly self-claimed positive receipt **never
  grants authorization**, since hashes, provider aliases and self-reported
  review cannot authenticate contract text or legal scope.

auditProspectiveInputBoundary composes both checks. Its fixed outcome
NO_DATA_INGESTION_OR_LIVE_EXECUTION_AUTHORIZED is intentional; contract
evidence, exchange notices and any user account/data entitlements need an
external check by the relevant authorized provider/compliance reviewer.
The module never examines raw contracts or copyrighted market prices.

### Still missing before genuine prospective observations

- Explicit proof from the user/provider that the *specific product and
  intended research/paper-simulation use* are permitted; not just a broker
  dashboard login or read-only API response.
- Verified release and calendar amendments for the **2027** equity year
  before any forward plan spanning 2027 is claimed calendar-complete.
- Independently verified daily instrument eligibility, corporate actions,
  session complete source timestamps and raw-file custody. Never put
  credentials, contract notes, client IDs or licensed raw market data into
  a public GitHub repository.
- Independently reconciled fee model and a sufficient, untouched, authorized
  forward evidence window. Even 60 complete self-reported mock sessions
  remain ZERO verified forward market sessions without independent evidence.

The code cannot place or cancel orders, retrieve broker account data, access
a feed, authenticate usage rights, or promote readiness. All outputs retain
canTrade:false, liveTradingAuthorized:false, realOrdersSent:0 and
marketDataUseAuthorizedBySoftware:false.

## Offline test

From repository root, Node 22:

    node --test projects/qhap-trader/live_readiness/test_*.mjs

This runs in the existing trusted PR workflow with no credentials.
