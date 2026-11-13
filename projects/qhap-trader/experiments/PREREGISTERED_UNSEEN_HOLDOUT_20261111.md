# QHAP-TRADER — prospective historical holdout protocol (frozen 2026-11-11)

**Status: PROTOCOL ONLY — NO DATA ACQUIRED OR OPENED, NO TEST EXECUTED, NO RESULTS.** Issue #27. This document is a prospective decision rule, not evidence of profitability. Any subsequent edits must be separately versioned and identified as post-registration before new observations are inspected.

## Question and falsifiable null

Does the **already committed, unmodified simple baseline** outperform NO_TRADE and the already committed DTT veto after costs across previously unseen Indian cash-equity minute days? Null: there is no robust positive net advantage over NO_TRADE; DTT adds no incremental benefit. No strategy changes, threshold search, model selection, or claims of novelty are allowed using the holdout.

## Eligibility gate before a single new candle is inspected

1. Establish explicit, documented legal entitlement to use the proposed minute bars for this purpose, including historical coverage, internal calculations, retention and public *derived* summaries. Publicly viewable URLs do not establish redistribution or research rights. Do not commit raw licensed candles.
2. Identify exchange-original symbol/instrument IDs, timezone, session calendar and special-session/halts, corporate-action adjustment convention, source publication timestamps, provenance hashes, completeness, and any source revisions. If any are unverified, classify **UNVERIFIED_DATA** and stop performance testing.
3. Freeze a machine-readable manifest **before opening data**: provider, license evidence reference (non-sensitive), instruments, start/end dates, chronological train/validation/holdout boundaries, regime definitions, source file hashes when available, and strategy/fee/simulator Git commit SHA. Any holdout data seen before freeze is development data and must be excluded.
4. At least three separately identified historical market regimes spanning multiple years, and a minimum of 60 distinct *previously unseen* cash-equity session dates in the holdout, not 60 symbol-days. If licensing cannot provide this, log **INSUFFICIENT_HOLDOUT**; do not quietly shrink the threshold.

## Frozen evaluation design

- Simulated starting equity INR 10,000 **per instrument**, no pooling, long-only cash, no leverage/derivatives/orders; the deterministic risk veto dominates all research policies.
- Policies: NO_TRADE (exact INR 0 net P&L); the existing simple breakout baseline; existing DTT veto, strictly quarantined. Run each on the same eligible symbol-days, calendar and decision timestamps; report unmatched opportunities explicitly, never describe different fills as matched trades.
- Costs: use dated, primary-source Indian brokerage/exchange/STT/GST/stamp/SEBI schedules where independently verified. Present historical-date and explicitly labeled illustrative current-date fee models separately; apply 1x, 2x, 3x friction stress and adverse slippage. Unknown rate/rounding => **COST_UNVERIFIED**, no certified net P&L.
- Simulator: next-observable timestamp ordering; stale/missing quote, holiday/halts, ambiguous same-candle stop/target, adverse gaps, entry rejection, partial fills, incomplete exit, uncertain position, capital conservation or risk-lock fault => **HALT_UNKNOWN** and unknown equity, not an invented zero or favorable fill. Record both halt count and affected sessions.
- Primary endpoint: aggregate net-of-cost INR expectancy per independent day and comparison with NO_TRADE, with day-block uncertainty intervals. Secondary: max drawdown, loss tail, exposure, abstention quality, completed trades, turnover, costs, failures, and per-regime outcomes. Report all symbols/regimes, including zero-trade days and negative results.
- **Decision rule:** no positive-edge claim if any critical provenance/license/calendar/cost/fill gate is unresolved; or if day-block 95% interval for baseline-minus-NO_TRADE includes zero; or if 2x/3x friction scenarios do not remain positive; or if a regime has negative net expectancy. A passing retrospective result alone never permits live or unattended execution. DTT is not promoted unless its incremental difference versus the baseline passes the same gates on new independent data.

## Reproducibility and anti-leakage record

Before evaluation, archive immutable protocol commit, manifest hash, code SHA, parameters, calendar and cost source citations. After evaluation, publish counts of distinct days, excluded/failed days and reasons, SHA-256 of authorized input **locally only** where license restricts publication, deterministic command, Node version, output hash, exact CI run/job links, and full negative/null outcomes. A changed protocol requires a fresh untouched holdout. No API credentials, raw unlicensed data or confidential records in GitHub.

## Current known negative development evidence (NOT holdout)

The 12 already examined February 2021 dates for ACC/RELIANCE, and previously examined NIFTY samples, are ineligible. The merged 2026-11-10 historical day-block audit found RELIANCE baseline +INR 17.17 at 5 bps/side but -INR 27.29 at 15 bps/side; the 5-bps descriptive interval crosses zero and DTT was worse. This cannot establish prospective edge. The Upstox status-only HTTP 200 is not a fresh quote or data license.

**Next gate:** obtain permitted, authenticated, previously unseen historical minute data and freeze its manifest before opening observations. Until then the research result is **NO VALIDATED EDGE; PAPER ONLY**.
