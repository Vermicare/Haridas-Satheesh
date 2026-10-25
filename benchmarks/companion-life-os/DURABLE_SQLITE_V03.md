# Companion — SQLite idempotency negative controls v0.3

**2026-10-24 · Synthetic software experiment only.** No identity proof, trusted clock, real connector, private Companion code, personal data, or external side effects. **No maturity advancement.**

## Question and baseline

Can a **single-host fictional** approval receipt survive a new store instance, concurrent callers and injected exceptions without producing duplicate *simulated* receipts? The v0.2 [in-memory guard](authorization_guard_v02.py) has only a process-local nonce set; it cannot preserve replay state across restart. Its original tests and frozen v0.1 fixture remain unchanged.

## Reproduce (30–90 seconds)

Python 3.13 / standard library; from this directory:

```bash
python -m unittest -v test_authorization_guard_v02 test_authorization_store_v03
python demo_authorization_store_v03.py > demo-v03.json
```

The [SQLite experiment](authorization_store_v03.py) calls the unchanged v0.2 fictional contract validator, then uses a local SQLite `BEGIN IMMEDIATE` transaction, a unique nonce key, a SHA-256 request fingerprint and a stored JSON receipt. A byte-equivalent retry returns the stored receipt marked `idempotent_replay: true`; a changed request using the same nonce is rejected. No connector is called.

## Evidence registry

| Field | Evidence |
|---|---|
| Baseline | `authorization_guard_v02.py` Git blob `005ee4a1850c465aee2598342c921a79da70e4fc` |
| New source | `authorization_store_v03.py` Git blob `fc52ef2d4aaf157b0ded2f330d3c742df5ad579f` |
| New tests | `test_authorization_store_v03.py` Git blob `904912b188084e7fc50847a046b0ee0de4b81b6e` |
| New demo | `demo_authorization_store_v03.py` Git blob `b5b3c34802352fa7e2f14a95094c486e57e7b70b` |
| Fixture | Existing fictional `scenario.json`, extended in memory by test setup |
| Runtime | CPython 3.13.5 / Linux local; GitHub-hosted OS/version per workflow run |
| Randomness | None; 16 concurrent attempts use one identical fictional grant |
| Predeclared outcomes | 1 first receipt, 15 idempotent replies; restart replay; rollback on pre-commit injected exception; idempotent retry after post-commit injected exception; changed scope/actor/expired grant rejected |
| Local execution | 26/26 v0.2 + v0.3 tests passed in two independent local Linux runs (CPython 3.13.5; original v0.1 fixture, baseline validator, v0.2 guard and v0.2 test Git blob SHAs verified byte-identical) |
| GitHub CI | [PR CI run #40071368125](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40071368125) **passed** at head `ddbc2e9ffc4140299046d8ca66e9c6a4687f2d93`: Ubuntu **26 tests, OK** and Windows **26 tests, OK**, plus both fictional demos/artifact uploads; original Companion benchmark [CI #40071368127](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40071368127) also passed |
| Real actions | 0 by construction, not an observed production metric |
| Real authentication, clock integrity, real connector, distributed exactly-once, physical crash/power loss, correction receipts, reviewer time | **TBD** |

## Failure/learning and boundaries

The v0.2 guard has no persistent consumption. The new local SQLite store prevents a second **simulated** receipt insert when callers race for the same nonce, and returns a stored receipt after reopening the database. Injected Python exceptions before commit roll back; after commit, a retry finds the original receipt. This is **not** a kill -9, power-failure, network partition, multi-host or real connector experiment. SQLite's atomic database transaction does **not** make an external side effect atomic. An actual connector would require an outbox, idempotency key and reconciliation protocol.

The fictional principal and clock are **caller-supplied**, not independently authenticated or trusted. The request fingerprint is an integrity comparison, not a signature. A local adversary with database access can alter records. There is no correction/reversal lineage or reviewer-burden measurement yet.

**Decision:** retain public evidence as synthetic Simulation / contract testing; keep draft and unmerged. Next: [Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11) — verified sandbox identity, trusted issuance, transactional outbox with fault injection, append-only correction receipts and independent review. Reframe as read-only advisory if these boundaries cannot be enforced with reasonable cost.
