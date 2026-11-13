# QHAP-TRADER — DhanHQ historical data onboarding (2026-11-13)

**State: CODE PREPARED; NO ACCOUNT OR DATA SUBSCRIPTION CONNECTED; NO REAL OR PAPER ORDERS.**

The user received a private written DhanHQ support reply on 13 November 2026 for **individual, noncommercial, private offline NSE cash-equity historical backtesting** and local retention. The customer-specific message, ticket ID, names, account details, and any future credentials **are not replicated in this public repository**. The provider support response is useful evidence for the specified private purpose; it is **not an independent ruling from NSE**, a blanket public redistribution license, approval for a commercial tool, or approval for real orders.

## Confirmed provider format and constraints

Source: [DhanHQ V2 Historical Data](https://dhanhq.co/docs/v2/historical-data/) and [Dhan Data API subscription](https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/).

- Historical 1-minute candles: `POST /v2/charts/intraday`, available for active instruments, using an account-specific Data API entitlement. No authenticated requests are made by this repository tool.
- Request uses `securityId`, `exchangeSegment: NSE_EQ`, `instrument: EQUITY`, `interval: 1`, `fromDate`, `toDate`; **maximum 90 calendar days per request**. The instrument ID must come from Dhan's official current security master; never guess.
- Returned columns are parallel `timestamp` (UNIX epoch seconds at candle **opening**), `open`, `high`, `low`, `close`, `volume`, and sometimes `open_interest`. A response may be direct data arrays or a `{status:'success',data:{...}}` SDK wrapper.
- Standard NSE regular session is treated structurally as **09:15 through 15:29 IST** (375 one-minute start times). This is a screening assumption, **not an independently verified holiday, special-session, halt, circuit, or instrument-specific calendar**.
- Dhan's support message says bonus/split adjustment is applied, but **not dividend or all point-in-time corporate action reconstruction**. Historical delisted-instrument coverage is not included in the stated active-instrument five-year product.
- The provider quoted a Data API subscription of ₹499 + GST (₹588.82 at 18%), a required Dhan Demat account, recurring 30-day renewals and cancellation control. Pricing and terms must be confirmed before any user purchase. Account opening, payment, or subscription **is not performed here**.
- Dhan did not grant unrestricted public display, publication of licensed raw bars, commercial usage or automated live trading. Their response about a custom WebSocket portal should **not** be interpreted as unrestricted virtual-trading or live execution approval.

## Local private intake — no network or token needed

The new [Dhan structure validator](../live_readiness/dhan_v2_private_minute_intake.mjs) works **only after the user has lawfully downloaded their own historical-data response into a local private file**, outside GitHub and outside shared folders. Do not paste API tokens, private OHLCV, account IDs or raw API responses into ChatGPT or GitHub.

1. Use a private local folder, e.g. `%USERPROFILE%\\QHAP-TRADER-PRIVATE\\dhan\\`. Keep all sensitive files there; do not `git add` them.
2. In `manifest.json` create the **exact** self-declared request manifest below. Replace the example dates and example `securityId` with values from the user-authorized Dhan request and verified instrument master. This manifest is for **development data intake only**; it cannot classify data as an untouched holdout.

```json
{
  "provider": "DHANHQ_V2",
  "dataClass": "USER_LOCAL_CANDLES_UNVERIFIED",
  "researchPurpose": "DEVELOPMENT_INTAKE_ONLY",
  "exchangeSegment": "NSE_EQ",
  "instrument": "EQUITY",
  "securityId": "1234",
  "intervalMinutes": 1,
  "fromDate": "2026-11-12",
  "toDate": "2026-11-12",
  "supportTicketReference": "USER_PRIVATE_DHAN_SUPPORT_REPLY_2026-11-13",
  "corporateActionTreatment": "BONUS_SPLIT_ADJUSTED_DIVIDENDS_UNKNOWN",
  "externalCalendarCertified": false,
  "sourceInstrumentMappingCertified": false
}
```

The `1234` ID and date above are **illustrative only**; no actual instrument entitlement or identity is established. Save the raw Dhan response in `response.json` locally, retaining the original parallel numeric candle arrays. Do not append a trading token to either file.

3. With Windows PowerShell, from the repository root, run:

```powershell
git pull --ff-only origin main
node --test .\projects\qhap-trader\live_readiness\test_dhan_v2_private_minute_intake.mjs

$root = Join-Path $env:USERPROFILE 'QHAP-TRADER-PRIVATE\dhan'
node .\projects\qhap-trader\live_readiness\dhan_v2_private_minute_intake.mjs --manifest (Join-Path $root 'manifest.json') --private-response (Join-Path $root 'response.json')
```

The program checks manifest scope and the 90-day bound **before** reading the private candle response; it validates array lengths, timestamp ordering and epoch alignment, IST regular-session minute range, finite OHLC prices, nonnegative integer volume, duplicate timestamps and calendar-date coverage. It prints **only safe counts, candidate date labels and SHA-256 fingerprints**—no prices, raw bars, provider credential, private file paths or instrument IDs. It never writes the data into GitHub or creates broker/network requests.

The result is unconditionally `NO_TRADE`, `canMakeEconomicEdgeClaims:false`, `completeHoldoutSessionsCertified:0`. Even a structurally complete 375-bar weekday is **not certified** until independently reconciled to an official trading calendar, instrument listing status, corporate actions, provider rights, source provenance and market-data revisions. Absence of weekday data cannot be presumed a holiday or a legitimate no-trade session.

## Non-negotiable future validation

- Preserve the **existing negative result** from the 204 inspected RELIANCE development daily bars; never rebrand those 2024 dates as unseen observations.
- Pre-register a genuinely untouched multi-year, three-regime, 60+ session holdout **with exact instruments and frozen code/fee versions before viewing new observations**. The current validator is deliberately development-only, not a holdout promotion gate.
- Verify dated historical brokerage/exchange tax schedules, instrument master validity across historical periods, corporate-action lineage (including excluded dividend adjustments), exchange calendars and complete minute session accounting.
- Report negative and abstention days, uncertainty intervals and 1×/2×/3× cost stress; compare an unmodified baseline and `NO_TRADE`.
- Do not assume a profitable trading edge, independently certified feed rights, approved paper feed, active Data API subscription, broker eligibility or any execution authority from a locally passing test.
- Do **not send QHAP-related emails** without separate approval for each specific outgoing message. Do not perform paid enrollment or enable live trading without explicit approval and separate externally verified readiness.

**Next practical dependency:** a user-owned Dhan account and specifically approved paid Data API subscription, followed by private authorized data export and true exchange-calendar/entitlement review. Until then the module can only be tested with synthetic fixtures, which are NOT trading evidence.
