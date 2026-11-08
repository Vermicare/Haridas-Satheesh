# February 2021 NSE cash-equity session exception: evidence gate (2026-11-08)

Scope: QHAP-TRADER research-only; no market-data reproduction or trading authorization.

## Primary regulatory evidence

- SEBI PR 9/2021 (2021-02-25): https://www.sebi.gov.in/media/press-releases/feb-2021/trading-halt-at-nse-on-february-24-2021_49287.html . NSE notified SEBI of an 11:40 IST trading halt on 2021-02-24; SEBI says participants were notified at 15:17 of a 15:30 resumption and an extension to 17:00. This is a regulatory account of an exceptional trading session, not a regular 09:15–15:30 session.
- SEBI PR 13/2021 (2021-03-22): https://www.sebi.gov.in/media/press-releases/mar-2021/trading-halt-at-nse-on-february-24-2021_49603.html . Subsequent regulator discussion; check this and NSE notices before resolving precise reopening phases.
- NSE 2021 capital-market annual holiday circular NSE/CMTR/46623 (2020-12-11): https://archives.nseindia.com/content/circulars/CMTR46623.pdf . No February weekday holiday in original schedule; subsequent amendments/exception notices still require exhaustive audit.
- NSE Clearing settlement circular NCL/CMPT/47328 (2021-02-12): https://archives.nseindia.com/content/circulars/CMPT47328.pdf . February 19 settlement holiday is NOT automatically a cash-equity trading holiday.

## Deterministic fail-closed expectations for future regression implementation

1. 2021-02-02 is an ordinary expected weekday in the provisional annual schedule. A purported manifest that omits it cannot claim authoritative continuous-session coverage.
2. 2021-02-19 must remain an expected trading date despite settlement holiday classification; excluding it solely for settlement status is a manifest error.
3. 2021-02-24 must remain a trading date but be marked EXCEPTIONAL_INTERRUPTED / NOT_CERTIFIED_FOR_ORDINARY_INTRADAY_REPLAY. Do NOT silently classify it as a full-day holiday or a regular session. No fabricated fills/P&L during halt or reopening uncertainty.
4. Reopening time/auction phases must remain UNKNOWN until reconciled against NSE cash-segment primary notices and timestamped data. A source stating 15:30 and another reporting 15:45 is a material discrepancy, not a reason to choose an optimistic execution timestamp.
5. The remaining 19 dates are only PROVISIONAL until amendments and exceptional-session checks are complete. Neither a caller-supplied manifest nor this research note certifies data licensing, minute-bar completeness, corporate actions or genuine fills.

## Falsification gate

Pass only when official-source identifiers and retrieved-byte SHA256 checksums are archived, NSE-specific halt/resumption phases reconciled, an immutable manifest is generated, and executable positive/negative tests plus GitHub Actions results show fail-closed behavior for (1) missing February 2, (2) wrongly excluded February 19, (3) unflagged February 24, and (4) unknown reopening timestamps. No synthetic pass is a live-feed or profitability result.

This note records source URLs and a conservative test specification, not authenticated source-file checksums or a completed code/test change. Previous negative DTT and cost-stress findings remain unchanged. Initial simulated capital ₹10,000; no orders or broker connectivity.
