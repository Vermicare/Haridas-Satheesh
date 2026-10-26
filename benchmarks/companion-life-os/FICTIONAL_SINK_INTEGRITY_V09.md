# Companion — Independent Fictional Sink Integrity v0.9

**Date:** 2026-10-26. **Project:** Companion Intelligence, public fictional authorization/outbox experiment. **Stage:** Simulation / software-contract evidence only. **Review state:** [draft PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10), unmerged. No real user, account, connector, consent, employer data, or external action.

## Question and predeclared negative controls

Does the **separate fake SQLite sink** enforce its own payload schema and verify its stored acknowledgment on replay, even when called directly rather than through the outbox? The existing v0.8 outbox checks the source receipt and its own acknowledgments, but the independent fake sink accepted a payload missing an action, accepted a whitespace-only decision, and returned a corrupted persisted acknowledgment without validating it.

Three tests in `test_fictional_sink_integrity_v09.py` require fail-closed behavior for (1) missing action, (2) blank decision, and (3) a persisted acknowledgment with an incorrect digest. A fourth test is a positive control for valid first delivery and replay. The fake sink uses disposable on-disk SQLite, with zero external effects.

## Reproduced failure and correction

- **Before-fix commit:** `86503326ec3d3a08bfc92dfacaece348ac9c2c64`. [Red CI #40334808905](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40334808905): **79 tests, 3 expected failures** on Ubuntu and Windows. The failures were exactly the three new negative controls; both job logs were inspected.
- **Corrected code commit:** `450d395f08363cd7fafec8193fef817cebfc4425`. [Green CI #40334887066](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40334887066): **79/79 tests passed on Ubuntu and 79/79 on Windows**. Both job logs were inspected; fictional demo and artifact-upload steps completed successfully.
- **Source Git blob:** `fb5e3bdbace00236a562fa1af705189606f35624`; **new test Git blob:** `4a650cf622f8edbeacba230ff7f516dc1feec659`.
- **Fix:** the fake sink now accepts only `nonce`, `decision`, `action`, and `synthetic`, requires nonblank strings and `synthetic=true`, and checks the persisted replay acknowledgment's nonce, payload digest and fictional effect markers before reporting success.

## Reproduction

From `benchmarks/companion-life-os`:

```bash
python -m unittest -v test_fictional_sink_integrity_v09
python -m unittest -v test_authorization_guard_v02 test_authorization_store_v03 test_correction_ledger_v05 test_actual_receipt_integration_v06 test_fictional_outbox_v07 test_fictional_sink_integrity_v09
```

**Run conditions:** GitHub-hosted Ubuntu and Windows, `actions/setup-python@v5` with Python `3.13`; exact patch-level Python, SQLite version and runner image: **TBD**. Python standard library only. Input: author-created fictional payloads and intentionally corrupted local SQLite rows. Seed: N/A. Metrics: contract-test pass/fail and fake sink row count; no throughput, latency, user benefit or real reliability measurement.

## Decision, limits and next gate

**Decision:** retain the correction; do **not** advance maturity. This closes a bounded direct-sink validation hole in the public fake adapter. SHA-256 and local SQLite do not authenticate actors, establish trusted timestamps, resist an operator who controls both databases, or guarantee exactly-once delivery to real connectors. The intentionally non-idempotent sink still duplicates fictional effects after crash/retry in the earlier v0.7 negative control.

**Largest gap:** authenticated, identity-bound issuance and real adapter semantics remain **TBD**. Next experiment: a separate trusted sandbox issuer, tamper/expiry/replay tests, and measured reviewer correction burden under a frozen threat model; [Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11) remains the gate. Reframe as read-only advisory if safe authorization cannot be shown without disproportionate complexity.

**Four lenses:** hiring—reproducible red/green tests, not deployment; technical—inspect independent sink trust boundary and stored acknowledgment checks; innovation—reusable integrity pattern, not novelty; founder—external reliability, operating cost and consent burden unmeasured.
