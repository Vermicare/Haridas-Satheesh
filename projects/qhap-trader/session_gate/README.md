# QHAP-TRADER — Offline NSE 2026 read-only probe session gate

**Stage: deterministic, tested offline helper; no live market access or real orders.**

The user reported a successful read-only Upstox Analytics Token status-only HTTP 200 request on 2026-11-10. That establishes user-reported authenticated connectivity but **does not establish a fresh quote, market availability, legal market-data rights, or profitable trading**.

This gate blocks candidate read-only quote tests on NSE published 2026 equity holidays, weekends, unsupported years, and outside a buffered test window.

## Published exchange reference

- Official first-party source: https://www.nseindia.com/resources/exchange-communication-holidays
- Verified for the 2026 equities calendar on 2026-11-10.
- NSE regular cash-equity session is 09:15 to 15:30 **IST**.
- **Our conservative probe window (not an exchange rule): 09:30 inclusive to 15:00 exclusive.**
- 2026-11-10 (Diwali Balipratipada) is a published holiday; November 11 is the next scheduled regular weekday.
- Sunday 2026-11-08's exceptional Muhurat session is deliberately not whitelisted.
- A published calendar is **not actual exchange session attestation**; independent updates, halts, session changes, venue rights and vendor feed freshness still require separate verification.

## Run offline (Node 22+)

From repository root on Windows PowerShell:

    node .\projects\qhap-trader\session_gate\nse_2026_probe_gate.mjs --now
    node --test .\projects\qhap-trader\session_gate\test_nse_2026_probe_gate.mjs

On Unix:

    node projects/qhap-trader/session_gate/nse_2026_probe_gate.mjs --now
    node --test projects/qhap-trader/session_gate/test_nse_2026_probe_gate.mjs

The output never includes an API key, prices, balances or broker instructions.

- VERDICT=ABSTAIN: do not attempt the read-only quote test.
- VERDICT=ONE_READ_ONLY_PROBE_MAY_BE_ATTEMPTED: scheduled date/time merely permits a **manually controlled single read-only data check**, subject to exchange circular changes and data-use rights.
- Under **no circumstance** does this authorize real or simulated orders, certify live market access, or count as a completed forward paper-trading session.

## User's next market-session check

On Wednesday 2026-11-11 between 09:30 and 14:59 IST, recheck authoritative NSE session announcements. Run the offline gate locally. Only if it permits, use the separate **existing on-device** QHAP-TRADER Upstox read-only V3 adapter for a single symbol (example NHPC: instrument NSE_EQ|INE848E01016, symbol NHPC). The user has already generated a private Analytics Token; **never paste it in chat or commit it to GitHub**.

The adapter is a separate local package; this repository gate deliberately neither requests the token nor automates the read-only request. The safe user output is a sanitized status only, such as ONE_READ_ONLY_QUOTE_VALIDATED_NOT_A_SESSION, or the specific redacted failure code.

## Boundaries

No order APIs, credential persistence, paid calls, private market-data storage, live session certification or trading authority. All source and user test results remain subject to independent verification. For any market session in 2027 or special session, create a separately reviewed and sourced calendar, rather than silently allowing unsupported dates.
