# QHAP-TRADER — Private multi-year Upstox historical development batch

**13 November 2026.** User has already validated actual Upstox historical one-minute import and authenticated fake Sandbox order placement/modification/cancellation. This workflow advances the **financial strategy evidence**, rather than repeating sandbox smoke tests.

**Classification:** **EXPLORATORY DEVELOPMENT DATA ONLY**. The purpose is to see whether the losing January 2025 RELIANCE strategies fail over additional market years. Do **not** represent these results as pre-registered unseen 60-day / three-regime holdout evidence; inspecting them consumes their independence for future testing. A calendar year is not itself proof of a distinct market regime.

Upstox's official [Historical Candle V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) offers one-minute data from January 2022, with a **maximum one calendar month per call**. This script uses the previously working read-only Analytics Token endpoint, not the trading-capable OAuth token, and never accesses the fake-order sandbox or live broker routes.

## Offline preview first (zero network and zero credentials)

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main

node .\projects\qhap-trader\live_readiness\upstox_v3_multiwindow_development.mjs --preview --instrument 'NSE_EQ|INE002A01018' --symbol RELIANCE --months '2022-07,2023-07,2024-07,2025-07'
~~~

Expected preview: PREVIEW_READ_ONLY_DEVELOPMENT_MULTIYEAR_NO_NETWORK. Four selected calendar months, one per year, comprise the proposed **development-only** windows. They are not statistically validated distinct market regimes. The script permits **two to four unique ascending months** in a single invocation. It does not fetch data in preview.

## Actual user-local read-only historical import

You already created a read-only **Analytics Token** for the January 2025 import. Use that token on your own Windows computer; **do not paste it here**. This is NOT the 30-day Upstox Sandbox Access Token and not a trading API credential.

~~~powershell
$secure = Read-Host "Paste your Upstox READ-ONLY Analytics Token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $env:UPSTOX_ANALYTICS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  Remove-Variable secure,ptr -ErrorAction SilentlyContinue
}

try {
  node .\projects\qhap-trader\live_readiness\upstox_v3_multiwindow_development.mjs --fetch-development --instrument 'NSE_EQ|INE002A01018' --symbol RELIANCE --months '2022-07,2023-07,2024-07,2025-07' --confirm-read-only-private-import
} finally {
  Remove-Item Env:\UPSTOX_ANALYTICS_TOKEN -ErrorAction SilentlyContinue
}
~~~

Expected when all four read-only requests succeed: DEVELOPMENT_MULTIYEAR_BATCH_LOCAL_ONLY_COMPLETE. The script makes up to **four sequential GET requests**, one per calendar month, separated by ~1.2 seconds, with no automatic retries. It fails closed and reports which month stopped on error. **Do not immediately rerun after a partial failure**, because the earlier private monthly source files are intentionally never overwritten. The script reports aggregate counts, source integrity unknown-weekday flags, and a **private combined manifest**; no token, raw price or HTTP body is printed.

The local combined manifest path ends with:

~~~text
QHAP-TRADER-PRIVATE\manifests\development-multiwindow-RELIANCE-2022-07_to_2025-07.json
~~~

Raw candles remain entirely within the user's home directory under QHAP-TRADER-PRIVATE/historical/YYYY/MM/DD/RELIANCE.csv, **outside** the Git clone, not on GitHub.

If the output shows candidateCompleteDays > 0 and a combined manifest path, run the existing **offline** costed exploratory simulator at 5, 15 and 30 basis points slippage per side:

~~~powershell
$root = Join-Path $env:USERPROFILE 'QHAP-TRADER-PRIVATE\historical'
$manifest = Join-Path $env:USERPROFILE 'QHAP-TRADER-PRIVATE\manifests\development-multiwindow-RELIANCE-2022-07_to_2025-07.json'

foreach ($bps in @(5, 15, 30)) {
  Write-Host "=== $bps basis points per side ==="
  node .\projects\qhap-trader\experiments\intraday_clock_replay.mjs $root $manifest $bps
}
~~~

The simulator currently uses **illustrative 2026 Zerodha-like fees**, not authenticated date-accurate Upstox contract note fees, and assumes minute-level prices that are not executable-book evidence. It resets imaginary capital for every symbol-day; do not add its outcomes as if they were a single compounded real-money account. Report all policies, negative results, source gaps and sensitivities; **do not optimize parameters after seeing these months and then call them an untouched holdout**.

## Previously saved local minute data — no token and no new download

The original 13 Nov importer unintentionally checked **09:16–15:29** (374
minutes) when assigning `CANDIDATE_COMPLETE_UNVERIFIED`; it did not require
the **09:15 opening minute**. This has been corrected without changing the
strategy's frozen **09:16-first feature window** or modifying existing private
source files. Before trusting an older local manifest, run the new
aggregate-only, read-only audit:

~~~powershell
node .\projects\qhap-trader\live_readiness\reaudit_existing_private_upstox.mjs --audit-local
~~~

The command scans the existing private `*.audit.json` metadata and matching
local source CSV files, checks their original SHA-256, requires the full
375-minute source-day shape, and reports only affected date labels and counts.
It **does not** need an Analytics Token, make a network request, modify a
saved manifest, load daily swing files, or publish raw candles. If
`staleCandidateLabels` is positive, treat those historical `eligible`
manifest entries as **stale** until corrected externally; the replay parser
now rejects missing openings rather than silently accepting such entries.
A structurally complete day still lacks independent official-calendar,
corporate-action, licensed-use and actual-fill certification.

## Continuing toward live readiness

- Actual Upstox sandbox order place/modify/cancel acknowledgements: **complete**, user confirmed 0 real orders.
- True final sandbox order status/fills: **not independently available from currently documented sandbox order API subset**.
- Private read-only market-history engineering: functional; this batch extends test dates if the user runs it.
- Forward read-only live-data paper trading and untouched, precommitted, multi-year holdout with independently verified after-cost robustness: **pending**.
- Real-money order execution: **disabled**. Historical losses at all tested slippage assumptions make NO_TRADE the better current policy.

QHAP-only project rule: **No sending, replying, forwarding or resending email without express user approval for the message and recipients**. No email is sent as part of this workflow. Never store tokens or market candles in GitHub, ChatGPT or shared files.
