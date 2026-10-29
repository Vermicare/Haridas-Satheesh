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
