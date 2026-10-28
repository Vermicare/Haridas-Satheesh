# Companion v1.3 — revocation-to-outbox boundary (fictional negative control)

**Date:** 2026-10-28. **Branch:** draft PR #10 only. **Stage:** public fictional Simulation / software-contract evidence; private implementation unassessed. **Status:** source and regression test committed; hosted cross-platform execution **TBD** until logs are independently inspected.

## Decision question

Can a previously created fictional receipt be delivered through the legacy v0.7 outbox *after* its signed approval is revoked by the v1.1 boundary?

**Source-level observation:** `FictionalRevocableBoundary.execute` checks the revocation table, but `FictionalOutbox.stage` and `FictionalOutbox.dispatch` do not. The latter reads an existing receipt and calls a separate fake SQLite sink. Therefore, revoking the approval is not presently a global stop signal for pending delivery.

## Reproduction

From `benchmarks/companion-life-os`, using Python 3.13 and standard-library-only dependencies:

```sh
python -m unittest -v test_revocation_outbox_gap_v13
python demo_revocation_outbox_gap_v13.py
```

The tests cover two orders: (1) receipt → stage → revoke → legacy dispatch; (2) receipt → revoke → stage → legacy dispatch. They deliberately assert that the **legacy** path can still create one *fictional* sink row. The demo prints JSON containing signed-path denial, legacy simulated delivery, counts and `external_actions: 0`.

**Expected negative control, not a passed result until executed:** v1.1 signed execution denies the revoked approval, while v0.7 legacy outbox dispatch still produces a fake-sink acknowledgment. The test fixture uses public, deliberately nonsecret HMAC keys, a caller-supplied clock and disposable SQLite databases. No human identity, consent, real task, external connector or physical device is involved.

## Consequence / design boundary

Revocation of **future receipt creation** and cancellation of **already staged work** are different semantics. An authorization design must explicitly define whether cancellation stops pending work, already-dispatched work, or neither. This experiment tests only the former implementation's missing link to the latter.

A check performed before delivery alone is not sufficient: a revocation may race with a separate sink's side effect. The next candidate must (a) retire or block all legacy direct dispatch entry points; (b) bind each outbox item to its verified approval digest; (c) define a serialized cancellation-versus-dispatch order for the *fictional* local test adapter; (d) test process termination between sink effect and acknowledgment; and (e) explicitly disclose that separate databases cannot guarantee general external exactly-once execution.

## Evidence and limitations

- Source: `test_revocation_outbox_gap_v13.py`, `demo_revocation_outbox_gap_v13.py`, v1.1 boundary and v0.7 outbox on draft PR #10.
- Version: v1.3; Python standard library; run environment and hosted job identifiers **TBD** until verified.
- Baseline: v1.1 revocable signed execution; comparison: v0.7 legacy staged delivery.
- Measurements: two order-specific assertions; expected fake sink rows = 1; actual hosted outcome **TBD**.
- External actions: **0 by design**; real-world effectiveness, human error, physical power loss, consent, authentication, security assurance and independent review **TBD**.
- Decision: **do not advance maturity**. Keep issue #11 open; reframe as read-only if no bypass-free, auditable cancellation contract can be built.

Do not merge or release this research as an authorization security control. The value of this experiment is exposing a falsifiable safety boundary, not claiming it has been closed.
