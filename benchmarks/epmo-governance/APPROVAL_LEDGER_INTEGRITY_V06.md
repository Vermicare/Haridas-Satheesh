# EPMO fictional approval-ledger integrity v0.6 — 2026-10-25

**Scope:** Independent, read-only structural audit of the *fictional* v0.5 SQLite approval-consumption tables. No real actions, credentials, employer records, or external data.

## Hypothesis and method

Can a separate reader detect inconsistent approval/receipt state after simulated corruption without changing the database? The baseline is the v0.5 writer's own successful receipt path. The v0.6 auditor opens SQLite with `mode=ro` and `query_only=ON`, reads both tables in one transaction, checks every approval and receipt, and produces a deterministic canonical snapshot digest. It checks schema presence, nonblank bindings, nonnegative times, consumption/receipt one-to-one agreement, expiry, scope, action, actor, nonce and request/receipt linkage.

Run from `benchmarks/epmo-governance` with standard-library Python:

```sh
python -B -m unittest -v test_verify_approval_ledger_v06.py
python -B demo_approval_ledger_integrity_45s.py
```

The short demonstration creates a temporary *fictional* database, consumes one fictional approval, verifies it, changes one receipt scope using a deliberate SQL fault injection, and shows the audit rejecting the inconsistency. It then deletes the temporary database. It does not touch external systems.

## Evidence and negative controls

- Local CPython **3.13.5**, SQLite **3.46.1**, Linux, Python standard library only, network not used; two separate local runs, including one clean-directory copy, each **22/22 tests passed**.
- Cases cover positive consumed/unconsumed states; deterministic read-only output; missing DB/schema; missing/orphan receipt; scope/action/actor/nonce/request/receipt mismatch; partial consumption; invalid expiry/time/type; explicit fictional origin.
- **Important negative result:** after both the approval and receipt actor fields are changed to the same forged value, the structural checker **accepts** their mutual consistency. This is an intentional documented blind spot, not a tamper-resistance claim.
- Initial local test falsely expected SQLite to preserve the string `'100'` in an INTEGER-affinity column; SQLite converted it to integer 100. The test was corrected to use `'not-a-time'`, which remains invalid. This was a **test design correction**, not a production defect.
- Source SHA-256: `05c07a53261c3ec7f040d6303b3825b7b46f8f2b62276313783f8831e029f6e5`.
- Test SHA-256: `ffb760e858727f594e72262f7cc7b80f2c142c44d9307f6c77eb851eaac73813`.
- Demo SHA-256: `cd8bad8aa0af0f7abe5096e9465ecc2560b62cc8214df47f409b02818cbd4e23`.
- Local demo JSON SHA-256: `09cffbf0490577907399a3b6b105344ff86f9bb0adad338583b6304e70960cd0`.
- Cross-platform CI for v0.6: **TBD until a final-head run is verified**. This local result must not be represented as independent GitHub CI.
- The prior v0.5 verified cross-platform result is preserved in [v0.5 evidence](FICTIONAL_APPROVAL_CONSUMPTION_V05.md).

## Decision and maturity

**Remain Research / Simulation.** This detects internally inconsistent SQLite state only. A database administrator can forge mutually consistent rows, delete all evidence, or alter the verifier; neither issuer identity nor time is trusted. There is no cryptographic signature, append-only external witness, trusted action adapter, transactional outbox, real correction, deployment, human validation or measured reviewer burden. Unknown values remain **TBD**.

**Next evidence-producing experiment:** Bind the v0.5 atomic gate to a sandbox identity provider, trusted-clock abstraction and transactional fake-action outbox, then reconcile the resulting receipts against the v0.4 replay under crashes, replay and adversarial cross-request races. Only after that measure blinded human correction time.

**Four lenses:** hiring manager—inspectable executable test suite; technical reviewer—read-only consistency and explicit coordinated-forgery failure; innovation leader—potential reusable lineage invariant without integrated proof; founder—no users, ROI, market validation or IP/patentability conclusion.

**Kill/reframe:** stop claims of security if a policy bypass survives negative controls; reframe the feature as an offline consistency diagnostic if independent authenticity cannot be established. Never publish employer information to strengthen a portfolio claim.
