# QHAP-TRADER — private source-evidence review protocol (draft, 2026-11-12)

**Scope:** Independent human audit design for a future, separately authorized, local-only NSE cash-equity observation. This document is **not** an entitlement, an exchange certification, an executed test, or a permission to run a broker-derived trading simulation. Current decision: **NO_TRADE / NO_AUTONOMOUS_FORWARD_PAPER**.

## Threat model and evidence hierarchy

A local SHA-256 chain establishes only byte continuity after collection; its creation time, origin, market-data entitlement, completeness, and book-event authenticity are **not** established by hashing. A timestamp provided by the same machine, a self-declared `sourceVerified` flag, a synthetic broker fixture, and a vendor `currentTs` field are not independent witnesses. A signed receipt is only as credible as the independently verified identity, key custody, clock and scope of its signer.

Evidence tiers (never silently promote):
1. **T0 synthetic:** handcrafted fixtures and CI tests; may validate software logic only.
2. **T1 user-local observation:** locally produced aggregate diagnostics; may establish reported transport behavior, not independent source authenticity or permitted use.
3. **T2 independently reviewed source and rights:** reviewer has independently checked vendor/exchange agreement version, account-specific intended use, and authentic source/time records *without uploading confidential material*. Still not execution-quality certification.
4. **T3 prospective audited research:** T2 plus frozen code and parameters before each unopened session, complete independently reviewed session coverage, explicit failure accounting, 60 observed sessions minimum, identical opportunities and NO_TRADE comparison, conservative net costs and uncertainty. This is still not live-trading authorization.

## Separate private/public boundaries

**Private, user's own machine or separately approved secure reviewer environment:** original signed agreement or license, account-entitlement screen, personally identifying identifiers, vendor raw frames/quotes (only if agreement permits retention), hardware monotonic clock calibration, local journal, signature private keys, and any real account records. Do not transmit any of these to GitHub, ChatGPT, CI, or third-party model providers. If retention is forbidden, do not retain raw market data; lack of reproducible permitted evidence remains an explicit blocker.

**Public research repository:** schema versions, source-document public URLs and retrieval dates, independently reviewed permission decision **without license text or account data**, blinded reviewer role and method, fixed code Git blob SHAs, sample counts, failure categories, synthetic test outcomes, aggregate non-sensitive metrics only when redistribution is explicitly permitted, and hashes only when they cannot reveal private identifiers. Never publish a raw payload hash as a substitute for rights or authenticity.

## Mandatory evidence register (one record per source and intended use)

- Source and responsible provider; official primary documentation URL, retrieval date/time and published/effective version.
- Exchange and vendor contractual chain; explicit non-display quantitative research, virtual/paper trading, retention, derived-output publication, redistribution and third-party processing rights **each independently evaluated**. Unknown, silent, ambiguous, expired, or contradictory means **DENIED_PENDING_EXTERNAL_REVIEW**.
- Named independent reviewer, review date, permitted instrument scope, source of legal interpretation, and a non-sensitive audit reference. A user's own checkbox, unsigned PDF digest or AI-generated assertion does not count.
- Exchange calendar circular and exception source for each session, including special trading/halts; distinguish published holiday schedule from actual venue/instrument open status.
- Timestamp semantics separately for (a) local monotonic receive, (b) vendor response creation, (c) last completed trade, (d) actual exchange order-book event. Do not infer (d) from (b) or (c).
- Acquisition software exact Git commit/blob, Node version, declared instrument alias (no account identifier), precommitted observation window, expected sample cadence, data gap/disconnect policy and source completeness limitations.
- Independent clock witness/calibration method and drift bound. If no trusted witness, record **CLOCK_NOT_INDEPENDENTLY_VERIFIED**.
- Durable journal integrity and recovery test; record the independent reference used to cross-check continuity. SHA-256 alone does not authenticate origin.
- Review disposition and expiry: **BLOCKED**, **REVIEW_REQUIRED**, or **PERMITTED_FOR_NARROW_RESEARCH_USE_ONLY**; never a `canTrade` flag.

## Local review procedure — no broker access from this automation

1. Before any data is accessed, obtain an independent rights determination for the exact proposed non-display/virtual-use case; do not assume Analytics Token possession grants it. Confirm any NSE/Upstox restrictions and expiry from primary terms. No paid acquisition or outreach by this automation.
2. Freeze a versioned manifest of instrument scope, strategy and cost assumptions, comparison arms including NO_TRADE, dates and exclusion rules, source code blob SHAs, calendar version, failure policy and analysis before opening any genuinely new session.
3. On a separately authorized local machine only, capture permitted source metadata and provenance with a trusted local receive clock; record disconnects, reconnects, heartbeat-only intervals, duplicates, order-book uncertainty and incomplete days. A vendor clock without an independent exchange book timestamp cannot certify execution freshness.
4. After a session, a separate reviewer checks rights, source origin, calendar, event sequence, gaps, ledger, missing reports and exit uncertainty. Any unverified or incomplete session remains in denominator as **UNKNOWN / EXCLUDED_WITH_REASON**, never as zero P&L or a successful no-trade.
5. Publish only explicitly permitted redacted aggregate evidence. Independently compare against the frozen NO_TRADE arm, all fixed comparator arms and conservative broker-specific charges; report null/negative results, uncertainty and all independent days.
6. Human release review is a separate future decision. Passing this protocol cannot activate a trading route. A deterministic risk veto, broker approvals, separate explicit authorization and verified prospective net advantage remain necessary.

## Falsifiable acceptance and negative tests for a future implementation

**Pass for a *protocol review only*** requires an external reviewer to produce a dated rights determination for every distinct use, verify original source and independent clock evidence locally, check complete planned-session coverage, and attest that no restricted material crossed the public boundary. No software-only fixture can satisfy these conditions.

**Mandatory fail-closed cases:** self-signed receipt without trusted identity; unverifiable key rotation or clock; rights covering display but not non-display research; virtual-trading restriction; no retention entitlement; source terms changed mid-study; 2027 calendar unpinned; vendor `currentTs` substituted for exchange book time; truncated feed; stale/duplicate/reordered event; reconnect gap; omitted losing session; missing terminal position; ambiguous fill; charge schedule not effective for studied period; hashes or aggregate outputs that violate data terms.

## Current disposition (2026-11-12)

- Public software: PR #58 / main synthetic chronology tests (334/334 in reported trusted CI) do **not** authenticate any real market book event.
- No independently approved market-data non-display/virtual-trading rights or licensed historical holdout has been supplied.
- No independently verified prospective sessions, proven positive net-of-cost edge, authenticated broker reconciliation or live order permission.
- **Next gate:** independent documented NSE/provider permission for the *specific* proposed research use, plus a separately witnessed local-only provenance method. Continue strictly offline engineering while blocked.

Primary reference starting points (review current effective documents, not merely links):
- https://www.nseindia.com/static/market-data/nse-data-policy
- https://upstox.com/developer/api-documentation/v3/get-market-data-feed/
- https://www.nseindia.com/resources/exchange-communication-holidays?apiversion=v2
- https://github.com/Vermicare/Haridas-Satheesh/issues/27


## 12 November 2026 — independently reviewed compliance caveat

Read the consolidated [NSE Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy),
whose linked [official PDF §7.4](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf)
explicitly addresses data provision to entities, apps and websites engaging
in virtual trading or simulation. **Our current Upstox feed possession, a
read-only analytics token, or a standard market-data agreement must never
be interpreted as consent to use NSE data in a simulated-trading product.**
This is a potentially disqualifying restriction. Only a documented,
current determination from the data provider and suitably qualified
compliance reviewer could establish whether a *particular* proposed
research/backtest activity and data product are permitted. No market-data
ingestion or market-data-driven paper execution is authorized here.

## Offline signed mock review checks, not trust certification

[signed_mock_review_attestation.mjs](signed_mock_review_attestation.mjs)
uses Node.js native Ed25519 verification over a domain-separated, canonical
**handcrafted mock-only statement**. The signer key is **not embedded in
the statement**. The verifier takes a separately supplied public key and
SHA-256 SPKI fingerprint; the simulated statement must match the expected
frozen plan and observation alias, timestamp window and narrow mock
scope. Tests generate throwaway key pairs in memory: no private key is
stored in the source tree, GitHub secrets, files or CI output.

This catches some classes of accidental or malicious evidence modification:
wrong key or key fingerprint, invalid signature, changed mock observation
or frozen plan, expired or future review time, evidence replay, key type
substitution, duplicated mock source digest, unexpected raw quote fields
and embedded access tokens. A valid result is explicitly
\`MOCK_SIGNATURE_MATHEMATICALLY_VALID_ONLY\`. A self-generated public/private
key pair can pass mathematical verification; **it does not establish an
independently vetted identity, trustworthy key custody, certified clock,
real market data, contract rights, or authorization to simulate or trade**.
No real reviewer trust root has been pinned. Even two valid synthetic
signatures yield **zero authenticated source sessions** and
\`canTrade:false\`.

This code is a preparation/checklist for a later *private* review, not a
mechanism to fabricate permission. No actual key, licensed agreement text,
broker account identifier, source price, order or API credential belongs
in this repository or in ChatGPT. A signed mock statement never upgrades
source evidence to T2 or T3.

Run in the existing read-only workflow:

    node --test projects/qhap-trader/live_readiness/test_*.mjs
