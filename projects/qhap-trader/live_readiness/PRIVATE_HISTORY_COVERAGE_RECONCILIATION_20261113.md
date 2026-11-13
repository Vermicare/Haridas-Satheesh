# QHAP-TRADER — private historical source-coverage reconciliation

**13 November 2026 — after the user's real Upstox RELIANCE July 2022/2023/2024/2025 read-only import and 84-date backtest.**

This tool reconciles **only private local audit JSON metadata** against the combined **date/symbol-only manifest**. It never reads the underlying licensed one-minute candle CSV, broker accounts or credentials; it uses no API calls. This is a **data-quality and selection-bias check**, not a profitable-strategy test.

## Why the exclusion audit matters

The user ran an audit that identified exactly these **incomplete** 2023 source sessions:

| Day | Missing required 09:16–15:29 bars | First missing |
|---|---:|---|
| 2023-07-12 | 1 | 14:57 |
| 2023-07-20 | 44 | 09:16 |
| 2023-07-24 | 3 | 12:49 |

The single missing weekday in July 2024 was **2024-07-17**. This is an official NSE capital-market **Moharram** trading holiday, per circular [NSE/CMTR/59722, issued 12 December 2023](https://nsearchives.nseindia.com/content/circulars/CMTR59722.pdf). This specific pinned holiday is independently evidenced; this tool **does not assume every other exchange date/calendar/exception is verified**.

Across these four selected months, there were **88 weekdays**: one verified exchange holiday and three incomplete one-minute sessions means **84 candidate-complete days out of 87 calendar-expected regular trading weekdays**, approximately **96.55% coverage**. The remaining 2023 source totals **7,826 of an illustrative 7,875 possible one-minute slots**. Exactly **48 missing required 09:16–15:29 minutes** are documented; the one remaining absent minute would be an **09:15 bar** if the provider's standard 375-slot regular-session convention applies. Its exact date is not shown by the abbreviated original audit and must not be fabricated.

**Crucial:** A prior replay returned `excluded: []` because its input manifest had already filtered to the 84 eligible days; that does **not** mean the downloaded source contained no gaps. These exclusions must accompany **every comparison**. No forward filling, no manufactured zero profit days, and no false claim of complete exchange-original tick coverage.

## Windows command (no token required)

Run after pulling GitHub main, from the existing repo:

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main

node .\projects\qhap-trader\live_readiness\private_history_coverage_reconcile.mjs --audit-private-development
~~~

Expected when local file counts match: `PRIVATE_METADATA_COVERAGE_RECONCILED_NOT_PROFIT_EVIDENCE`. The program reads only:

- `QHAP-TRADER-PRIVATE/manifests/development-RELIANCE-YYYY-07-01-to-YYYY-07-31.audit.json` for the four selected July years
- `QHAP-TRADER-PRIVATE/manifests/development-multiwindow-RELIANCE-2022-07_to_2025-07.json` containing only eligible dates/symbols

The summary reports the known excluded sessions, counts of required-minute gaps and optional 09:15 gaps, known calendar closures, unresolved absent weekdays, and checks whether the date-only manifest matches the source audits exactly. It never prints price rows, hashes, tokens or user-specific secrets.

If the program returns `PRIVATE_COVERAGE_AUDIT_BLOCKED`, stop: the local audit/manifest identity or calendar accounting is inconsistent and no performance certification is permitted from that source until investigated. Do not overwrite original source files.

## Why the test can pass without proving trading readiness

CI uses handcrafted fake audit metadata. The actual user's local result is needed to independently establish the date-only sample selection. This check **does not** certify all trading holidays, exchange time stamps, corporate actions, licensed redistribution rights, real-world fills, realistic Upstox contract note fee model, out-of-sample profitability or positive edge.

Current live-release decision remains **NO_TRADE**: the user-observed 84-day development evidence already showed FAST, ONE and TIME_MOMENTUM_GATE negative at 5, 15 and 30 basis points of slippage per side. The authenticated Upstox SANDBOX place/modify/cancel acknowledgements prove fake API mechanics only. No actual live order routing or funds are used.

**QHAP email rule:** no sending/replying/forwarding/resending email without the user's approval for that specific message and recipients.
