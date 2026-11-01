# Companion v2.1 — fictional dispatch-time expiry candidate (partial evidence)

**Date:** 2026-11-02 (Asia/Kolkata). **Stage:** Research / Simulation, unchanged. **No production security, real consent, external connector, real user or deployment.**

## Falsifiable question

The [v1.8 negative control](DISPATCH_EXPIRY_GAP_V18.md) demonstrated that the v1.4 fictional atomic outbox could stage a valid signed approval and then create a fake sink row after the hypothetical approval expiry: its `dispatch(nonce)` accepted neither an approval token nor a clock. Can a *separate candidate* reject expired fictional approvals at simulated dispatch without breaking idempotency, restart and concurrent single-row behavior?

**Candidate:** [expiry_checked_delivery_v21.py](expiry_checked_delivery_v21.py), intentionally separate from the frozen v1.4 negative control. **Tests:** [14 adversarial cases](test_expiry_checked_delivery_v21.py). **Demonstration:** `python demo_expiry_checked_delivery_v21.py` emits aggregate-only JSON in a few seconds; no real action.

## Protocol and observations

- Test harness issues two independently signed **fictional HMAC** tokens (identity and exact approval). The candidate validates signatures, subject/approval agreement, grant nonce and expiry at **every fake dispatch**, including idempotent replay.
- A single SQLite `BEGIN IMMEDIATE` transaction binds the staged approval digest to the original receipt and payload, rechecks local revocation, and inserts at most one fake sink row. It rejects mismatched/altered evidence and malformed signatures.
- Regression controls cover valid dispatch, expiry at the boundary, expired identity, not-yet-valid or malformed time, wrong identity/approval, pending/acked revocation, expired replay, restart replay, precommit rollback, concurrent dispatch, and invalid signature.
- The existing v1.8 expired-dispatch **negative control** and v2.0 **four reachable legacy fictional effect routes** are deliberately preserved; the candidate does **not** close those bypasses.
- On [GitHub Actions run #41343453670](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41343453670), **Ubuntu 24.04 and Windows 2022**, both CPython **3.13.17**, each executed **169/169 repository tests PASS**, including **14/14 new tests**. Both original job logs were independently inspected; each v2.1 JSON demonstration reported `passed=true`, `tests_run=14`, `real_external_actions=0`, `clock_trust=caller-supplied-test-only`, and `legacy_bypass_routes=remain-open`. GitHub Actions uploaded aggregate-only ZIP artifacts: Ubuntu ID `13098407514` (runner-reported SHA-256 `db15e7c341c64b9a4b1d7e3914d39707e43078fa902ba7bc7ee678f8667b68c2`) and Windows ID `13098173659` (runner-reported SHA-256 `caec6c37152855e84d2974d85fff06c6db9d74b1df18fed86767c5ff4d4a772c`). ZIP bytes were **not independently downloaded or rehashed**. Candidate source Git blob `c8807d2a1621152dac4b3bb8ebc9e563f6cea50d` and test blob `f269a397f2748f393fee7e2a3e96f449ef686c9c` matched independently generated local Git blob hashes.

Reproduce from `benchmarks/companion-life-os`:

```sh
python -m unittest -v test_expiry_checked_delivery_v21
python demo_expiry_checked_delivery_v21.py
```

No third-party Python dependencies are needed. Workflow executable commit `4d768746f4bdd05badb608f6e0e33fc459071aa4`; source/test blob hashes above. Unknown operational measurements are **TBD**.

## Threat model, unresolved failures and decision

**Largest gap:** the `now` clock is **caller-supplied** and can be backdated; public test signing keys are forgeable by design; the legacy `FictionalDurableStore.execute`, `FictionalOutbox.stage`, `FictionalOutbox.dispatch` and `FictionalIdempotentSink.apply` remain callable in public fixtures. The candidate is *not* a single enforced effect gateway, a production security control, or proof of human consent. The SQLite transaction cannot atomically cover a separate real service. No physical power-loss or external receipt tests were run.

**Next experiment:** place all four legacy fictional entry points behind an isolated, deny-by-default fake adapter with a separately trusted time source; preregister red/green tests for revoked and expired dispatch, crash/restart, concurrency and direct sink attempts. Do not connect accounts. **Kill/reframe:** if legacy writers remain reachable or trusted effect-time verification cannot be established, keep Companion read-only/advisory.

**Four-lens review:** hiring manager—preserves negative findings rather than hiding them; technical reviewer—one candidate path does not prove global reachability or trusted time; innovation leader—no novelty or patentability claim; founder—no real identity, user adoption, revenue, safety certification or production deployment.

**No maturity advancement, merge, release, external commitment or collaborator outreach.**
