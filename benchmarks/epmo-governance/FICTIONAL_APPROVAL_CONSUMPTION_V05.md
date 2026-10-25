# EPMO — fictional atomic one-use approval consumption v0.5

**2026-10-25 · independent SQLite simulation · no maturity advancement.**

## Question and result

Can one **fictional, test-seeded** approval be consumed at most once across concurrent callers, connection restarts, changed request/receipt identifiers, scope/action/nonce mismatches, and injected crashes?

**Local result:** yes within this narrowly specified SQLite transaction model. A `BEGIN IMMEDIATE` transaction inserts a unique receipt and marks its approval consumed before committing. Identical retries return an idempotent result without creating another receipt. Distinct contenders fail closed. A simulated crash before commit rolls back both changes; an exception after commit is recovered by a retry.

**Not demonstrated:** authenticated actor identity, trusted approval issuance, trusted clock, tamper resistance against a database administrator, real external action, compensation, integration with the earlier v0.4 replay/ledger reconciler, or production security.

## Reproduce (standard library; no network)

From `benchmarks/epmo-governance`:

```sh
python -B -m unittest discover -v
python -B demo_approval_consumption_45s.py
```

The short demonstration returns `consumed → idempotent → rejected`, exactly one **fictional** receipt, zero external actions, `identity_authenticated=false`, and `trusted_clock=false`. The supplied `now` value is an untrusted test clock; the seeded actor identifier is an assertion, not verified identity. A caller who controls the database or issuer can forge approvals. Never connect this code to live action adapters.

## Provenance and observations

| Item | Evidence |
|---|---|
| Origin | `FICTIONAL_SYNTHETIC`; generated identifiers and test clocks |
| Source | `approval_consumption_v05.py`; SHA-256 `a294d83068e190ad5dc9ce75d006ddfd17c410c5fad6a9c90b57a179be42d36b` |
| Adversarial tests | `test_approval_consumption_v05.py`; SHA-256 `bc74fc6399e948054dc78e8375f9d79dfc428a8ab42f188466e4a91b35aaddc3` |
| Demo | `demo_approval_consumption_45s.py`; SHA-256 `32750ec31d6b178d98a5216cdfc9b62885ed545dd91dac2badeb33a72c48ef80` |
| Demo tests | `test_demo_approval_consumption_45s.py`; SHA-256 `fbdbbb8c3a1598038e79fc7a5d5d3e66050e7ca5f9009ff7bdc5962a9e613ae2` |
| Local execution | Linux, CPython 3.13.5, SQLite via standard library; 27/27 tests passed in each of two reruns |
| Deterministic demo JSON SHA-256 | `03df1a111f97be02b7ddca49c8e21cec9fb875a103b2c8d71b5fba6f61fa5c50` |
| Cross-platform GitHub CI | **TBD** until final-head job logs are checked |
| Human reviewer burden / external actions | **TBD** / 0 |

The first local run revealed a **test assertion error**, not an implementation failure: the test assumed a fixed row index despite `ORDER BY approval_id`. It was corrected to select the named approval and the entire suite reran successfully. The failed run is retained as engineering learning, not reported as a policy defect.

## Negative controls

- Two 16-worker scenarios: identical requests yield one consumed and 15 idempotent results; distinct requests yield one consumed and 15 rejected results.
- Scope, action, declared actor and nonce mismatches; unknown approval; expiry at exact boundary; reused approval with different receipt or request.
- Duplicate issuance nonce, receipt collision and request collision across approvals; both transaction tables remain consistent.
- Before/after commit crash points; connection reopen; false/negative clock, blank identifiers, invalid origin and failpoint.
- Rejected mismatches leave the approval available for a later correctly bound fictional request.

## Gate and decision

**Remain Research / Simulation.** This isolated primitive does not establish the complete original governance workflow. The next experiment must integrate approval issuance and consumption with the v0.4 replay and receipt reconciliation using a **sandbox identity provider, trusted clock abstraction, and transactional outbox**, with adversarial replay, crash/restart and fake-action compensation. Then measure blinded reviewer correction time versus manual structured notes. Reframe if policy bypass is possible or governance overhead outweighs review benefit.

**Four lenses:** hiring manager—reproducible executable artifact; technical reviewer—explicit transactional and untrusted-input limits; innovation leader—reusable lineage concept without claimed integration; founder—no user, ROI, deployment, novelty or patentability claim. No employer data or private outreach information.
