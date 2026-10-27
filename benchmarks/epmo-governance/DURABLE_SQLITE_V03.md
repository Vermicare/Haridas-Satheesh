# EPMO — durable fictional receipt sandbox v0.3

**2026-10-24 · Isolated storage-contract experiment · No maturity advancement**

## Question and scope

Can SQLite preserve **fictional** receipt uniqueness across concurrent callers, connection reopen, and controlled pre/post-commit failures, including a later correction marker?

This additive experiment does **not** modify the original six-event governance_demo.py fixture. It is not the authenticated, policy-checked end-to-end gate requested by Issue #14: approval_id is a caller-provided string, **not evidence of approval**.

## Reproduce (Python standard library only)

From benchmarks/epmo-governance:

~~~sh
python -B -m unittest discover -v
python -B durable_receipt_sandbox.py --output fictional_durable_demo.json
~~~

The demo uses a temporary local SQLite database and reports created → idempotent → corrected, one fictional ledger row, **0 external actions**, and explicit identity_authenticated=false and approval_policy_verified=false. No network, employer data, credentials, tenant or real workflow are used.

## Evidence and provenance

| Field | Verified |
|---|---|
| Origin | FICTIONAL_SYNTHETIC |
| Source Git blob | 5d7902c468b34dfa20e34a9325c63a93e155d7fc |
| Test Git blob | a4c3550022e907a59511538e550141ad544aa937 |
| Source SHA-256 | 67487f7b09c09cee0b644e18ae4778a7df3e12925d5200f25906649b82ed4ff9 |
| Test SHA-256 | 308244009ba17256d388f0ae6087529ba6e1a4bd95304888ae1397b4e19215f3 |
| Deterministic demo JSON SHA-256 | 1dd567faf378ebc9ab6a8a625151667a4d495c94c6901b35b46fa23b6d9997e3 |
| Local environment | CPython 3.13.5, Linux, stdlib, network off; seed N/A |
| Clean-directory local reruns | **17/17 additive tests passed twice**; identical demo JSON hash |
| GitHub Actions | [Run #40112459325](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40112459325): **38/38 tests passed on Linux and Windows**; original fictional receipt assertions passed |
| Real external actions | **0** |
| Real identity, approval, execution and reviewer-time metrics | **TBD / not implemented** |

Published source/test Git blobs were reread and match locally executed files. Source commit 398e23d3fa21960080dcf7f8264d7df44d6b005b; test commit fb5d094bcaa494a8a053599ad8276c2414ca661e. These results establish local storage invariants, not database tamper resistance.

## Tested failures

- Sixteen concurrent identical fictional requests: **1 created, 15 idempotent**, one row (thread workers, not distributed processes).
- Two different request IDs claiming the same receipt concurrently: one created, one conflict.
- Reuse of corrected receipt by another request; changed request scope or receipt: rejected.
- Before-commit injected crash: transaction rollback and later successful creation.
- After-commit injected crash: subsequent retry is idempotent.
- Correction survives reopening; changed reason or wrong request binding: rejected.
- Correction pre/post-commit faults; unknown receipts, blank fields, nonfictional origin: rejected.

## Limits and next gate

The ledger does **not** verify approval policy, actor identity, expiry, or action authorization. It is not integrated with governance_demo.py, does not perform any external action or real compensation, and has no signed audit, trusted timestamps, multi-host consensus, power-loss validation, or human-review study. A corrected row is only a fictional marker.

**Decision: remain Research / Simulation. No release or maturity advancement.** Next, integrate a separately authenticated sandbox actor and policy gate with the durable store, then test approved/expired cases and a stubbed fictional adapter with real sandbox receipt/compensation outcomes. Measure reviewer correction burden against manual fictional notes only after blinded cases exist.

**Kill/reframe:** simplify if durable approval safety cannot be established or reviewer workload outweighs manual governance.
