# QHAP-TRADER: Read-only quote evidence gate (2026-11-11)

## Motivation and real-world observed symptom

A user **locally** executed the separate QHAP-TRADER Upstox read-only quote diagnostic and reported this **sanitized** result:

- status: RECENT_SNAPSHOT_OLDER_LAST_TRADE_OBSERVATION_ONLY
- tradeAgeSeconds: 5
- snapshotAgeSeconds: 0
- reason: LAST_TRADE_OLDER_THAN_3_SECONDS
- tradesSent: 0; ordersPossible: false
- safeToUseForPaperExecution: false

The user did **not** disclose an Analytics Token, order, holding, live price, full market feed, raw timestamp, or bid/ask. This is **reported local output**, not an independently reproduced live vendor test by GitHub Actions.

[Upstox Full Market Quote V3 documentation](https://upstox.com/developer/api-documentation/get-full-market-quote-v3/) defines **timestamp** as response-generation time; **last_trade_time** is time of last completed trade. A just-generated REST response containing an older trade is not necessarily evidence of a stale network or an invalid token. Neither timestamp alone independently validates market book update recency. The original local QHAP strict adapter requires BOTH within 3 seconds and properly fails closed for simulated tick ingestion; do not silently change that requirement.

## What the new module actually does

quote_evidence_gate.mjs **only interprets a status-only diagnostic record**. It has **no networking, API, token, price, broker or storage code**, and never authorizes paper or live order execution. It separates:

- recent vendor response + older last trade = **observation-only research signal**, not an executable price;
- strict timestamp pass = **one-shot diagnostic pass only**, not a session or fill;
- stale, future, contradictory or otherwise failed status = **reject**;
- unknown/private fields or contradictory safety flags = **exception**, not a reinterpretation.

The function summarizeSanitizedObservations only counts previously sanitized statuses supplied by a caller; even a series cannot certify a streaming feed or exchange session. Do not mistake a REST response-generation timestamp for proof that best-bid/best-ask levels were freshly updated.

## How to test (Node.js 22+)

From repo root:

    node --test projects/qhap-trader/read_only_quote/test_quote_evidence_gate.mjs
    node projects/qhap-trader/read_only_quote/quote_evidence_gate.mjs --demo

The demo is a **synthetic fixture** with sample ages 0 and 5 seconds. The real 2026-11-11 user result is documented above for audit; **no real-time API call is performed here**.

GitHub Actions should pass all 17 standalone tests independently of Upstox availability. The existing local diagnostic is a separate package; keep the user's current client private and do not prompt for token in GitHub, automation, or chat.

## Next evidence requirements

1. Acknowledge local read-only authentication was established earlier; current case is not an Upstox 401/403.
2. Get license/terms confirmation for multi-observation research and avoid unnecessary vendor calls.
3. During verified NSE market session, obtain **authorized and timestamped book-update evidence** via a suitably documented read-only stream if Analytics Token supports the chosen endpoint. The REST quote response-generated time is not an exchange event sequence.
4. Verify continuity, clock offset, out-of-order/duplicate events, bid/ask liquidity and venue session exceptions, without using synthetic fills as actual prices.
5. Preserve genuine untouched holdout and at least 60 prospective complete paper-monitoring sessions, but only after the data quality gate. Separate explicit authorization would be needed for any live trading; **none is sought or granted**.

References: [Official Upstox Full Market Quote V3](https://upstox.com/developer/api-documentation/get-full-market-quote-v3/), [Upstox V3 Streaming Market Data](https://upstox.com/developer/api-documentation/v3/get-market-data-feed/).
