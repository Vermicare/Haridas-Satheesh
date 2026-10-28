# Companion v1.4 — same-database fictional cancellation experiment

**Date:** 2026-10-28. **Branch:** unmerged draft PR #10. **Maturity:** unchanged; fictional software-contract experiment, not a production authorization mechanism. **Hosted execution:** TBD until job logs are inspected.

## Question and predeclared decision

Does binding the revocation check, simulated delivery and acknowledgment to **one SQLite write transaction** remove the v1.3 revoked-before-dispatch negative result **for this isolated new adapter**, while preserving the known legacy bypass?

Predeclared pass conditions (all required): (1) revoke-before-dispatch creates **zero** new v1.4 fake sink rows; (2) dispatch-before-revoke leaves exactly **one** previously committed fake row and replay does not create a second; (3) injected precommit failure rolls back both sink and acknowledgment; (4) postcommit failure retries idempotently; (5) concurrent calls create one fake row; (6) direct legacy v0.7 outbox still reproduces its known **unsafe** behavior, proving the overall system is **not fixed**.

## Architecture and threat boundary

The existing v1.1 fictional signed boundary verifies the test-only identity/approval tokens and writes a receipt. v1.4 staging binds the existing receipt payload to the approval-token SHA-256 digest, rechecking revocation inside a `BEGIN IMMEDIATE` transaction. v1.4 dispatch rechecks the same revocation table and writes **both** the fake sink row and acknowledgment in the **same database transaction**. A revocation committed before dispatch wins; a dispatch committed before revocation is already completed and cannot be undone.

`FictionalOutbox` v0.7 and `FictionalIdempotentSink` v0.7 are deliberately **unchanged**. They remain an alternate route that can deliver fictional work after revocation. Any claim of global cancellation safety is **false** until legacy dispatch entry points are retired/blocked and all connectors enforce the new boundary. This experiment has **no external connector**, no human identity verification, no consent proof, no trusted clock, no network, no real actions, and no clinical/commercial claims. A local test-harness operator may revoke; it is not authenticated.

SQLite's [transaction documentation](https://www.sqlite.org/lang_transaction.html) describes single-writer behavior and `BEGIN IMMEDIATE`; its [isolation documentation](https://www.sqlite.org/isolation.html) explains that writes serialize. The [WAL documentation](https://www.sqlite.org/wal.html) warns that atomicity across multiple attached databases is not generally preserved in WAL mode. v1.4 therefore deliberately uses **one** database for the fake sink. This does **not** prove physical power-loss durability or arbitrary external exactly-once effects.

## Reproduce

From `benchmarks/companion-life-os` with Python 3.13 and only the standard library:

```sh
python -B -m unittest -v test_atomic_revocation_delivery_v14
python -B demo_atomic_revocation_delivery_v14.py
```

The demonstration emits a single JSON line containing the cancellation outcome and `external_actions: 0`. The test suite includes the v1.3 legacy-bypass negative control, intentionally demonstrating the unsafe old route.

## Evidence registry (pre-execution)

- Source: `atomic_revocation_delivery_v14.py`, `test_atomic_revocation_delivery_v14.py`, `demo_atomic_revocation_delivery_v14.py`.
- Comparison: v1.3 [verified unsafe legacy dispatch](REVOCATION_OUTBOX_GAP_V13.md).
- Fixtures: public fictional `scenario.json`, deliberately public HMAC test keys, disposable local SQLite files.
- Run conditions: Python 3.13 requested; exact patch, runner image, SQLite version, journal mode, synchronous mode **TBD** until inspected.
- Metrics: nine adversarial test cases; expected v1.4 fake sink counts 0/1 depending on ordering; real external actions 0.
- Hosted Ubuntu/Windows test counts: **TBD**; no success is claimed before inspecting logs.
- Physical power-loss tests: **not performed**. Human reviewers, security audit and real identity: **TBD**.
- Failure/learning: v1.3 legacy route is intentionally retained as a reproducible counterexample; one-database transaction semantics do not protect independent adapters.
- Advancement decision: **no maturity advancement**, no merge/release. Only consider a stronger boundary after legacy paths are blocked, subprocess termination tests are reproduced and independently reviewed.

## Next falsification

Test actual subprocess termination at each commit boundary, then explicitly prevent every legacy dispatch path in a separately versioned adapter; demonstrate a negative control that fails before the change and passes after it. Do not call this production-grade consent or exactly-once delivery.
