# EPMO Governance — Fictional Approval and Correction Replay v0.1

**Independent research/simulation demo, not employer software or production evidence.** No private employer processes, named stakeholders, credentials, Microsoft 365 tenant access or external actions are included.

## 30–60 second reproduction

~~~sh
cd benchmarks/epmo-governance
python -m unittest discover -v
python governance_demo.py synthetic_scenario.json --output demo_result.json
python -c "import json; x=json.load(open('demo_result.json')); print(x['accepted'], x['rejected'], x['external_actions'])"
~~~

The six explicitly fictional events produce **4 accepted**, **2 rejected** (premature execution and repeated execution), **0 real actions**. Results include per-event input SHA-256, acceptance reasons and a linked audit digest.

## Evidence, provenance and limits

- CPython 3.13.5/Linux, Python standard library; executed **2026-10-24**. **19/19** local regression tests passed. Two independent clean-directory reruns each passed 19/19 and produced identical output SHA-256 **1b4c7e80f4e7338226aa3f020e51312baabf0d62805731ea978e60e1851939c7**.
- Tests cover declared roles, approval ordering, scope, expiry, replay, duplicate IDs, time ordering, receipt binding, correction reasons, and digest tampering.
- GitHub CI **verified**: [run #40041342338](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40041342338) passed on Python 3.13 **Linux and Windows**, with 19/19 regression tests and the fictional receipt assertion in both jobs.
- Actor roles are **asserted by the fixture, not authenticated**. The digest chain can be recomputed and is not tamper-proof or signed. A correction changes **fictional state**, not any real external action.
- This does **not** measure employer delivery, cycle time, handoff reduction, ROI, real-world security or operational readiness. All remain **TBD**.

## Hypothesis / architecture

Fictional input -> schema/time check -> declared-role and approval policy -> accept/reject -> digest-linked audit -> fictional request state/correction. Reusable concepts overlap with Companion authorization, CORTEX lineage and IoT provenance, but no integrated product exists.

## Decision gates

**Retain as synthetic research/simulation. No maturity advancement.** Advance only after an independent authenticated sandbox test of durable atomic one-use approval, crash/restart and concurrency, verified action/compensation receipts, and measured reviewer burden versus a manual fictional baseline. Reframe if added governance complexity increases human correction burden or cannot preserve safe reversible action boundaries.

**Four-lens review:** Hiring managers can inspect executable workflow policy; technical reviewers can challenge the untrusted actor map and hash limits; innovation reviewers can test reuse; founders have no evidence yet of market demand or commercial return.

**Confidentiality:** This is a deliberately invented, vendor-neutral scenario. It does not reproduce internal company logic, documents, identifiers or architecture.

## v0.2 — cross-request receipt uniqueness (2026-10-24; fictional-only)

A new adversarial test exposed a concrete failure: after request 01 was **corrected**, a second fictional request could reuse the first request's execution `receipt_id` (`r1`) and still be accepted. Reusing receipt identifiers makes an audit receipt ambiguous across requests. The [before-fix CI run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40082736541) reproduced this false acceptance: Ubuntu **20/21** tests passed and the duplicate-receipt negative control failed as expected (Windows was cancelled by the superseding push).

The corrected replay reserves receipt identifiers for the entire in-memory fictional session, even after correction, and rejects reuse across requests. A distinct-receipt positive control remains accepted. The [corrected CI run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40082777613) passed **21/21 tests on Linux and 21/21 on Windows** (CPython 3.13, standard library). The original six-event demo remains **4 accepted / 2 rejected / 0 external actions**. The original source/fixture v0.1 evidence above is preserved; follow-up source/test Git blobs, failure and run conditions are recorded in [EXPERIMENT_REGISTRY.json](EXPERIMENT_REGISTRY.json).

**Boundary:** uniqueness exists only within one fictional replay, not across restarts or distributed workers. Roles and times are operator-declared; receipts are not authenticated, signed, or bound to real actions. No real-world security, governance accuracy, production deployment or employer performance is established. **No maturity advancement.** Next: durable globally unique receipts, authenticated sandbox actors, transactional replay protection, and inspectable correction lineage.


## v0.3–v0.4 — durable receipts and replay/ledger reconciliation (2026-10-24–25)

The [v0.3 SQLite receipt experiment](DURABLE_SQLITE_V03.md) adds local durable uniqueness, idempotent retry, concurrent caller and crash/restart tests. The [v0.4 read-only reconciliation experiment](REPLAY_LEDGER_RECONCILIATION_V04.md) now checks that **all** persisted fictional receipts match accepted replay executions/corrections; it rejects missing, extra, scope/approval/correction mismatches. A [short fictional demonstration](demo_reconciliation_45s.py) shows both a positive match and a deliberately injected extra-row failure.

**Verified v0.4:** [GitHub CI #40135124046](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40135124046) passed **52/52 tests separately on Ubuntu and Windows** (Python 3.13, standard library); [machine-readable registry](REPLAY_LEDGER_RECONCILIATION_V04_REGISTRY.json). The original fictional 4 accepted / 2 rejected / 0 external-action baseline remains unchanged.

**Critical boundary:** read-only reconciliation is not transactional approval consumption or actor authentication. A mutually forged scenario and ledger can still agree. Trusted timestamps, action/compensation, human review and employer metrics are **TBD**. No maturity advancement or release.
