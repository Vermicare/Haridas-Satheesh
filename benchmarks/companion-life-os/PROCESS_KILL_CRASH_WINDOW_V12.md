# Companion v1.2 — process-kill SQLite crash-window experiment

**Date:** 2026-10-28 (Asia/Kolkata). **Scope:** entirely fictional local SQLite software. **Maturity:** unchanged (private implementation not evaluated; public synthetic contract evidence). **No personal data, employer data, network requests, authenticated human, physical power cut or external connector.**

## Question and predeclared expectations

The v1.1 revocation boundary serializes fictional approval revocation and receipt insertion using SQLite `BEGIN IMMEDIATE`. Can a fresh process distinguish a transaction interrupted **before commit** from a transaction committed **before the caller receives a response**, for both receipt creation and revocation?

| Child operation | Injected termination | Expected persisted row after restart | Expected subsequent behavior |
|---|---|---|---|
| Fictional receipt insertion | Before `Connection.commit()` | 0 receipts | Retry creates first receipt |
| Fictional receipt insertion | After `Connection.commit()` returns | 1 receipt | Retry returns same receipt idempotently |
| Fictional approval revocation | Before `Connection.commit()` | 0 revocations | Approval still permits fictional first use |
| Fictional approval revocation | After `Connection.commit()` returns | 1 revocation | Signed approval denied, no receipt |

These tests intentionally kill **only a disposable Python child process** using `os._exit`; the parent reopens the same temporary SQLite file. They use the existing `FictionalRevocableBoundary`, `FictionalRevocableStore`, v1.0 test issuer, v0.1 fictional scenario, and public test-only keys. A `sqlite3.Connection` subclass injects the kill immediately around the actual commit call. A child that does not hit the intended hook exits with a different code, causing the parent test to fail. All tests check row counts and restart behavior, not merely process exit codes.

## Reproduce

From `benchmarks/companion-life-os`:

```sh
python -B -m unittest -v test_process_kill_v12
python -B demo_process_kill_v12.py
```

No nonstandard Python dependencies. Run conditions: hosted Python 3.13 per workflow; exact patch version, SQLite library version, journal mode, filesystem and durability configuration are **TBD** until recorded in hosted logs/JSON. The short JSON demo prints actual Python/SQLite/operating-system versions and a machine-readable success/failure summary; do not infer physical power-cut behavior from a successful software-process termination.

## Observed execution (code-bearing CI)

[Cross-platform GitHub Actions run #40596438679](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40596438679) at commit `605680616e8f606b07f84c7e0d3bd1290552e7b9`: **114/114 tests passed on Ubuntu and 114/114 on Windows**; all four new process-kill tests are visible as passed in both inspected job logs. The four expected cases above were checked on both systems. Earlier v1.1 test count was 110 per OS. **Zero real external actions.** This is an actual hosted software execution, not physical measurement or an operational authorization claim.

**Code identity:** `test_process_kill_v12.py` Git blob `2bfd5d37ef50671fbe0b233fe7d0461b55eb4390`; `demo_process_kill_v12.py` Git blob `1eff7f3cfdca197ccbd0ed83720a0ba48b9991e5`. Workflow adds the test module to the existing Ubuntu/Windows matrix and uploads a JSON demo. **Final-head workflow/demonstration outcome: pending verification at the time of this evidence note; do not claim its success without inspecting that run.**

## Evidence boundary and negative learning

The observed four-case result exercises SQLite's local transactional commit boundary under process termination. It does **not** demonstrate physical power-loss durability, filesystem corruption resistance, distributed exactly-once effects, authenticated consent, revocation enforcement across legacy adapters, trusted timestamps, real-world safety or a production user benefit. The independent legacy `FictionalDurableStore` write path remains a known bypass if a caller uses it directly against the same database; v1.2 does **not** close that routing gap. A non-idempotent external connector can still duplicate effects despite an idempotent local receipt.

**Decision:** retain synthetic contract maturity; no merge, release, pilot or safety claim. Next experiment: prohibit all legacy write paths in a separately versioned test adapter, demonstrate that revocation cannot be bypassed through any public adapter, and inject process termination at the fictional outbox/ack boundary. Independently review test identity and key management before any real integration.

**Four-lens review:** hiring manager — reproducible cross-platform failure-injection tests; technical reviewer — commit boundaries measured but crash/power-loss and legacy routing remain open; innovation leader — reusable consent/abort architecture hypothesis, not established novelty; founder — no user, deployment, value, regulatory or commercial validation.

References: [SQLite transactions](https://www.sqlite.org/lang_transaction.html), [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html), [issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11).
