# Companion v1.1 — atomic fictional approval revocation experiment

**Date:** 2026-10-27. **Status:** local synthetic execution; hosted cross-platform verification **TBD** until GitHub Actions is inspected. **Maturity:** unchanged, private implementation not evaluated. **No real identity, consent, account, connector or user data.**

## Decision question

The v1.0 signed test-harness approval has no revocation check: can a withdrawn approval still produce a *new fictional* receipt? Does putting the revocation check and receipt insert inside the **same SQLite `BEGIN IMMEDIATE` transaction** close this local time-of-check/time-of-use gap, including concurrent attempts and restart?

## Frozen fixture and reproducibility

- Existing `scenario.json`, v0.2 `simulate_once`, v0.3 `FictionalDurableStore` schema, v1.0 signed identity/approval validator; unchanged.
- New additive `revocable_signed_boundary_v11.py` subclasses the existing fictional store, creates an append-only-by-API `fictional_revocations` table keyed by SHA-256 of the canonical signed approval token, and reuses the v1.0 signed-boundary checks before a revocation-aware store proxy is called.
- The revocation event and receipt insert both acquire a write transaction on the **same** local SQLite database. A revocation that commits first denies a subsequent receipt; a receipt that commits first is preserved historically, but the revoked token cannot be replayed afterward. No external connector is invoked.
- Run from `benchmarks/companion-life-os`: `python -m unittest -v test_revocable_signed_boundary_v11` and `python demo_revocable_signed_boundary_v11.py`.
- Only Python standard library; exact CI Python/SQLite versions and hosted commit **TBD**. Local Python **3.13.5**, SQLite **3.46.1**; local 15/15 tests passed, with manually mirrored upstream dependencies, so exact upstream integration remains **TBD** pending hosted CI.

## Negative control and observations

The explicit v1.0 **negative control** accepts a new fictional receipt despite a test-harness revocation row, because that earlier implementation has no revocation query. This is an expected, reproduced *sandbox contract gap*, **not** a vulnerability in a deployed agent. The v1.1 tests cover pre-use revocation, post-use revocation, replay after restart, duplicate revocation event preservation, concurrent revoke-versus-execute ordering, 12 parallel denied attempts, token-specific revocation, invalid signature, identity mismatch, scope escalation, expiry, missing revocation table, and invalid operator inputs.

**Local measured outcome:** 15/15 new tests passed; short demo created one fictional receipt, one fictional revocation, denied use after revocation and after SQLite reopen; external actions = **0**. Cross-platform GitHub Actions results: **TBD** until inspected. Human review time, power-loss behavior, actual authenticated revocation, production safety and reviewer burden: **TBD**.

## Threat model and limits

The revocation operator is a **test harness**, not an authenticated person. The issuer/verifier HMAC keys are intentionally public test values; the verifier still possesses signing material. The clock is caller-supplied. SQLite row contents can be altered by a filesystem attacker, and there is no independent trust root, signed revocation feed, monotonic trusted clock, process-kill or power-loss test, hardware-backed identity, external connector, or real user consent. A local serialized write transaction does **not** imply distributed revocation or exactly-once external effects. The internal `_execute_checked` method is **not** an authentication boundary and must not be exposed to untrusted callers.

## Advance / kill / next experiment

**No maturity advancement.** This is a fictional software contract check. Reframe as read-only advisory if an already revoked approval can create a new receipt in a correctly routed v1.1 test or if serialization fails under controlled concurrent attempts. Next: separate test IdP/verifier with externally managed test keys and a trusted-clock emulator; add process-kill and tamper tests, then independent review and actual blinded reviewer burden. Do not integrate any personal or employer accounts without separate approval.

**Primary engineering rationale:** [SQLite transaction modes](https://www.sqlite.org/lang_transaction.html) and [SQLite isolation](https://www.sqlite.org/isolation.html) document serialized writes and `BEGIN IMMEDIATE`. This is a database property, not an identity/security certification. For real authentication boundaries, see [NIST SP 800-63B-4](https://csrc.nist.gov/pubs/sp/800/63/b/4/final). No standards compliance or novelty claim.

**Four-lens review:** Hiring manager — executable negative control and cross-platform gate, pending hosted CI; technical reviewer — local serialization is testable but signer/operator/clock remain untrusted; innovation leader — revocation adds an explicit abort path to a general authorization architecture, not demonstrated novelty; founder — no verified user benefit, customer deployment, real consent, or business performance.
