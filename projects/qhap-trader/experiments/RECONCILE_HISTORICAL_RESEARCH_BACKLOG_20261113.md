# QHAP-TRADER — historical research backlog reconciled (13 November 2026)

**State: RESEARCH-ONLY, NO_TRADE.** No strategy performance data, broker orders, trading API credentials or exchange candles were acquired or emitted.

## Scope of older PR #47 — historical untouched holdout

[PREREGISTERED_UNSEEN_HOLDOUT_20261111.md](PREREGISTERED_UNSEEN_HOLDOUT_20261111.md) is a byte-for-byte port of the original 11 Nov protocol (source Git blob c2c83a236c584a9f1095936965af77b2863a8b6a), kept distinct from the 12 Nov prospective forward-session protocol in [FORWARD_EVIDENCE_PROTOCOL_20261112.md](../live_readiness/FORWARD_EVIDENCE_PROTOCOL_20261112.md).

These are **different studies**, never interchangeable:
- Historical validation: independently permitted, untouched minute data across at least three separate historical market regimes and at least **60 distinct genuinely uninspected NSE trading dates** in a predeclared holdout (not 60 symbol-days), with multi-year coverage, valid instrument survivorship, 1x/2x/3x stress and day-block net-of-cost uncertainty. Preset NO_TRADE and simpler-baseline comparison, full negative per-regime disclosure.
- Prospective forward audit: at least 60 complete future session records under authorized data-use terms, covering outage/no-trade days, source chronology and independent witnesses; even 60 genuine sessions do not equal 60 independent trades or demonstrate an edge.

**Neither milestone has occurred.** The prior ACC/RELIANCE February 2021 examples are inspected development data, not a pristine holdout. The archived source SHA establishes the historic research document's provenance, *not* an agreement that all current simulator code is frozen after PRs #65 and #66. On independent source entitlement and **before** accessing a true new holdout, pin the actual source/code/fee/calendar SHA, intended sample boundaries, provider and use rights.

## Scope of older PR #41 — 2026 illustrative Zerodha reference fee audit

[COST_FEE_DESK_AUDIT_20261105.md](COST_FEE_DESK_AUDIT_20261105.md) preserves the bounded original desk audit (source blob a58445e99a6eec171f3e8b7c35c9758b9f0e1ea3). It compares the historical development pilot's six item fee expressions to published **2026 reference** Zerodha brokerage, STT, exchange, SEBI levy, GST and stamp duty—**not** actual 2021 historical exchange charges, execution-level fees, or an actual contract note. The pilot's historical rate assumptions cannot certify 2021 after-cost performance.

The preserved [test_fee_formula_audit.mjs](test_fee_formula_audit.mjs) reads and extracts the fee closure from the **current** source file [costed_intraday_pilot.mjs](costed_intraday_pilot.mjs), independently checks six fixed arithmetic/rounding invariants, and must pass in the existing read-only Node22 offline test workflow. A representative ₹100,000/₹101,000 turnover test is **outside** the hypothetical ₹10,000 research capital and is purely a mathematical vector. A zero-quantity helper test likewise is not an executable trade. The separate conservative current **Upstox** indicative fee engine is in [../live_readiness/upstox_intraday_cost_stress.mjs](../live_readiness/upstox_intraday_cost_stress.mjs); do not quietly substitute one broker's rate for another's, or add IPFT twice.

## External hard stops still not resolved

| Gate | Needed independent evidence | Currently authorized? |
|---|---|---|
| G2 market data | Upstream exchange and broker-specific rights for the exact proposed research, retention, derived analytics and untouched multiyear history | NO |
| G2 positive edge | Pre-frozen actual holdout, credible authentic source, after-cost rupee P&L and dependence-aware day uncertainty versus NO_TRADE, across stressed costs and regimes | NO |
| G3 forward | Live feed-driven virtual research explicitly permitted, 60+ genuinely observed full forward sessions and verified source event freshness | NO |
| G4 real broker | Approved account/app, IP/algo order tags, broker-authoritative positions/fees and applicable SEBI/NSE compliance | NO |
| G5 release | Independent risk/security/operational validation, failover and supervised authorization before any real order route | NO |

A documentation or CI pass does **not** establish these rights or performance outcomes. Keep issue #27 open and maintain the existing QHAP-TRADER hourly automation, without duplicate runs, payments, live orders or new protected-data collection.
