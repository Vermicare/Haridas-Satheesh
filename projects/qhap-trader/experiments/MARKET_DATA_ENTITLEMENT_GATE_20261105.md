# QHAP-TRADER — source entitlement and provenance gate (2026-11-05)

**Scope:** NSE cash-equity historical/forward minute-level research; **not** market-data authorization or trading approval. No licensed raw data is included. Status: **BLOCKED**. ₹10,000 simulated, long-only, no broker orders.

## Falsifiable gate

A source is **eligible for authenticated replay** only if ALL of these fields have independent evidence: (1) named provider and chain of custody, (2) user's permitted non-display research/backtest use and local retention, (3) explicit public-repository redistribution permission *or* commitment not to redistribute raw data, (4) symbol/ISIN, timezone, bar construction and timestamp semantics, (5) date-specific exchange session/halts and corporate-action handling, (6) independently checked per-day completeness and file hashes, and (7) sufficient independent untouched days across regimes. Missing/ambiguous fields => **UNKNOWN / NO AUTHENTICATED REPLAY**. Public URL, working download, broker app registration or reproducible Git blob alone are not licenses.

## Source matrix — verified documentation vs unverified entitlements

| Candidate | Official documentation | What it actually establishes | Missing evidence | Gate |
|---|---|---|---|---|
| NSE historical order/trade data | [NSE historical data products](https://www.nseindia.com/static/market-data/eod-historical-data-subscription) | NSE advertises capital-market historical order/trade products and a subscription process; EOD is distinct from minute bars | Subscription, research/non-display agreement, delivered schema, minute OHLC derivation, dates, entitlement, sample verification | **BLOCKED** |
| NSE realtime or stock-wise feed | [NSE real-time products](https://www.nseindia.com/static/market-data/real-time-data-subscription) | Feed levels and stock-wise time-interval product exist; real-time snapshots are not automatically full minute OHLC candles | Licensed vendor agreement, timestamp semantics, continuous feed and local observation ledger | **BLOCKED** |
| Authorized third-party data vendor | [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy) | Vendor delivery can be a route, but usage/redistribution governed by relevant agreements | Specific vendor authorization, user entitlement, historical minute product, permitted research retention | **BLOCKED** |
| Existing February 2021 ACC/RELIANCE third-party Git blobs | [QHAP issue #27](https://github.com/Vermicare/Haridas-Satheesh/issues/27) | Reproducible development inputs, not exchange-certified | Origin chain, rights, authoritative bar reconciliation, session completeness | **BLOCKED** |
| Upstox read-only future adapter (not published here) | [QHAP issue #27](https://github.com/Vermicare/Haridas-Satheesh/issues/27) | Local adapter tests were reported; account application pending review as of 2026-11-05 | Approved account, personal read-only entitlement, actual feed, terms, durable offline safety infrastructure, 60 observed sessions | **BLOCKED** |

## Primary rights findings

NSE [Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy) says relevant agreements define use, handling and dissemination; subscribers cannot redistribute market data except as agreed. It specifically includes historical and delayed data in its market-data definition. The [NSE historical-data page](https://www.nseindia.com/static/market-data/eod-historical-data-subscription) distinguishes EOD from historical order/trade products. The [NSE realtime-data page](https://www.nseindia.com/static/market-data/real-time-data-subscription) distinguishes quote/depth feeds and stock-wise interval feeds. These public product descriptions **do not establish this researcher's contractual entitlement**.

## Minimal evidence receipt for a future source (no credentials or licensed raw bars in Git)

```json
{
  "provider": null,
  "instrument_isin": null,
  "product_and_granularity": null,
  "bar_timestamp_timezone_and_construction": null,
  "license_reference_local_only": null,
  "research_non_display_permitted": "UNKNOWN",
  "retention_permitted": "UNKNOWN",
  "public_redistribution_permitted": "UNKNOWN",
  "session_calendar_reference": null,
  "corporate_action_reference": null,
  "local_source_sha256": null,
  "observed_session_count": 0,
  "replay_authorized": false
}
```

**Acceptance:** all required fields independently evidenced and checked; negative/missing evidence remains visible. This document is a rights **screen**, not a legal opinion or substitute for reviewing the actual agreement. Do not infer a subscription, pay for access, contact providers or connect a broker automatically. No forward-paper readiness before actual permitted data, persistent local watchdog/ledger and 60 prospective sessions. No performance claim.
