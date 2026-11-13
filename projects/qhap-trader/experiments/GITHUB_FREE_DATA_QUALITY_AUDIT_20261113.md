# QHAP-TRADER — publicly reachable GitHub market-data quality audit (2026-11-13)

**Result: NO certifiable external GitHub minute-data source yet. NO_TRADE.**
This is a source-integrity and policy-screening report, **not a recommendation
to scrape, bulk download, redistribute, trade from or commercially reuse
market data of uncertain provenance**. Dhan subscription is unavailable;
do not ask the user to purchase one or presume a paid plan is necessary for
safe offline development.

## 1. What exists in our owned GitHub

A connected-repository tree inspection of
[`Vermicare/Haridas-Satheesh`](https://github.com/Vermicare/Haridas-Satheesh)
on 13 Nov 2026 found **no stored original NSE-equity minute-price CSV/Parquet
dataset**. Existing `experiments/evidence` JSON is a **sanitized aggregate**
from previous *private* Upstox observations, not a downloadable price history.
The separate `Vermicare/QHAP` repository is the Bitcoin project.
Do **not** upload provider or third-party candles or private tokens to either
public repository.

## 2. Three independently inspected *public GitHub* file specimens

Read each `RELIANCE.txt` file in the GitHub connector in memory and counted
CSV rows, time stamps and basic OHLCV structure. All source values were
discarded after the aggregate audit; no prices are reproduced here.

| Unverified source file | Git blob SHA | Total rows | 09:15–15:29 IST minutes | Missing regular minute | Outside regular session |
|---|---|---:|---:|---|---|
| [2021-02-01 RELIANCE](https://github.com/gsidhu/nse-intraday-data/blob/main/2021/FEB/01FEB/01FEB/RELIANCE.txt) | `14d4da9a63ea5885651e81a2d162a18781baba8c` | 380 | 374 of 375 | **09:15** | 1 pre-open, 5 after 15:29 |
| [2022-01-03 RELIANCE](https://github.com/gsidhu/nse-intraday-data/blob/main/2022/JAN/03JAN/03JAN/RELIANCE.txt) | `81f02c6601567c6dcc7b5e8a8891f981d72ea14c` | 380 | 374 of 375 | **09:15** | 1 pre-open, 5 after 15:29 |
| [2023-01-02 RELIANCE](https://github.com/gsidhu/nse-intraday-data/blob/main/2023/JAN/02JAN/02JAN/RELIANCE.txt) | `21aeaae10f60225f4f7dd6651cdc9849ba4804c6` | 379 | 374 of 375 | **09:15** | 1 pre-open, 4 after 15:29 |

For these specific three specimens, duplicate intraday minute stamps and
plain OHLCV value-shape errors were not observed by the bounded check. They
**neither establish** archive-wide completeness **nor** exchange authenticity,
contractual research rights, instrument events, dated historical execution
costs, ticks, actual fill prices or a valid trading result. In particular,
the missing **opening 09:15** minute makes these dates **unsuitable as
complete opening-range strategy evidence**. Never silently fill missing
prices, shift 09:16 to 09:15, or use pre-open/after-close trades as regular
session execution evidence.

The third-party README describes its files as intended for backtesting and
claims an MIT license, but the repository's **root LICENSE path was absent
when checked**. A repository license, even if present, does **not** itself
establish the author had permission to redistribute upstream NSE market
data. Treat the source as **UNVERIFIED** for our use.

## 3. Other GitHub candidate — broader claim but unverified completeness

[`voletiramu/nse-fno-1min-data` release v1.0.0](https://github.com/voletiramu/nse-fno-1min-data/releases/tag/v1.0.0)
offers a public ~464 MB compressed asset described as 214 cash-stock
one-minute histories from April 2024 to April 2026, sourced from Zerodha
Kite. No archive extraction, provider authentication or licensing audit was
performed. Its README asserts *approximately 5.5 million bars*.

**Internal coverage plausibility red flag:** even an illustrative 500 full
375-minute trading sessions for 214 stocks would contain about
`214 × 500 × 375 = 40,125,000` bars. Conversely, 5.5 million bars for
214 symbols represent only ~68.5 full 375-minute stock-sessions per symbol on
average. This is **not proof that the ZIP is corrupt**: the README counts
may be approximate, coverage may vary or the declared window may only bound
the collection. It **is reason to withhold any assumption of uniform
two-year per-stock completeness** until the actual files, per-stock year/date
histograms and provenance are independently checked under lawful terms.

[`technovusin/nifty50-historical-data`](https://github.com/technovusin/nifty50-historical-data)
contains year-separated NIFTY50 index candles including 2024, but
the **nontradable index** is not a substitute for licensed NSE_EQ stock
execution evidence or symbol-specific liquidity. Its README acknowledges
special sessions, data cleaning, and missing minutes.

## 4. Source-rights boundary

The [official NSE Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy)
reserves original market-data ownership and restricts redistribution without
the relevant agreements. A public repository or a third-party MIT statement
cannot substitute for independent permission to use provider-origin candles
for this particular application, or to run live-feed virtual trading. Do not
assume licensing based on public downloadability or silent GitHub reads.
Paper and live execution remain forbidden without explicit relevant rights
and approvals.

## 5. Actually free, provider-authenticated path

Use the **existing**, user-local Upstox V3 read-only ingestion code rather
than buying Dhan data:
- [Official free Analytics Token](https://upstox.com/developer/api-documentation/analytics-token/):
  one-year read-only token, incapable of placing orders.
- [Official Upstox V3 historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/):
  **one-minute history available from January 2022**, maximum one month per
  request for 1–15 minute intervals.
- Existing QHAP private importer and
  [operator guide](../live_readiness/UPSTOX_V3_LOCAL_DEVELOPMENT_20261113.md):
  data stays outside GitHub and chat, only on the user's own machine.
  Prior Upstox RELIANCE observations were inspected development data and
  already failed to establish post-cost edge. Those dates cannot become
  fresh holdout data by reimport.

Upstox's free access and no-order token do **not** automatically establish
full NSE data license, virtual-paper-feed rights or positive trading edge.
An actual user-owned Upstox app/Analytics Token and corresponding written
rights remain subject to verification. No current user credentials or source
observations are available to this GitHub CI job.

## 6. New local quality audit for a legally obtained specimen

The [`audit_public_third_party_minute_csv.mjs`](../live_readiness/audit_public_third_party_minute_csv.mjs)
is an **offline local-file-only** inspector for the 9-column archive shape:
`SYMBOL,YYYYMMDD,HH:MM,O,H,L,C,V,OI`.
It validates the expected single date/symbol, finite positive OHLC, nonnegative
integer volume, duplicate minute time stamps, regular-session minute coverage,
the 09:15 open, 15:29 close, off-session data and weekend review. It accepts
no network URL, API token, paid subscription, order route or strategy.
Output contains only aggregate counts, date/symbol alias and local hash—no
raw prices, file paths or credentials. It **never upgrades** an unverified
third-party sample to licensed, unseen, tradeable data.

On Windows PowerShell, after `git pull --ff-only origin main`,
an already-lawfully obtained single-day copy may be checked offline:

```powershell
node .\projects\qhap-trader\live_readiness\test_audit_public_third_party_minute_csv.mjs
node .\projects\qhap-trader\live_readiness\audit_public_third_party_minute_csv.mjs --file "$env:USERPROFILE\QHAP-TRADER-PRIVATE\external\RELIANCE.txt" --symbol RELIANCE --date 2022-01-03
```

The quoted file path is illustrative and **no such user-local file was
created by this work**. No public-source bulk acquisition is programmed
into QHAP-TRADER.

**Next usable step:** continue *authorized private* Upstox historical
development with strict time/window and source-provenance checks; pre-register
a new untouched multi-year, three-regime 60+ distinct-session holdout **before**
viewing any new holdout data; pin actual current simulator/fee code and legal
rights. Keep historical sample leak controls, the independently negative
204-day prior RELIANCE research result, 1×/2×/3× friction stress, separate
60-day forward feed audit and `NO_TRADE` as hard boundaries.
