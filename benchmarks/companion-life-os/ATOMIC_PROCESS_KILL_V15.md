# Companion v1.5 — actual child-process termination at fictional atomic sink/ack commit

**Date:** 2026-10-28. **Status:** verified in [GitHub Actions #40673893645](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40673893645) at tested commit `d93e39712ad493a0d27ef5aee308b5c46f87a7a8`; Ubuntu **129/129** and Windows **129/129** tests passed, including **4/4 new child-process kill tests per OS**. Both job logs inspected; demo generation and artifact upload succeeded. **Branch:** unmerged draft [PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10). **Maturity:** unchanged; fictional software-contract research.

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
- Hosted run conditions: Ubuntu Python **3.13.17** and Windows Python **3.13.16**, as printed in the logs; exact runner image revision, SQLite library version, journal mode and synchronous setting **TBD**. Four new tests passed on each platform; 129/129 total on each. Uploaded ZIP member bytes were **not** independently inspected.
- A passing test supports only the predeclared local fictional process-crash ordering. No maturity advance, merge, release or real consent claim.

## Provenance / next gate

Source: `atomic_revocation_delivery_v14.py` (unchanged), new `test_atomic_process_kill_v15.py`, new `demo_atomic_process_kill_v15.py`, fictional `scenario.json`. The original v1.4 [protocol](ATOMIC_REVOCATION_DELIVERY_V14.md) and [legacy-bypass negative control](REVOCATION_OUTBOX_GAP_V13.md) remain authoritative.

**Next decisive falsification:** retire or block all old dispatch/write entry points in a separately versioned fictional adapter and demonstrate red/green negative controls against direct legacy calls. Independently review the threat model before any action-capable integration. If the bypass cannot be closed, reframe to a read-only advisor.

## Execution / learning (2026-10-28)

[Ubuntu and Windows CI #40673893645](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40673893645) completed successfully. Ubuntu job `122767269818` passed 129 tests in 1.471 seconds; Windows job `122767269343` passed 129 tests in 10.425 seconds. Each log independently shows all four actual `os._exit` tests passing and `demo-v15.json` generation. Artifact uploads completed (Ubuntu `12808504687`, Windows `12809487428`). The observed outcomes agree with the preregistered state matrix; there is no performance comparison or claim about power-loss safety. No failures were observed in this run; the known legacy bypass remains a separate verified negative result.
