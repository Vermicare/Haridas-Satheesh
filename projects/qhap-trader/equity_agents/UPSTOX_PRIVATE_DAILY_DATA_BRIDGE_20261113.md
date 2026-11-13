# QHAP NSE agents — authenticated user-local Upstox daily development bridge

**13 November 2026.** The nine-agent NSE synthetic demonstration succeeded; its guardian correctly outputs NO_TRADE. This adds REAL daily historical data import under the user's local private data directory, outside public GitHub, as the next source-engineering milestone.

Official Upstox [Historical Candle V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) supports **days/1** for NSE equities, available from January 2000 with up to a decade per request. Our importer deliberately constrains a request to **365 calendar days** and 80–260 actual returned 1-day candles. It never fills missing dates or invents provider candles. No live/real broker order route, no paid model API, and no automatic retries.

## 1. Preview without credentials or a network request

Run in Windows PowerShell, after the PR is merged:

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main

node .\projects\qhap-trader\live_readiness\upstox_v3_private_daily_swing_development.mjs --preview --instrument 'NSE_EQ|INE002A01018' --symbol RELIANCE --from '2024-01-01' --to '2024-11-30'
~~~

Expect PRIVATE_DAILY_RESEARCH_PREVIEW_NO_NETWORK and requestsAttempted 0. This chosen window includes 2024 July data already inspected, so classify the whole window **DEVELOPMENT ONLY — NOT UNSEEN HOLDOUT**.

## 2. Optional user-local one-request historical download

Use your existing **Analytics Token**, not the Sandbox Access Token. Keep it entirely on your Windows computer. The token's account privileges are not independently verified, but the script itself has only a fixed, read-only historical GET endpoint and no broker order routes.

~~~powershell
$secure = Read-Host "Paste your UPSTOX Analytics Token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $env:UPSTOX_ANALYTICS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  Remove-Variable secure,ptr -ErrorAction SilentlyContinue
}

try {
  node .\projects\qhap-trader\live_readiness\upstox_v3_private_daily_swing_development.mjs --fetch-read-only-development --instrument 'NSE_EQ|INE002A01018' --symbol RELIANCE --from '2024-01-01' --to '2024-11-30' --confirm-private-research-only
} finally {
  Remove-Item Env:\UPSTOX_ANALYTICS_TOKEN -ErrorAction SilentlyContinue
}
~~~

If successful, expect PRIVATE_DAILY_DEVELOPMENT_STORED_AND_AGENT_RESEARCH_RUN, dailyBarsStored actual count, agentAuditValid true, agentDecision NO_TRADE, realOrdersSent 0, and the local private file:

    $env:USERPROFILE\QHAP-TRADER-PRIVATE\equity_daily\development-RELIANCE-2024-01-01-to-2024-11-30.json

**Do not share that daily data file, prices, or token in chat, GitHub or email.** Only share the sanitized JSON result. File already exists? Fail before making any provider request to avoid overwrite. A partial local write error? Stop, inspect locally, never delete source blindly. The digest is for local file integrity, not authenticated stock-exchange provenance.

## 3. Review the nine-agent explanations without a token

~~~powershell
$file = Join-Path $env:USERPROFILE 'QHAP-TRADER-PRIVATE\equity_daily\development-RELIANCE-2024-01-01-to-2024-11-30.json'
node .\projects\qhap-trader\live_readiness\nse_swing_interdependent_agent_network.mjs --private-replay "$file"
~~~

This is STILL nine deterministic local roles, NOT independently running paid Claude/GPT assistants or a strategy that has proven profitability. The data source is Upstox, but corporate-action adjustments, dividends, all exchange-calendar exceptions, book fill prices, venue fees, account trading terms, and written data redistribution rights have not been independently verified. Candidate research WATCH always results in finalDecision NO_TRADE, zero paper and real orders.

Official Upstox fee reference: https://upstox.com/brokerage-charges/ — equity delivery ₹20 per executed order plus ₹20 per-scrip/per-day DP sell fee, STT on both sides, GST, exchange/SEBI/stamp, potential account plan exceptions. The DAILY agent's current ₹70 hypothetical roundtrip fee assumption is NOT a validated contract-note schedule; the synthetic 328bps / 984bps stress was NOT observed future market profit.

## Next priorities

- P0: accurate Upstox **DELIVERY** fee/DP/STT/stamp/GST/SEBI model (currently only indicative), date-aware primary-source evidence.
- P0: corporate-action and calendar validity, prospective hypothesis freeze BEFORE accessing a distinct untouched evaluation period, 60+ truly unseen dates and three characterized regimes.
- P1: instrument selection, conservative swing portfolio/overnight gap/position ledger, passive ETF and NO_TRADE comparison, real bid/ask/spread when licensed and available.
- P1: optional multi-LLM research council independent of deterministic risk engine, only after separate informed approval of any model inference costs, public-only permitted inputs, no external licensed candles.
- No real-money broker integration or AI-directed trading without independent profitability and explicit separate user authorization.

**QHAP-specific email policy** remains no send/reply/forward/resend without specific prior approval for each email. No QHAP emails are involved.
