# QHAP-TRADER — Live-Readiness Engineering Firewall (2026-11-12)

**State: INCOMPLETE / LIVE ORDER ROUTING DISABLED.** This folder prepares the independent risk-control and deployment-gate architecture. It does **not** activate live orders, prove a strategy's profitability, authorize any account operation, or confer regulatory / market-data use rights.

## Why this is needed

The existing user-local read-only Upstox pipeline successfully opened a V3 WebSocket, decoded messages, and completed a 15-minute indicative shadow-paper experiment (₹10,000 simulated initial capital; approximate −₹24.96 indicative P&L on first 15-minute window). The standalone Analytics Token is deliberately **read-only** and cannot place, modify, or cancel orders. A live-ready system must be a completely separate engineering/release milestone, not simply switching an environment variable.

2026 references: Upstox [Analytics Token](https://upstox.com/developer/api-documentation/analytics-token/), [Static IP / Algo circular](https://upstox.com/developer/api-documentation/announcements/algo-trading-circular/), [Order V3 API, including 2026 error semantics](https://upstox.com/developer/api-documentation/v3/place-order/); NSE [retail client direct API algorithmic trading procedures](https://www.nseindia.com/static/trade/platform-services-non-neat-decision-support-tools-algorithm-trading), and [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy). The 2026 framework requires applicable broker/app/static IP registration and algo order tagging. Do not infer all obligations from a single example; verify the precise instrument, execution model, rate, and account with Upstox and an appropriately qualified reviewer.

## What the code actually does

- [readiness_gate.mjs](readiness_gate.mjs): read-only **inventory** of 20 prerequisite items. Missing requirements block; *even if all 20 are self-claimed satisfied*, outcome is **EXTERNAL_REVIEW_REQUIRED**, never `READY`. JSON, environment values, user-asserted receipts and synthetic tests do not self-certify live approval.
- `assessPaperEntry()`: pure deterministic paper-intent pre-trade firewall with cash equity, long BUY, LIMIT-only, tick-size, available cash, one-position, maximum ₹2,500 exposure, ₹4,000 reserve, budgeted ₹50 candidate risk with gap/friction buffer, daily ₹100 and weekly ₹300 loss locks, ₹800 peak drawdown, at most two virtual entries, mandatory kill switch, clock, and book provenance prerequisites.
- Time gate is research-conservative **09:30–14:30 IST for new paper entries** (not exchange-wide opening/closing hours). Only current / actually confirmed official session calendars and instrument eligibility can prove a session. Upstox vendor timestamp `currentTs` is **not** independently certified exchange book event time.
- All outputs are sanitized aggregate statuses, never live orders, network calls, source quotes, keys or authenticated requests. Passing the synthetic paper firewall cannot authorize a real trade or certify a quote.

This is **not a production risk-management system**. No broker account/positions/fills reconcile to it yet, the daily risk limits are modeling choices rather than guarantees, a limit order could fill partially, stop orders can fail, and a kill switch cannot guarantee immediate exit. Production requires an independent, persistent, fully tested order-state and reconciliation system, incident monitoring, human-supervised rollback, eligibility/compliance approval, and substantial evidence on net strategy expectancy.

## How to test (Node.js 22+, offline)

```bash
node --test projects/qhap-trader/live_readiness/test_readiness_gate.mjs
node projects/qhap-trader/live_readiness/readiness_gate.mjs
```

The second command should show `BLOCKED_REQUIREMENTS_INCOMPLETE` and `realOrderSubmissionPossible: false`.

**There is intentionally no `--live`, `--enable-orders`, broker URL, OAuth flow, API trading scope, trade mode, or bypass switch in this implementation.** Never add one just because a report says green.

## Evidence-based path to real readiness

1. **G1 — Engineering correctness:** deterministic order intent, time, venue/instrument, account state and risk checks; complete cancellation/modify/fill/partial-fill/rejection retry modeling; idempotent durable journal, independent risk kill switch, alerts, fail-closed reboot.
2. **G2 — Financial evidence:** licensed and exchange-verified market data, untouched historical holdout, realistic brokerage/STT/GST/spread/slippage/market impact and multiple regimes. No-trade and simpler strategies must be explicit benchmarks; synthetic and already-inspected results cannot prove edge.
3. **G3 — Forward validation:** at least **60 complete** authorized paper sessions with frozen strategy versions, independent reconciled journals, all missed signals, full incident evidence, final flat position and sufficient trades to assess uncertainty. Even 60 sessions alone is not profitability proof.
4. **G4 — Broker/compliance:** eligible trading account, broker-approved algo application, *separate* trading OAuth, registered static IP and any applicable algo-name and tags, data-use/virtual-trading rights, applicable SEBI/NSE rules, accurate instrument/lot/tick/bands, broker's official order-reconciliation and trade limits. The current read-only Analytics Token cannot qualify as trading authorization.
5. **G5 — Human sign-off, monitored deployment:** independent security/operations review, a tiny initially approved exposure cap, supervised operations, independent emergency cancellation/exit, and written go/no-go authorization. No automatic promotion in this repository.

Any failed gate -> **NO TRADE**. Until all gates pass after independent review, stay read-only/research.

## Deterministic synthetic order lifecycle audit

The pure offline [`mock_order_lifecycle.mjs`](mock_order_lifecycle.mjs) records fake acknowledgement, partial/final fills, cancellation races, rejection, duplicated event IDs and sequence gaps. It **retains partial exposure** on cancellation/rejection, demands reconciliation after disconnect or impossible events, and never unlocks risk or emits a broker request. It is a test harness for future durable broker-order reconciliation, not a connector; it currently stores no durable order journal and proves no account-side trading capability. Test with `node --test projects/qhap-trader/live_readiness/test_mock_order_lifecycle.mjs`.


## Offline hypothetical order-state lifecycle

The separate [paper_order_lifecycle.mjs](paper_order_lifecycle.mjs) now models CREATE → ACK → partial or full cumulative FILL → CANCEL_REQUEST/CANCEL_ACK, rejection, and disconnection using *pure offline fixtures*. It tracks confirmed simulated long holdings; a SELL intent can never exceed holdings after accounting for outstanding simulated sell reservations. Duplicate identical events are idempotent, but conflicting replays, sequence gaps, impossible fills, late cancellation acknowledgments, and disconnections **latch a hard halt**. No automatic halt reset, no inferred broker cancel or flat position, and no actual order transport exists. For an irreconcilable order state, manual externally verified reconciliation remains required.

Offline tests:

```bash
node --test projects/qhap-trader/live_readiness/test_readiness_gate.mjs projects/qhap-trader/live_readiness/test_paper_order_lifecycle.mjs
```

The new lifecycle reducer's **20 regression tests passed locally**, but this does not verify the broker's actual message ordering or reconnect behavior. Local journal state is **not durable after process restart**; persistent idempotent event storage, integration with independently validated real broker positions, and external deployment approval are still separate milestones. The test-only event reducer does not turn QHAP-TRADER live-ready.

Official Upstox April 2026 static-IP / algo guidance: https://upstox.com/developer/api-documentation/announcements/algo-trading-circular/. The announcement says certain high-frequency algorithms (over 10 orders/second) must undergo exchange registration and the configured `X-Algo-Name` is used when applicable. Under-10 orders/second is not a blanket exemption from registered IP, risk rules, app approval, data entitlements, or any other relevant regulatory obligations. Confirm exact applicability with Upstox before real API development.


## Durable restart audit (2026-11-12)

[durable_paper_journal.mjs](durable_paper_journal.mjs) adds a strictly offline, append-only JSON Lines simulated event journal and [20 tests](test_durable_paper_journal.mjs). It is NOT production broker order management.

- New journals are created exclusively with `wx`; existing files cannot be reopened automatically for appends, or silently overwritten.
- Strict event allowlist; SHA-256 chained record digests and sequential numbers; each write requests `fsync`. Corrupted/missing/reordered/truncated records block recovery.
- On restart, even a valid journal returns `RECOVERED_RECONCILIATION_REQUIRED` with `canAppend=false`. Confirmed hypothetical holdings are never presumed flat.
- Duplicate identical events are idempotent; conflicting event IDs or disconnects persist a hard halt. No assumed fills, cancels or automatic recovery.
- A supplied matching synthetic reference returns `canTrade=false` and `brokerReconciled=false`: software does not authenticate the broker's external positions.
- The unkeyed hash chain detects accidental modification, not malicious tampering. Process distribution, cross-platform crash atomicity, protected backups, real broker reconciliation and incident response are separate engineering gates.

Run all standalone offline tests on Node 22:

```bash
node --test projects/qhap-trader/live_readiness/test_*.mjs
```

The new journal's 20 tests passed in a local runtime. The GitHub Actions PR #51 workflow lookup is still returning zero runs and therefore CI PASS is NOT verified. This component cannot authorize real orders.


**Trusted CI validation note (2026-11-12):** The main branch now carries a separate [read-only safety CI workflow](../../../.github/workflows/qhap-trader-trusted-offline-safety-ci.yml) that checks all three suites (risk, mock lifecycle, durable recovery). The workflow has no trading tokens or order permissions. PR checks must show an actual completed successful job before this change is considered CI validated; creation of a YAML file alone is not proof.


## Paper capital-conservation hardening (2026-11-12)

The previously merged low-level `paper_order_lifecycle.mjs` reducer tracked confirmed *units* but did NOT verify starting cash or gross buying notional. This defect was identified by the existing hourly research task. It could accept an impossible ₹10,00,000 hypothetical BUY. This fix enforces the constraints **inside** the event reducer rather than relying only on the separate pretrade firewall.

- Starting paper cash: ₹10,000, allocated in integer paise. Maximum capital committed across all pending buys and filled positions: ₹2,500; minimum unreserved cash: ₹4,000; at most two hypothetical BUY intents per session.
- A BUY `CREATE` immediately reserves the full limit-price notional plus a conservative 1% paper cost buffer, rounded **per share** so partial fill ordering cannot consume more than allocated. Confirmation alone spends no money.
- Cumulative BUY fills are never allowed above the stated limit. Each accepted delta debits its actual hypothetical fill price plus an illustrative 0.30% per-side friction reserve. Duplicate confirmation IDs cannot double spend.
- Cancel acknowledgment or valid full rejection releases only the unfilled pending reservation. A cancel *request* does not release cash; a fill racing cancellation remains accounted for.
- SELL fills require pre-existing confirmed unreserved units and cannot execute below their hypothetical limit. Sale proceeds are placed into a **non-reusable unsettled** bucket, never automatically available for more purchases.
- Every reducer transition verifies the conservation identity `available + reserved + spent = ₹10,000`, positive positions, pending notional constraints and nonnegative balances. Invalid state or impossible fills trigger a persistent halt.
- The durable journal now retains and replays available, reserved, spent, unsettled and position-cost aggregates. Its new **synthetic capital-snapshot** comparison can detect balance mismatches but can NEVER certify broker reconciliation or permit trading.

Fees, market impact, settlement semantics, actual Upstox margins, exchange instrument tick schedules, broker client account reconciliation, multi-instrument inventory, cash from real settled sales and distributed transaction atomicity remain **outside this mock engine**. The numeric risk values are provisional research limits, not a guarantee of loss containment.

Tests from repository root on Node.js 22:

```bash
node --test projects/qhap-trader/live_readiness/test_*.mjs
```

Do not merge until automated CI passes; there is still no real-order route or trading authorization.


## Broker-shaped snapshot reconciliation (offline contract, 2026-11-12)

Added [broker_snapshot_contract.mjs](broker_snapshot_contract.mjs) and [30 offline tests](test_broker_snapshot_contract.mjs). This is a **strict, untrusted SYNTHETIC_FIXTURE-only interface** for future broker reconciliation adapter development. It does not make authenticated broker API requests, submit orders, parse raw vendor payloads, or attest to any actual account's balances.

Each mock snapshot must include an explicit observation time, `ALL_ORDERS_AND_POSITIONS` coverage, unique order IDs, full status/cumulative-fill quantities, positions and all six mock capital fields. Missing or extra top-level fields, non-synthetic claims, stale/future snapshots, incomplete pagination, mismatched cash/units/orders, unexpected broker-like orders, an unknown fill, any pending/open order or a halted journal must fail closed. A matching snapshot returns only `SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED`; **canTrade=false** and **brokerReconciled=false** always.

Paired mock snapshots are also tested for distinct capture IDs, chronological order and a mismatch in either capture. Even if both match, the result remains `PAIRED_SYNTHETIC_MATCH_EXTERNAL_AUTHENTICATION_REQUIRED`. A future production broker adapter would need independent account identity, appropriately secured OAuth scopes, complete broker API position/order/fund responses with verified timestamps, trade confirmations, corporate actions and settlement semantics, audit logging, and a human operational signoff before real-money use.

Run all offline tests with Node.js 22:

```bash
node --test projects/qhap-trader/live_readiness/test_*.mjs
```

**No real-order capability exists.** The synthetic mock snapshot schema is not an official Upstox schema and its matched statuses are not evidence of current broker connectivity. This contract does not solve the unresolved market-data license, strategy profitability, or regulatory gates.


## Upstox documentation-shaped synthetic fixture adapter (2026-11-12)

[upstox_doc_shaped_fixture.mjs](upstox_doc_shaped_fixture.mjs) and
[test_upstox_doc_shaped_fixture.mjs](test_upstox_doc_shaped_fixture.mjs)
add a pure offline, **redacted/mock-only** parser inspired by Upstox's published
[v2 order book](https://upstox.com/developer/api-documentation/get-order-book/),
[v2 positions](https://upstox.com/developer/api-documentation/get-positions/),
[v2 holdings](https://upstox.com/developer/api-documentation/get-holdings/),
[v3 funds](https://upstox.com/developer/api-documentation/get-funds-and-margin-v3/),
and [order statuses](https://upstox.com/developer/api-documentation/appendix/order-status/).
It intentionally accepts only an explicit `SYNTHETIC_UPSTOX_DOC_SHAPE`
fixture with a small *pre-sanitized* field subset; never supply raw vendor
responses, credentials, an actual client identifier or access token.

Tests exercise incomplete coverage, stale/future clocks, pending and unknown
orders, impossible quantities, duplicate identities, cross-session snapshots,
regressed cumulative fills, disappearing orders, pledged holdings/funds, and
unsupported instruments. Only NSE delivery-equity, LIMIT and single-instrument
mock cases are in scope. All results carry `canTrade:false`,
`brokerReconciled:false`, and `realOrderRoutePresent:false`. A matching shape
is emphatically **not** an authenticated broker snapshot, independent account
reconciliation, correct fees/settlement, or evidence of an executable strategy.
The order book is day-scoped; overnight positions can move into holdings,
so calendar rollover explicitly requires re-baselining rather than an inferred
zero position. Run the existing offline test glob to include this suite.
