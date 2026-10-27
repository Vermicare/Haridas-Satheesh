# Companion v1.1 — atomic fictional approval revocation experiment

**Date:** 2026-10-27. **Status:** synthetic contract verified in hosted cross-platform CI; no real identity or external actions. **Maturity:** unchanged, private implementation not evaluated. **No real identity, consent, account, connector or user data.**

## Decision question

The v1.0 signed test-harness approval has no revocation check: can a withdrawn approval still produce a *new fictional* receipt? Does putting the revocation check and receipt insert inside the **same SQLite `BEGIN IMMEDIATE` transaction** close this local time-of-check/time-of-use gap, including concurrent attempts and restart?

## Frozen fixture and reproducibility

- Existing `scenario.json`, v0.2 `simulate_once`, v0.3 `FictionalDurableStore` schema, v1.0 signed identity/approval validator; unchanged.
- New additive `revocable_signed_boundary_v11.py` subclasses the existing fictional store, creates an append-only-by-API `fictional_revocations` table keyed by SHA-256 of the canonical signed approval token, and reuses the v1.0 signed-boundary checks before a revocation-aware store proxy is called.
- The revocation event and receipt insert both acquire a write transaction on the **same** local SQLite database. A revocation that commits first denies a subsequent receipt; a receipt that commits first is preserved historically, but the revoked token cannot be replayed afterward. No external connector is invoked.
- Run from `benchmarks/companion-life-os`: `python -m unittest -v test_revocable_signed_boundary_v11` and `python demo_revocable_signed_boundary_v11.py`.
- Only Python standard library. Local Python **3.13.5**, SQLite **3.46.1**; local corrected 15/15 tests passed with manually mirrored upstream dependencies. **Hosted CI #40498978104** used Python **3.13.16** on Ubuntu and Windows at executable commit `b700f0d03426ab3b38e88340a4e2a39e138cb7be`; hosted SQLite version **TBD**.

## Negative control and observations

The explicit v1.0 **negative control** accepts a new fictional receipt despite a test-harness revocation row, because that earlier implementation has no revocation query. This is an expected, reproduced *sandbox contract gap*, **not** a vulnerability in a deployed agent. The v1.1 tests cover pre-use revocation, post-use revocation, replay after restart, duplicate revocation event preservation, concurrent revoke-versus-execute ordering, 12 parallel denied attempts, token-specific revocation, invalid signature, identity mismatch, scope escalation, expiry, missing revocation table, and invalid operator inputs.

**Local measured outcome:** 15/15 new tests passed; short demo created one fictional receipt, one fictional revocation, denied use after revocation and after SQLite reopen; external actions = **0**. [GitHub Actions #40498978104](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40498978104): **109/109 passed on Ubuntu and 109/109 on Windows**, both job logs inspected, v1.1 demo executed and artifacts uploaded. Human review time, power-loss behavior, actual authenticated revocation, production safety and reviewer burden: **TBD**.

## Threat model and limits

The revocation operator is a **test harness**, not an authenticated person. The issuer/verifier HMAC keys are intentionally public test values; the verifier still possesses signing material. The clock is caller-supplied. SQLite row contents can be altered by a filesystem attacker, and there is no independent trust root, signed revocation feed, monotonic trusted clock, process-kill or power-loss test, hardware-backed identity, external connector, or real user consent. A local serialized write transaction does **not** imply distributed revocation or exactly-once external effects. The internal `_execute_checked` method is **not** an authentication boundary and must not be exposed to untrusted callers.

## Advance / kill / next experiment

**No maturity advancement.** This is a fictional software contract check. Reframe as read-only advisory if an already revoked approval can create a new receipt in a correctly routed v1.1 test or if serialization fails under controlled concurrent attempts. Next: separate test IdP/verifier with externally managed test keys and a trusted-clock emulator; add process-kill and tamper tests, then independent review and actual blinded reviewer burden. Do not integrate any personal or employer accounts without separate approval.

**Primary engineering rationale:** [SQLite transaction modes](https://www.sqlite.org/lang_transaction.html) and [SQLite isolation](https://www.sqlite.org/isolation.html) document serialized writes and `BEGIN IMMEDIATE`. This is a database property, not an identity/security certification. For real authentication boundaries, see [NIST SP 800-63B-4](https://csrc.nist.gov/pubs/sp/800/63/b/4/final). No standards compliance or novelty claim.

**Four-lens review:** Hiring manager — executable negative control and cross-platform 109-test green gate; technical reviewer — local serialization is testable but signer/operator/clock remain untrusted; innovation leader — revocation adds an explicit abort path to a general authorization architecture, not demonstrated novelty; founder — no verified user benefit, customer deployment, real consent, or business performance.

## Preserved red → green CI learning

At [run #40498874654](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40498874654), Ubuntu passed but Windows failed **2 of 109** tests during temporary-directory cleanup (`WinError 32`): two test cases used a SQLite connection context manager that commits/rolls back but does **not** close the handle. Explicit `contextlib.closing` corrected the fixture without changing the revocation algorithm. At [run #40498978104](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40498978104), both operating systems passed **109/109**, and both v1.1 demo uploads succeeded. This is a reproducibility fix, not a production security finding. The verified source/test/demo Git blobs are `043ff70bf82416f2a7bb624835eb167255a3711c` / `1b408965e65e52266bb3c2f8061dde9a569efd01` / `1e67269c684669663401987805447530f6b063ca`. The original v1.0 evaluator, existing receipts and prior verified CI were not overwritten.

## Additional negative control — inherited execution API bypass

An independent follow-up found that the first v1.1 subclass still inherited the original v0.3 public `execute` method. After a test-harness revocation, calling that inherited method **created one new fictional receipt**, bypassing the new revocation-aware wrapper. This is a *real test-contract routing failure* reproduced locally, not a deployed-system vulnerability. The correction overrides `FictionalRevocableStore.execute` to fail closed and adds an adversarial regression test. Corrected local **16/16** new tests passed. Final cross-platform 110-test run: **TBD until inspected**.

**Residual boundary:** separate callers can still instantiate the older `FictionalDurableStore` directly against the same local database; the v1.1 wrapper does not enforce revocation globally across legacy adapters. A real design must retire or block legacy write paths and independently authenticate revocation operators. Do not claim production-wide revocation or tamper resistance from this candidate.
