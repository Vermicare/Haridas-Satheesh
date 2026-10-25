# Companion — fictional durable correction lineage v0.5

**Experiment date:** 2026-10-25 (Asia/Kolkata). **Status:** published synthetic experiment; [GitHub Actions #40148356063](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40148356063) passed **49/49 tests on Ubuntu and Windows** at code head `c36937070f382cd0bf346c43cc91244bce7e1dda`; [original Companion benchmark #40148356065](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40148356065) passed. Later documentation-only commits were not independently rerun. **Maturity:** unchanged (private implementation In Progress; public synthetic contract evidence only).

## Research question

Can a fictional original v0.3 SQLite authorization receipt remain preserved while a separately authorized *fictional* correction is recorded as a durable, idempotent, linear append event? This is not a test of real user identity, approval provenance, or actual task updates.

## Provenance / scope

- Parent interface: `authorization_store_v03.py` from public Companion draft PR #10; this v0.5 package uses its documented `receipts(nonce,fingerprint,receipt_json)` table shape. Tests seed that shape with a **fictional original receipt**, rather than invoking the v0.3 evaluator. Full end-to-end v0.3 integration remains **TBD**.
- Input: fictional original receipt `ACT1` / `D1` / `fictional-nonce-1`, and invented correction `C1` / `AUTH-C-C1` / `correction-nonce-1`.
- Dependencies: Python 3.13.5 standard library only; SQLite from bundled `sqlite3`; Linux x86_64. Seed: N/A. No network, credentials, employer data or external actions.
- Mechanism: `BEGIN IMMEDIATE` + unique correction ID, parent-event ID and correction-grant nonce. Same-request retries return the stored event, including after a new instance; changed requests are rejected. A second correction can follow the first, but branching from one parent is rejected.
- Predeclared outcomes: original receipt unchanged; one event after 16 simultaneous identical attempts; deterministic demo; invalid principal, expiry, scope, dates, forged original, unknown parent and nonce reuse rejected; pre-commit rollback and post-commit idempotent recovery.

## Reproduce

```bash
python -m unittest -v test_correction_ledger_v05
python demo_correction_ledger_v05.py
```

Two independent local invocations passed **18/18** tests each on CPython 3.13.5 Linux; deterministic demo JSON SHA-256 in both runs: `c201dc11f56c440bce2b8f5a3398a0ae69be196ecd441ce2a97c48b12c861310`.

## Recorded cross-platform failure and correction

The first v0.5 CI runs passed the new test assertions on Ubuntu, but Windows reported **18 test cleanup errors** because `with sqlite3.connect(...)` commits without closing the database connection; Windows prevented deletion of still-open temporary SQLite files. The tests and demo were corrected to use `with closing(sqlite3.connect(...)) as db, db:`. The corrected final code passed **49/49 tests** on both operating systems, with both demos and artifact uploads successful. This was a test-harness resource-lifecycle defect, not evidence of failed authorization logic.

## Limitations / failure learning

The original receipt is **test-seeded**, not created by the real v0.3 store during this experiment. SQLite event rows are logically append-only through this API, **not tamper-evident or immutable** against an operator who can edit the database. Trust membership and the clock are caller-supplied. The correction grant is a JSON assertion, **not a cryptographic signature or authenticated consent**. A stored correction is **not** a real reversal or connector acknowledgment. Python exception injection is **not** power-failure testing. No reviewer burden, latency, accuracy, external outcomes, multi-host concurrency or security effectiveness has been measured. All are **TBD**.

## Next evidence gate

Integrate this ledger with an actual v0.3 `FictionalDurableStore.execute` receipt in CI on Ubuntu and Windows, then implement a trusted sandbox identity issuer and outbox/ack failure injection. Require independent technical review before any maturity advancement, merge or release. If durable authorization and correction complexity cannot be justified, reframe as read-only advisory.

## Four-lens check

Hiring: runnable code, not a deployed agent. Technical: test database trust boundary and the gap between receipt and external side effects. Innovation: reusable provenance pattern, not claimed novelty. Founder: reviewer burden, operational costs, liability and user value **TBD**.
