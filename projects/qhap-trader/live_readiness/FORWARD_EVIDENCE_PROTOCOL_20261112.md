# QHAP-TRADER — frozen forward-evidence protocol, research only (2026-11-12)

**Decision:** remain NO_TRADE / zero real order capability. This document
pre-registers the next methodology; it does **not** assert possession of an
authorized feed, a future published exchange calendar, a complete strategy,
genuinely unseen stock data, or a verified profitable edge.

## Locked research hypothesis

- **Market / model:** NSE cash-equity, unleveraged long-only,
  ₹10,000 simulated capital; max ₹2,500 gross paper exposure under current
  [readiness risk firewall](readiness_gate.mjs). No overnight-position
  assumptions, independent exchange opening/closing and corporate actions.
- **Rule-only comparator:** development baseline
  `ORB_10MIN_NEXT_BAR_V1`, using 09:30–09:39 opening 10-minute proxy range,
  bar-close breakout confirmed before *next* bar entry, 1% modeled stop,
  1.5% modeled target, conservative same-minute stop precedence, and by-14:55
  model exit, as currently described in
  [costed_intraday_pilot.mjs](../experiments/costed_intraday_pilot.mjs).
  Reference source Git blob SHA:
  `13c3e9d8857f22610435e9c9b1f2d4ee03888d0f`.
  The 2021 development replay uses a different broker's cost reference and
  must **not** be reused as a pristine holdout.
- **Economics:** conservative mock Upstox 2026 estimate in
  [upstox_intraday_cost_stress.mjs](upstox_intraday_cost_stress.mjs),
  Git blob SHA `80f20e3df0d043da2a116370781dbf68e46a8684`,
  with 5/15/50 basis-point per-side extra execution adversity and adverse
  STOP-gap stress. This tool is a falsification test, **not** an independently
  reconciled contract note or full historical reprice.
- **Never tune to the evaluation period.** Previously observed February 2021
  ACC/RELIANCE and all historical diagnostics, as well as the first
  approximately −₹24.96 paper shadow window, are *development evidence only*.
  DTT veto is quarantined after weaker old results. There is no
  forecast of daily return, no optimization search, no adaptive threshold
  changes after seeing future evaluation days.
- **Mandatory comparison:** NO_TRADE = ₹0 net against the same declared
  observation dates. A model with positive historical net performance but
  incomplete authorization or unbounded uncertainty is still NO_TRADE.
- **Earliest tentative forward evaluation day:** 2026-11-16, *only if*
  independently established exchange calendar and instrument eligibility,
  user-specific authorized research rights, and local safety/data integrity
  are all verified first. This date is a research-planning marker, not a
  statement of actual market hours or broker readiness.

## Protocol freeze and reproducibility

The new pure offline
[prospective_evidence_ledger.mjs](prospective_evidence_ledger.mjs) provides
`freezeProspectiveResearchPlan()` and
`auditProspectiveResearchLedger()`. A plan records the identified source
code blobs, cost policy, freeze time, predeclared date range, declared closures,
and exact decision-comparator IDs. It seals the canonical manifest with an
unkeyed SHA-256 digest, which detects **local accidental mutation**, but is
**not** a certified timestamp, independent licensing check or tamper-proof
attestation. The actual public GitHub revision/commit and independent human
review must be recorded separately *before reading eligible evaluation data*.

To discourage day selection, the plan deterministically expands **all
weekdays** in the frozen range, excluding only weekday closures declared
**before** outcomes are observed. The expansion is intentionally **not** an
authenticated NSE calendar; actual holiday, halt, session/auction membership,
or an unforeseen closure requires an externally reviewed pre-registered
amendment. A new plan version cannot erase a bad day from the old evidence.
Require at least 60 scheduled weekdays to create a research manifest, then
at least 60 complete declared observations to reach a provisional
**external independent review** status.

## Daily evidence contract — no raw market data committed

One report per elapsed declared weekday, **including no-trade days**. Each
report has a session date, local record timestamp (not before 16:00 IST),
SHA-256 digest of permitted local source bytes (not the bytes), source
completeness flag, classification, counts of observed and rejected decisions,
number of **closed** mock trades, and gross/charges/net in rupees.
Accepted *self-declared* classifications:

- `NO_TRADE`: zero trade and zero profit/cost, all observed candidate
  decisions accounted for as rejected/abstained.
- `CLOSED_PAPER_TRADES`: 1–2 closed paper trades and positive modeled
  charges, full arithmetic consistency, with rejected decisions tracked.
- `DATA_GAP`, `FEED_OUTAGE`, `UNRESOLVED_POSITION`: **explicit
  incomplete** evidence. Never manufacture an exit price, claim flat holdings
  or treat unknown profit/loss as zero.

Incomplete/missing/duplicate/out-of-order/unscheduled reports, non-paisa P&L,
negative or missing fees, impossible counts, unknown sources, premature or
future report timestamps, and tampered manifests fail closed. When any such
issue exists, aggregate P&L is **withheld** to prevent partial performance
claims. A clean, all-NO_TRADE 60-session *synthetic* ledger can reach
`DECLARED_60_SESSIONS_NEEDS_INDEPENDENT_AUDIT` but still shows exactly
**0 independently verified forward sessions** and cannot authorize orders.

This contract accepts **redacted handcrafted research reports only**.
Do not supply personal identifiers, raw Upstox payloads, tokens, exchange-
licensed prices, user holdings, or private contract documents to GitHub.
Use only sources that actually permit intended local research/retention.
Data ownership, market provenance, genuine timestamp publication,
exchange calendar accuracy, broker invoice correctness, and position
reconciliation remain separate externally verified gates.

## Promotion rule

A hypothetical 60 complete *declared* observations do **not** imply enough
trades, statistical confidence, or net positive expectancy. Before any further
readiness claim, require independent lawful source/use verification,
prospectively frozen holdout, confidence/uncertainty treatment across dates,
adverse fee/slippage stress, comparisons to baseline and NO_TRADE, outage
statistics, and human risk/compliance signoff. Actual real-money trading
requires separate explicit user authorization. The new code exports **no
broker order function**, cannot authenticate market evidence and always returns
`canTrade:false`, `realOrdersSent:0`, and `brokerReconciled:false`.

## Offline validation

```bash
node --test projects/qhap-trader/live_readiness/test_*.mjs
```

CI runs in the existing trusted no-credentials workflow on pull requests.
No new data subscription, network fetch, paid API call, or live order is
requested or implied.
