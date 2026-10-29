# Companion v1.7 — receipt-to-stage revocation interleaving (fictional negative control)

**Date:** 2026-10-29. **Status:** draft experiment, no real external actions. **Maturity:** unchanged. **Parent:** [draft PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10).

## Falsifiable question

Does v1.4 `AtomicFictionalDelivery.stage` provide one atomic boundary around **both** creating the original receipt and staging its fake outbox entry? If a fictional approval is revoked after the receipt transaction commits but before the staging transaction starts, is any residual receipt usable through the legacy v0.7 outbox?

## Method and acceptance

Use a fresh temporary SQLite database for each test, public test-only keys, frozen fictional fixture and a test-injected interleaving. The mock calls the **real** v1.1 signed boundary to commit the receipt, immediately invokes the **real** revocation operation, then returns control to the unchanged v1.4 staging implementation. No timing race is claimed: the injection deterministically selects the gap. Four regression tests check normal staging, revocation before receipt, revocation between receipt/stage, and a separate legacy fake-sink dispatch from the residual receipt. Expected negative control: stage denies, v1.4 fake sink remains empty, **one previously committed receipt remains**, and the legacy outbox can still produce **one fictional** sink row. This is a **failure of end-to-end admission**, not a passing security gate.

## Reproduce

From `benchmarks/companion-life-os` on the draft branch with Python 3.13:

```sh
python -B -m unittest -v test_stage_receipt_revocation_gap_v17
python -B demo_stage_receipt_revocation_gap_v17.py
```

No dependencies beyond the Python standard library and existing draft branch modules. The demonstration prints machine-readable test counts, outcome and LF-normalized test source SHA-256. Runtime version, Git commit, runner image and hosted execution must be recorded from the actual run, never assumed.

## Interpretation and next design decision

The v1.4 **dispatch** is transactionally serialized with revocation inside one SQLite database, but its **stage** operation first calls `FictionalRevocableBoundary.execute` (receipt COMMIT) and only then opens a separate outbox staging transaction. A rejected stage can therefore leave a historical receipt. The legacy `FictionalOutbox.stage/dispatch` path does not consult revocation and can consume it. The existing v0.3 direct-store path remains a separate bypass.

A new Python facade alone cannot prove global revocation while legacy classes and same-file write access remain available. The next implementation must isolate authority and storage, make the entire entry-point inventory explicit, and demonstrate that **all** formerly unsafe routes fail closed before any real connector is considered. If this cannot be enforced, the system must remain read-only.

**Limits:** controlled deterministic interleaving, not a stochastic process race; fake SQLite sink only; no actual account, trusted identity, consent, network, real-world action, physical power loss, or independent security review. No novelty, patentability, product, or compliance claim. Existing v1.6 process-race evidence remains valid for its narrower dispatch question. No merge, release or maturity change.

**Four lenses:** Hiring — runnable failure-focused engineering; technical — two-transaction gap and legacy path are independently inspectable; innovation — explicit cross-boundary failure, not a novel algorithm; founder — execution-capable agent remains unsafe until isolation and consent evidence exist.

## Verified execution (2026-10-29)

[GitHub Actions #40802405846](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40802405846) **completed successfully** at code-bearing commit `7fe77c4a79c24c25ec118bc16fcb6057b1c6239c`. Both Ubuntu (job `123213325875`) and Windows (job `123213326228`) logs were inspected: **135/135 tests passed per operating system**, including the **four v1.7 tests**. Both machine-readable v1.7 demonstrations reported `success=true`, `tests_run=4`, `external_actions=0`, and the same LF-normalized test source SHA-256 `df6bb7bd2ef3df1ac2bc41e3cb8d52025ba8679a3545bdbe81e619d82a893a7c`. Artifact upload steps succeeded on both platforms; **artifact ZIP bytes were not independently downloaded or inspected**. The actual runner image, exact Python patch, SQLite version and journal/synchronous settings remain **TBD**.

**Observed negative result:** a revocation injected after the signed fictional receipt commits but before v1.4 outbox staging causes staging to reject, while leaving one persisted receipt. The legacy v0.7 outbox can still stage and dispatch that receipt into **one fake sink row** after revocation. This does **not** contradict v1.6's narrower same-database dispatch serialization result; it exposes a different two-transaction admission boundary. No real side effect, stage upgrade, merge, release, or safety claim.
