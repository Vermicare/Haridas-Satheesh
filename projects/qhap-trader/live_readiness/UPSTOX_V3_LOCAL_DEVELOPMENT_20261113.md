# QHAP-TRADER — Upstox V3 local historical development import (13 Nov 2026)

**State:** One read-only API request per run; private local files; development-only. No live order routes, subscriptions, emails or trading. The user reports Upstox verbally approved private historical backtesting and read-only live-feed paper simulation. This report preserves that as **user-attested verbal permission**, not an independently obtained written broker/exchange licence.

## What this fixes

The frozen February 2021 guarded engine cannot handle new 2022+ data; the separate chronology-first offline simulator can, but did not have an Upstox adapter. The new [upstox_v3_private_history.mjs](upstox_v3_private_history.mjs) requests exactly one historical 1-minute NSE cash-equity calendar-month window using Upstox's strictly **read-only Analytics Token**, normalizes minute timestamps and prices, validates individual rows and chronological uniqueness, and creates the existing simulator's nine-column CSV schema. Data stays outside GitHub by default.

The [official Upstox V3 historical candle API](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) documents 1-minute bars from January 2022 with a one-month request limit. The [official Analytics Token](https://upstox.com/developer/api-documentation/analytics-token/) is free and strictly read-only, unlike a trading-capable OAuth token. This script does **not** use a trading token or SDK, call order endpoints, fetch a live feed, or print secrets/candle prices.

## Windows PowerShell — actual developer-sample download

Run from the existing Git repository, with Node 26 already installed. If an Analytics Token does not yet exist, generate one from Upstox Developer Apps > Analytics; keep it on your machine. The example RELIANCE instrument key comes from [the Upstox instrument directory](https://upstox.com/developer/api-documentation/instruments/). The date window is **a development sample and is ineligible as untouched holdout evidence**.

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main

$secure = Read-Host "Paste the Upstox READ-ONLY Analytics Token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $env:UPSTOX_ANALYTICS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  Remove-Variable secure,ptr -ErrorAction SilentlyContinue
}

try {
  node .\projects\qhap-trader\live_readiness\upstox_v3_private_history.mjs --instrument 'NSE_EQ|INE002A01018' --symbol RELIANCE --from 2025-01-06 --to 2025-01-10
} finally {
  Remove-Item Env:\UPSTOX_ANALYTICS_TOKEN -ErrorAction SilentlyContinue
}
~~~

The token temporarily exists in the environment of this PowerShell session/child process, then is cleared by the finally block. Never paste it into ChatGPT, GitHub, a command argument, or email. The data is stored privately in the user home directory:
- Home/QHAP-TRADER-PRIVATE/historical/YYYY/MM/DD/SYMBOL.csv
- Home/QHAP-TRADER-PRIVATE/manifests/development-RELIANCE-2025-01-06-to-2025-01-10.json
- A separate local audit JSON for original CSV SHA-256, missing minutes, unknown weekdays, and authorization/provenance limitations.

Each previously absent weekday is recorded as **unknown** rather than silently a no-trade session (could be official holiday, suspension or missing vendor coverage). The importer refuses duplicate/out-of-range/invalid prices, unexpected IST timestamps, zero-volume sessions, weekends without an exception calendar, and overwriting existing private files. A day is a **candidate** only if **all 375 opening timestamps from 09:15 through 15:29 IST** are present; actual source/calendar/fill validity remains unverified.

## Offline costed experimental replay

Only if the import reports candidateCompleteDays > 0:

~~~powershell
$private = Join-Path $env:USERPROFILE 'QHAP-TRADER-PRIVATE'
$prices = Join-Path $private 'historical'
$manifest = Join-Path $private 'manifests\development-RELIANCE-2025-01-06-to-2025-01-10.json'
node .\projects\qhap-trader\experiments\intraday_clock_replay.mjs $prices $manifest 15
~~~

The existing simulator evaluates historical candles locally with FAST, ONE, TIME_MOMENTUM_GATE, and NO_TRADE policies. It resets hypothetical equity each symbol-day, uses indicative 2026 Zerodha-like fee assumptions rather than actual Upstox/historical contract notes, and cannot certify intraminute fills or positive expected returns. Its outcome is a **development-only hypothesis test**, not real financial profits or permission for real orders.

## Testing and provenance

~~~powershell
node --test --test-reporter=tap .\projects\qhap-trader\live_readiness\test_upstox_v3_private_history.mjs
node .\projects\qhap-trader\live_readiness\operator_offline_preflight.mjs --offline-check
~~~

GitHub Actions runs **synthetic** provider-shaped candle and mock-fetch tests, never authenticates or downloads an actual user's Upstox data. The new API adapter never puts prices, tokens or broker details in GitHub. The next parallel engineering path is the authorized-by-phone read-only V3 WebSocket feed with strict event freshness and a separate, explicitly non-executable hypothetical ledger.

**The external research permission is user-attested, not independently verified in writing. No additional email should be sent from QHAP without the user's approval.** Real-money trade execution, paid data, broker account changes and guaranteed daily gains are excluded.
