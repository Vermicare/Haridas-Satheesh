# QHAP-TRADER — authenticated Upstox SANDBOX place, modify, cancel

**User-verified prerequisite:** 13 November 2026, Windows Node26 real sandbox test using the user's private token returned SANDBOX_PLACE_AND_CANCEL_CONFIRMED after one fake order and one fake cancel, 0 real orders. This established sandbox API ACK connectivity; not terminal order status or broker reconciliation.

Upstox [official sandbox API list](https://upstox.com/developer/api-documentation/sandbox/) enables **Place Order V3**, **Modify Order V3** and **Cancel Order V3**. [Modify V3](https://upstox.com/developer/api-documentation/v3/modify-order/) requires order_id, validity, price, order_type, and trigger_price. **Get Order Details is currently not on the documented sandbox-enabled list.** Do NOT infer that a cancellation ACK proves a terminal cancelled order, zero partial fills, or final account reconciliation.

The independent upstox_sandbox_modify_smoke.mjs is pinned to https://api-sandbox.upstox.com, never uses live URLs, and never accepts arbitrary host or market instrument inputs. It has no real-order route and never retries uncertain API requests. It tests a **fresh one-unit fake LIMIT BUY** at 9.12, then an attempted **fake modify** to 9.10, then exactly **one fake cancel**. If the modify fails but placement returned one unique order ID, it still attempts one cleanup cancel, without inventing success. No token or raw order ID is logged.

## From your existing PowerShell Git clone

First, verify the zero-network preview:

~~~powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main
node .\projects\qhap-trader\live_readiness\upstox_sandbox_modify_smoke.mjs --preview
~~~

To perform the actual **three fake sandbox mutation requests only**, use the **Sandbox Access Token** (not the historical Analytics Token) through a masked prompt on your local computer:

~~~powershell
$secure = Read-Host "Paste your UPSTOX SANDBOX Access Token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $env:UPSTOX_SANDBOX_ACCESS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  Remove-Variable secure,ptr -ErrorAction SilentlyContinue
}
try {
  node .\projects\qhap-trader\live_readiness\upstox_sandbox_modify_smoke.mjs --sandbox-modify-smoke --confirm-sandbox-only
} finally {
  Remove-Item Env:\UPSTOX_SANDBOX_ACCESS_TOKEN -ErrorAction SilentlyContinue
}
~~~

**Only when all three sandbox acknowledgements match**, expected sanitized status:

- SANDBOX_PLACE_MODIFY_CANCEL_ACKS_CONFIRMED
- placeAcknowledged: true, modifyAcknowledged: true, cancelAcknowledged: true
- terminalStatusIndependentlyVerified: false, finalFilledQuantityKnown: false
- realOrdersSent: 0, realOrderRoutePresent: false, canTradeRealMoney: false

If any request is rejected, times out, or returns a mismatched order ID, the script returns SANDBOX_PARTIAL_ACK_MANUAL_REVIEW or SANDBOX_PLACE_UNCONFIRMED_MANUAL_REVIEW with sanitized reason codes. It does **not** retry, assume a cancelled terminal status, use real funds, or promote a live strategy. This isolated smoke is not an unattended execution loop.

## Validation

~~~powershell
node --test --test-reporter=tap .\projects\qhap-trader\live_readiness\test_upstox_sandbox_modify_smoke.mjs
node .\projects\qhap-trader\live_readiness\operator_offline_preflight.mjs --offline-check
~~~

GitHub Actions uses only mock API responses and deliberately has no sandbox token or network request. Real-money trading remains **NO_TRADE** because Jan 2025 user-local RELIANCE strategy development experiments produced negative modeled after-cost results. User-reported verbal Upstox research approval covers historical analysis and read-only paper, not live execution. QHAP emails are prohibited without user approval.
