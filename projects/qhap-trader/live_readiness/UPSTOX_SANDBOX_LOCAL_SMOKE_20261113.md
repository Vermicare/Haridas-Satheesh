# QHAP-TRADER — Upstox SANDBOX-only order smoke test

**13 November 2026. User created a free Upstox Sandbox App and has a private Sandbox Access Token.** This is separate from the read-only Upstox Analytics Token used for historical candles. Do NOT share the Sandbox Token, App Secret or API Key in chat, GitHub issues, screenshots or command-line arguments.

Official sources:
- [Upstox Sandbox API](https://upstox.com/developer/api-documentation/sandbox/): free, sandbox token valid 30 days, fake orders cannot place real trades
- [Upstox official Python SDK configuration](https://github.com/upstox/upstox-python/blob/master/upstox_client/configuration.py): sandbox host https://api-sandbox.upstox.com; allowlisted /v3/order/place, /v3/order/modify, /v3/order/cancel
- [Place Order V3](https://upstox.com/developer/api-documentation/v3/place-order/), [Cancel Order V3](https://upstox.com/developer/api-documentation/v3/cancel-order/)

## What this deliberately does and does not do

The isolated [upstox_sandbox_smoke.mjs](upstox_sandbox_smoke.mjs) has exactly one pinned network host: https://api-sandbox.upstox.com. There is **no live fallback, alternate host, broker login, real-money order route, or auto-retry**. The script uses a hardcoded, one-share, delivery-product, LIMIT BUY fake test order (₹9.12 limit) with official Upstox sandbox example instrument NSE_EQ|INE669E01016. The price and instrument are for sample payload testing, **not investment recommendations**.

Two modes:
- **--preview**: no token needed, zero network and zero orders.
- **--sandbox-smoke --confirm-sandbox-only**: requires local *Sandbox Token*, sends exactly one fake sandbox place request and, if a single identifiable order ID comes back, attempts one fake sandbox cancel request. No live order transmission is possible by this script.

The script reports sanitized status, request counts, a one-way short order fingerprint (not raw ID), and a bounded error category if the fake order was not confirmed cancelled. **Never retry automatically**: a lost or malformed response might conceal an accepted fake order in the sandbox.

## Windows PowerShell commands

Run from existing clean repository and first do network-free preview:

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main

node .\projects\qhap-trader\live_readiness\upstox_sandbox_smoke.mjs --preview
~~~

This should print SANDBOX_ONLY_PREVIEW_NO_NETWORK. For an actual fake sandbox place-and-cancel smoke, paste the **Sandbox Access Token** locally in a masked input:

~~~powershell
$secure = Read-Host "Paste Upstox SANDBOX Access Token (NOT Analytics Token)" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:UPSTOX_SANDBOX_ACCESS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Variable secure,ptr -ErrorAction SilentlyContinue
}

try {
    node .\projects\qhap-trader\live_readiness\upstox_sandbox_smoke.mjs --sandbox-smoke --confirm-sandbox-only
} finally {
    Remove-Item Env:\UPSTOX_SANDBOX_ACCESS_TOKEN -ErrorAction SilentlyContinue
}
~~~

**Expected if both simulated broker requests succeed:**

~~~json
{
  "status": "SANDBOX_PLACE_AND_CANCEL_CONFIRMED",
  "mode": "UPSTOX_SANDBOX_ONLY_NO_REAL_FUNDS",
  "sandboxOrdersAttempted": 1,
  "sandboxCancelsAttempted": 1,
  "realOrdersSent": 0,
  "realOrderRoutePresent": false,
  "canTradeRealMoney": false,
  "tokenPrinted": false
}
~~~

A real API response may instead report a rejected test instrument/price, expired token, or failure to cancel. **Do not infer success unless the returned JSON says both are confirmed.** In that case, share the sanitized JSON output only (no raw token, order details, headers or screenshots with credentials). We can then adapt the sandbox-only test payload.

## Verification and restrictions

~~~powershell
node --test --test-reporter=tap .\projects\qhap-trader\live_readiness\test_upstox_sandbox_smoke.mjs
node .\projects\qhap-trader\live_readiness\operator_offline_preflight.mjs --offline-check
~~~

GitHub Actions uses mock responses only and no sandbox token. No real broker accounts, live market data, funds or emails are used in automated CI.

**Trading strategy remains NO_TRADE for real money.** The existing January 2025 five-day RELIANCE historical development run showed every tested trading policy lost after illustrative costs. The sandbox is for API integration readiness, not permission to deploy an unprofitable strategy.

**Project email policy:** Never send, reply, forward or resend QHAP emails without explicit approval of the specific email and recipients from the user.
