# Companion v1.5 — actual child-process termination at fictional atomic sink/ack commit

**Date:** 2026-10-28. **Status:** independent hosted execution **TBD** until final-head job logs are inspected. **Branch:** unmerged draft [PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10). **Maturity:** unchanged; fictional software-contract research.

## Question / falsifiable prediction

The v1.4 adapter's injected `RuntimeError` is not an operating-system process crash. Does a **real disposable child-process termination** immediately before versus after `sqlite3.Connection.commit()` preserve the all-or-nothing property of its **same-database** fictional sink and acknowledgment?

Predeclared outcomes, each on a fresh temporary SQLite database:

| Child termination | Expected persisted state | After restart |
|---|---|---|
| Before unrevoked sink/ack commit | `pending`; 0 fake sink rows | Retry writes exactly 1 fake row |
| After unrevoked sink/ack commit | `acked`; 1 fake sink row | Retry is idempotent; still 1 |
| Before revoked cancellation commit | `pending`; 0 fake sink rows; revocation persists | Retry cancels; 0 fake sink rows |
| After revoked cancellation commit | `cancelled`; 0 fake sink rows | Retry denied; 0 fake sink rows |

The subprocess must exit with **71** (before commit) or **72** (after commit), otherwise the test **fails**. The parent checks SQLite `PRAGMA integrity_check` and reopens the adapter. This deliberately tests the real `os._exit` path, rather than catching a Python exception.

## Reproduce

From `benchmarks/companion-life-os`, with standard-library Python 3.13 and no external accounts:

```sh
python -B -m unittest -v test_atomic_process_kill_v15
python -B demo_atomic_process_kill_v15.py
```

`test_atomic_process_kill_v15.py` defines four adversarial tests. `demo_atomic_process_kill_v15.py` prints a single JSON line contrasting before/after commit. CI runs the new tests alongside all previous fictional authorization regressions on Ubuntu and Windows. Each child is launched by `subprocess.run` with a 20-second timeout and only touches a disposable local database.

## Threat and interpretation boundaries

- The fake sink and acknowledgment share **one SQLite database**, unlike the separate-database legacy v0.7 adapter.
- This is **process termination**, not physical power removal, filesystem fault injection, disk-cache flush verification or cross-machine distributed transactions.
- Test-only public keys, a fixture-supplied clock, a fictional approval and synthetic scenario are used. There is **no authenticated real human**, no external connector and **zero real-world actions**.
- The known **v0.7 direct outbox and legacy base-store bypasses remain**. These tests cannot establish global revocation or authorization safety.
- `PRAGMA integrity_check` is a limited structural check, not a complete integrity or security proof.
- SQLite version, OS runner image, journal/synchronous settings and final test counts: **TBD** until verified logs.
- A passing test supports only the predeclared local fictional process-crash ordering. No maturity advance, merge, release or real consent claim.

## Provenance / next gate

Source: `atomic_revocation_delivery_v14.py` (unchanged), new `test_atomic_process_kill_v15.py`, new `demo_atomic_process_kill_v15.py`, fictional `scenario.json`. The original v1.4 [protocol](ATOMIC_REVOCATION_DELIVERY_V14.md) and [legacy-bypass negative control](REVOCATION_OUTBOX_GAP_V13.md) remain authoritative.

**Next decisive falsification:** retire or block all old dispatch/write entry points in a separately versioned fictional adapter and demonstrate red/green negative controls against direct legacy calls. Independently review the threat model before any action-capable integration. If the bypass cannot be closed, reframe to a read-only advisor.
