# QHAP-TRADER live-trading readiness — go/no-go record (12 November 2026)

**Decision: NO-GO. Real orders OFF. Capital transferred ₹0.** User wants a real-trading-capable end product; code upgrades are permissible without account credentials, placing real orders, or switching to funded execution. Engineering progress does not independently establish suitability to use real funds.

## Current evidence (facts, assumptions and unresolved external dependencies)

| Release gate | Current evidence | Decision |
|---|---|---|
| Read-only data transport | User-reported Upstox Analytics Token V3 WebSocket, decoded messages and 60-sec feed-health window | TECHNICAL PASS, limited |
| Integrated experiment | User-local 15-minute read-only NHPC stream; 723 decoded frames; 5 virtual fills, unrealized open position, final indicative equity ₹9,975.04 from ₹10,000 | EXPERIMENT ONLY |
| Historical strategy economics | Previous exploratory 34 separate ACC/RELIANCE stock-day 2021–23 one-minute proxy: at 15bps extra slippage/side FAST −₹1,674.39, ONE −₹242.99, TIME_GATE −₹17.57, NO_TRADE ₹0 | **FAIL: no demonstrated after-cost edge** |
| Historical data provenance | Community third-party 2021–23 data; missing-minute sessions excluded; rights and exchange fidelity not independently certified | BLOCKED |
| Actual NHPC cross-regime holdout | No appropriately licensed pristine multi-regime NHPC history with executable fills | BLOCKED |
| 60 complete prospective sessions | Only one reported short 15-minute user-local pilot and short transport/preflight checks | BLOCKED |
| Real broker trading account authorization | No independently verified eligible Upstox account or trading API app; Upstox Analytics Token is read-only | BLOCKED |
| Static egress IP | Broker-whitelisted client-specific static IP not verified | BLOCKED |
| Registration and order tagging | Applicable NSE/SEBI/Upstox 2026 client-direct API / algorithmic-trading obligations not confirmed for this account/strategy | BLOCKED |
| Broker order price bands/tick, limits, charges | Upstox order-specific metadata and actual ledger fees/margins/fill-price rules not independently certified | BLOCKED |
| Persistent order state & replay | A new MOCK-only order state machine models partial fills/cancels/dup IDs; no durable broker-authoritative reconciliation | BLOCKED |
| Kill switch, cancellation, mandatory square-off | Pure paper pretrade guard exists; independent broker-side emergency actions / persistent alerts / outage recovery not implemented | BLOCKED |
| Production operations & independent security | No audited deployment, secrets vault, failover, real broker reconciliation or supervised runbook | BLOCKED |
| Written owner + independent sign-off | None supplied or verified; self-claims must not grant readiness | BLOCKED |

## Work done in PR #51
- **Pure non-executable release gate:** refuses to claim live readiness even when all mandatory points are self-reported green. No credentials, HTTP, broker SDK, trading endpoints or live-order ability.
- **Pure paper-intent risk controller:** long BUY cash equity LIMIT-only, ₹2,500 max gross exposure, ₹4,000 cash reserve, ≤₹50 modeled loss per candidate (non-guaranteed), daily ₹100/week ₹300 lock, max drawdown ₹800, explicit kill switch, clock/session, instrument, book provenance, spread, price tick and account reconciliation conditions.
- **Pure synthetic order receipt model:** acknowledgement, partial fills, cancel pending, race/duplicate/out-of-order events, halt on disconnect or mismatch and retain residual exposure. No live network, no authenticated broker orders, no durable order journal.
- Automated GitHub Actions unit tests; CI result and merge must be verified before citing PASS or claiming merged code.

## Next build order
1. Secure offline tests and merge immutable engine snapshot, independently verify CI.
2. Implement durable audit/event journal with restart/recovery and cancel/partial-fill reconciliation against **synthetic fixtures**, no broker credentials.
3. Independently verify current instrument session/tick bands, fee model, risk caps and transaction journal using allowed non-live test data.
4. Preregister frozen strategy and execute untouched multi-regime historical evaluation with licensed sources, NO_TRADE and twice-cost benchmarks. If it fails, revise research before capital exposure.
5. Obtain exchange/vendor permitted forward-data rights and gather ≥60 complete frozen-strategy monitored paper sessions; independently review incident log and after-cost results.
6. Separate broker-authorized trading app, OAuth and compliant static IP; independent legal/compliance review. An Analytics Token alone cannot be promoted to trading.
7. Human written approval to consider a **small supervised deployment** following end-to-end fault injection; never implicitly enable orders.

**No mode switch should convert this repository to order submission without separate explicit authorization and a review of evidence.**

## Official references (2026)
- Upstox Analytics Token restrictions: https://upstox.com/developer/api-documentation/analytics-token/
- Upstox retail API static IP/algo announcement (April 2026): https://upstox.com/developer/api-documentation/announcements/algo-trading-circular/
- Upstox V3 order API / current broker errors: https://upstox.com/developer/api-documentation/v3/place-order/
- NSE algo trading/Client Direct API procedures, May 2026: https://www.nseindia.com/static/trade/platform-services-non-neat-decision-support-tools-algorithm-trading
- SEBI framework transition effective from 1 April 2026: https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html
- NSE data policy: https://www.nseindia.com/static/market-data/nse-data-policy
