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


## 2026 Upstox cash-intraday paper-cost stress (2026-11-12)

[upstox_intraday_cost_stress.mjs](upstox_intraday_cost_stress.mjs) contains a
new **OFFLINE ONLY** synthetic closed-trade fee and execution-adversity audit.
[Regression tests](test_upstox_intraday_cost_stress.mjs) run under the trusted
read-only Node 22 workflow. This fixes an important economic modelling mismatch:
the earlier [February 2021 pilot](../experiments/costed_intraday_pilot.mjs)
explicitly uses a **Zerodha reference** 0.03% brokerage assumption, while Upstox
currently advertises **up to 0.1% or ₹20/executed intraday order**, whichever
is lower. Historical results have *not* been retroactively recalculated or
relabeled as Upstox profit evidence.

Source: [Upstox published fees](https://upstox.com/brokerage-charges/),
consulted 12 November 2026. Paper estimates assume ₹20/order brokerage cap,
0.1%/side brokerage, NSE 0.00307% turnover fee, illustrative 0.0001% SEBI levy,
0.003% buy stamp, 0.025% sell STT, and 18% GST on selected fee components.
**Conservative choices:** round individual charge components *up* to a paise,
STT up to a whole rupee, and separately include a 0.0001% IPFT contingency
that **might double count** if included in exchange fees. Actual transaction
notes, eligibility, regulatory rounding, fill-splitting, taxes and broker plan
must determine real charges; this is not an authoritative Upstox calculator.

The strict input only accepts a single *closed, hypothetical* long transaction
within the existing ₹2,500 position cap; it never consumes broker messages.
A published gross profit can become a loss after fees and explicitly modeled
5/15/50-basis-point *additional economic adversity* on each side, with a
separate 200-basis-point tail-gap shock for simulated STOP outcomes. These
penalties are **not** predictions of literal worse-than-limit fills. No liquidity,
spread or execution availability is authenticated. `NO_TRADE = ₹0` remains
the benchmark. Every result has `canTrade:false`, `brokerReconciled:false`
and `realOrderRoutePresent:false`, even when a hypothetical outcome is
positive. This module is a cost falsification aid only; **never promote a
strategy from these reused development examples**, and obtain independent
licensed holdout and forward evidence before any real-money consideration.

To reproduce: `node --test projects/qhap-trader/live_readiness/test_*.mjs`.


## Prospective anti-selection evidence ledger (2026-11-12)

The new [prospective_evidence_ledger.mjs](prospective_evidence_ledger.mjs)
and [offline regression suite](test_prospective_evidence_ledger.mjs) enforce
a **pre-frozen** day manifest to catch missing, duplicate, out-of-order,
future/premature, or incomplete self-reported evaluation sessions. It counts
no-trade days, discloses exceptions, checks closed-trade fee arithmetic and
blocks partial P&L summaries when data are unknown. The study compares
estimated returns against `NO_TRADE = ₹0` and requires 60 complete
prospective research observations before even **external review**.
Read [the full preregistration and hard limitations](FORWARD_EVIDENCE_PROTOCOL_20261112.md).
A deterministic SHA-256 manifest digest is not a third-party timestamp or
proof of an actual exchange/market-data event; closure dates, market-data
entitlements, any actual source or broker state and a profitable net edge
all remain **unverified**. The tool never counts any independently certified
forward session and **cannot** authorize or route live orders.


## NSE 2026 public holiday overlay and unverified data rights (2026-11-12)

[market_data_calendar_preflight.mjs](market_data_calendar_preflight.mjs)
and [its offline tests](test_market_data_calendar_preflight.mjs)
strengthen the forward-protocol research boundary. The public
[NSE 2026 equity holiday table](https://www.nseindia.com/resources/exchange-communication-holidays?apiversion=v2)
lists **24 November 2026** and **25 December 2026** as closed, and the
module checks whether those dates were incorrectly included in our
frozen calendar manifest. It **does not** have a pinned 2027 market
calendar: forward plans spanning 2027 remain blocked from any claim of
independent calendar verification, regardless of correct 2026 exclusions.
Unknown special sessions, instrument halts and amendments require external
official evidence.

The redacted, strict metadata-only rights gate flags missing or denied
non-display research, **paper simulation** and local retention permission
claims, invalid effective dates, and secret/raw-data fields. A positive
metadata claim or hash still **cannot attest a license or entitle us to
ingest a feed**. The current
[NSE usage policy](https://www.nseindia.com/static/market-data/nse-data-policy)
makes specific allowed uses contractual. All outputs remain
`marketDataUseAuthorizedBySoftware:false`, `canTrade:false`, and
`realOrderRoutePresent:false`.
Read [source references, caveats and next evidence needs](MARKET_DATA_CALENDAR_PREFLIGHT_20261112.md).


## Source-metadata feed chronology (2026-11-12)

New [synthetic_feed_chronology.mjs](synthetic_feed_chronology.mjs) and
[adversarial regression suite](test_synthetic_feed_chronology.mjs)
exercise strict **mock-only** event ordering, local receive time, vendor
\`currentTs\` vs hypothetical book-event timestamps, SHA-256 chain integrity,
stale heartbeats, session rollover, outage/reconnect halts and incomplete
capture intervals. Unkeyed hashes cannot prove source identity; vendor
tick time cannot certify real exchange book freshness. The input rejects
real broker/quote data and access tokens, and the output remains
\`independentlyAuthenticatedExchangeBookUpdates:0\`,
\`canTrade:false\`, \`canMakePaperFill:false\`, and
\`realOrderRoutePresent:false\`. No real market data has been used.
See [scope and future private-adapter requirements](SYNTHETIC_FEED_CHRONOLOGY_20261112.md).


## Private evidence review & signed synthetic attestation (2026-11-12)

[The private source-evidence protocol](PRIVATE_SOURCE_EVIDENCE_REVIEW_PROTOCOL_20261112.md)
sets an independent licensing and source/time review boundary, and flags
the [NSE data usage policy §7.4](https://www.nseindia.com/static/market-data/nse-data-policy)
restriction relating to virtual trading and simulation. A read-only
vendor token cannot itself authorize feed-based paper trading.

The [signed_mock_review_attestation.mjs](signed_mock_review_attestation.mjs)
and its [offline tests](test_signed_mock_review_attestation.mjs) use
Ed25519 verification of **handcrafted mock-only metadata** to detect
untrusted keys, forged signatures, expired statements, modified frozen
manifest commitments, replay and private/raw fields. All keys used by
tests are ephemeral, generated in memory. An authentic signature against
a self-declared key is **not** an independent reviewer, permission
determination or original exchange event. Nothing in these modules
requests, reads, stores or authorizes real data, credentials or broker
orders. `canTrade:false`, `sourceOrMarketDataAuthenticated:false`
and `legalLicenseRightsVerified:false` are immutable output
boundaries. Verified independently permitted data and live order
authorization remain separate external gates.


## 2026-11-12 — actual data-source permission and financial feasibility

[DATA_SOURCE_REQUIREMENTS_AND_RIGHTS_20261112.md](DATA_SOURCE_REQUIREMENTS_AND_RIGHTS_20261112.md)
documents current primary NSE/Upstox policy, the *explicit* Upstox historical
equity backtesting technical pathway (one-minute data Jan 2022 onward),
NSE consolidated policy §7.4 restrictions on virtual trading/simulation,
March 2026 non-display agreement requirements, 1 Apr 2026 official domestic
tariffs, Upstox sandbox and actual retail-algo IP/header requirements.
It separately identifies intended uses (private historical strategy
evaluation, live-feed synthetic paper execution, eventually real orders);
none can be assumed legally equivalent. It gives exact questions for
written Upstox/NSE permission and provenance review, and explains why
an NSE direct non-display enterprise subscription is not economically
sensible for the ₹10k research capital.
**No source account/license was checked; no paid product, broker feed,
credentials, market data or real trading accessed.** Remain NO_TRADE.


## 13 November 2026 — independent cross-provider verification

[INDEPENDENT_EXTERNAL_DATA_RIGHTS_CROSSCHECK_20261113.md](INDEPENDENT_EXTERNAL_DATA_RIGHTS_CROSSCHECK_20261113.md)
separately verifies the seven questions in the Upstox inquiry using
**original NSE, SEBI, Zerodha and Dhan publications**, rather than
waiting for a broker support reply. Important update: SEBI's
**8 May 2026** price-data circular, effective **1 July 2026**, imposes
a **30-day sharing/usage lag for investor education** and a special
one-day NISM simulation-lab exception; it is **not** a general
commercial-backtest or live-feed paper-trading permission.
Other brokers publish one-minute/history APIs and retail fees, but
subscription access does not waive NSE non-display or virtual-simulation
rights. Upstox V3 explicitly uses **start-of-candle** timestamps and
documents corporate actions via a separate endpoint; automatic price
adjustments, private storage rights, and account-specific simulation
permissions remain unverified. All genuine market-data-driven QHAP
paper fills and real orders are still blocked pending applicable
legal/contract checks. Strict synthetic offline engineering can continue.


## 13 November 2026 — fixed payoff viability falsification

[precommitted_payoff_viability.mjs](precommitted_payoff_viability.mjs)
and its [offline regression tests](test_precommitted_payoff_viability.mjs)
reuse the pre-existing Upstox **indicative** fee engine without network,
licensed market data, credentials, or execution. They algebraically
calculate theoretical break-even hit-rate thresholds for an imaginary
₹2,000 BUY, 1.5% TARGET and 1% STOP, under four fixed per-side
adversity assumptions (0/5/15/50 basis points), plus hypothetical
0% or 5% of losing outcomes with additional 200-bp stop-gap penalties.
All 40 win-rate what-if cells are reported; NO_TRADE=₹0 is the reference.
A profitable *assumed* hit rate is never empirical strategy evidence,
and an unfilled stop can exceed the modeled ₹50 candidate risk budget.
See [full explanation and limitations](PAYOFF_VIABILITY_FALSIFICATION_20261113.md).
There are **zero actual research sessions, data rights, authenticated fills,
broker orders, or demonstrated trading edge** in this experiment.


## 13 November 2026 — sample-size feasibility, not edge certification

The [statistical_evidence_sample_design.mjs](statistical_evidence_sample_design.mjs)
calculates minimal **imaginary independent target-win counts** whose
two-sided 95% Wilson lower hit-rate bound would exceed the frozen,
fee-aware synthetic break-even hit-rate scenarios. Its associated
[research report](STATISTICAL_EVIDENCE_SAMPLE_DESIGN_20261113.md)
and [offline tests](test_statistical_evidence_sample_design.mjs)
explain why **60 prospective trading sessions do not imply 60 independent
closed trades, a valid confidence interval, or a positive net advantage**.
At 15 basis points of added slippage each side, 46 of 60 independent
binary target outcomes would be needed for this *hypothetical* 64%
break-even bound; at 50 basis points 60/60 would be needed. These are
precommitted mathematical sample thresholds, NOT actual trading
observations, a permission to fetch protected prices, or a live/paper
trading activation. Real-world evaluation must use permitted unseen
per-day net-rupee evidence with dependence-aware uncertainty,
independent source audit and NO_TRADE comparator.


## 13 November 2026 — verified market-data access path and NSE prospective-client exception

[MARKET_DATA_ACCESS_VIABILITY_20261113.md](MARKET_DATA_ACCESS_VIABILITY_20261113.md)
documents a **material primary-source clarification**: NSE's consolidated
policy §5.1 explicitly provides an exchange-approved, potentially free
six-month historical tick/trade **strategy testing trial** for qualifying
prospective/new Indian-market clients, with a **not-currently-trading-that-
segment declaration** in §5.2 and possible extra approval for up to
12 months. This is **not** a universal self-service entitlement, and
neither six nor twelve months alone meets QHAP's multi-year three-regime
untouched holdout. Live price-driven virtual-paper simulation remains
separately restricted by §7.4 and NSE/COMP/56426. Existing EPR academic
noncommercial research is a different route.

Verified alternative technical coverage: **Upstox V3** one-minute since
January 2022, **DhanHQ** up to 5 years at ₹499 plus GST per automatically
renewing 30-day Data API, **Zerodha Kite Charts** since 2015 with native
Streak backtesting (limited strategy fidelity), **Tick Data** leased
2012+ intraday quotes/trades, **TrueData API** default six-month window
and **Global Datafeeds API** default three-month window. Product
availability is NOT an account-specific use-rights or data-completeness
attestation. A non-sensitive DhanHQ provider-use query was sent to its
official API help on 13 Nov; existing NSE and Upstox inquiries continue.
**No market-data access, payment, account, execution or new genuine
research result. Keep NO_TRADE.**
