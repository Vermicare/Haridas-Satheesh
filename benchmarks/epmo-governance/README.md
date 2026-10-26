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

## v0.5 — atomic one-use fictional approval consumption (2026-10-25)

The isolated [v0.5 SQLite gate](FICTIONAL_APPROVAL_CONSUMPTION_V05.md) now creates an approval-consumption receipt **atomically** under a single `BEGIN IMMEDIATE` transaction. The [27 new adversarial tests](test_approval_consumption_v05.py) and [short deterministic demo](demo_approval_consumption_45s.py) cover concurrent callers, exact one-use semantics, idempotent retry, scope/nonce/expiry checks, request/receipt collisions, and crash-before/after-commit recovery. [GitHub CI #40151625112](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40151625112) passed **79/79 tests separately on Ubuntu and Windows** (Python 3.13); [registry](APPROVAL_CONSUMPTION_V05_REGISTRY.json).

**Limits:** fictional test-seeded approvals, declared (unauthenticated) actors, untrusted test clock, no external actions or correction adapter, and **no integration** yet with the v0.4 replay reconciler. No security certification, employer-data claim, maturity advancement, release or deployment. Next: identity/time-bound integration and transactional fake-action/outbox tests.

## v0.6 — independent read-only SQLite integrity audit (2026-10-25)

The [v0.6 structural auditor](APPROVAL_LEDGER_INTEGRITY_V06.md) checks the v0.5 fictional approval and consumption-receipt tables against each other, including missing/orphan receipts, mismatched actor/action/scope/nonce, expired/invalid timestamps and partial consumption. Its [22 adversarial tests](test_verify_approval_ledger_v06.py) passed twice locally on Linux/Python 3.13.5; [short demo](demo_approval_ledger_integrity_45s.py) injects a forged scope and shows rejection. [Machine-readable registry](APPROVAL_LEDGER_INTEGRITY_V06_REGISTRY.json) records hashes and unknowns; v0.6 [cross-platform CI #40174154959](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40174154959) passed **101/101 tests on both Ubuntu and Windows**.

**Critical negative control:** coordinated changes to both approval and receipt actor fields remain internally consistent and are **not detected**. This is a read-only consistency diagnostic, not tamper resistance, identity authentication or a complete v0.4–v0.5 integration. No stage change, external action, deployment or release.

## v0.7 — fictional blinded reviewer-burden preflight (2026-10-26)

The [v0.7 packet generator and strict private scorer](blinded_review_preflight_v07.py) create **16 fictional governance decisions** (3 valid, 13 invalid) using the existing `governance_demo.evaluate` policy as a synthetic oracle. Two case-identical packets use reversed seeded order for manual-notes and structured-review arms. A separate private gold key is generated **locally only**; do not commit the key, reviewer responses or participant identifiers.

From `benchmarks/epmo-governance`, generate into a **new private directory outside the repository**:

~~~sh
python -B blinded_review_preflight_v07.py --out /path/outside/repo/private_epmo_packet
python -B -m unittest discover -v
~~~

The private scorer expects a JSON object with `origin="FICTIONAL_SYNTHETIC"`, `version="0.7"`, the exact packet `arm`, and a `decisions` array of 16 unique objects, each with `case_id`, boolean `accept`, and numeric `seconds`. After independent responses are collected privately, run:

~~~sh
python -B blinded_review_preflight_v07.py --score --packet PRIVATE_PACKET.json --gold PRIVATE_gold.json --response PRIVATE_response.json
~~~

**Verified contract evidence:** [final-code GitHub CI #40222952196](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40222952196) passed **117/117 tests on Ubuntu and Windows** (Python 3.13), including **16 additive tests**. This verifies packet generation and scorer behavior, **not** independent reviewer performance. [Protocol and limitations](BLINDED_REVIEW_PREFLIGHT_V07.md) · [machine-readable registry](BLINDED_REVIEW_PREFLIGHT_V07_REGISTRY.json).

**Human review results remain TBD.** The deterministic public generator allows reconstruction of the key; this is only procedural blinding. No human recruitment, external action, employer data, measured correction burden, maturity change or release. Next: predeclared independent reviewer comparison and separately the identity/trusted-clock/outbox gate in [Issue #14](https://github.com/Vermicare/Haridas-Satheesh/issues/14).

## v0.8 — bind reviewer packets to private gold (2026-10-26)

A targeted negative control demonstrated that the v0.7 scorer accepted altered fictional candidate evidence, context or instructions when case IDs remained unchanged. [Before-fix CI #40265362490](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40265362490) ran 120 Ubuntu tests with **three expected failures**; the superseded Windows job was cancelled. The original v0.7 source/tests and their verified evidence remain unchanged.

The separate [v0.8 scorer](blinded_review_preflight_v08.py) now hashes the complete packet into its private gold key and rejects missing, swapped or mismatched bindings and malformed labels. [Final CI #40265457537](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40265457537) passed **139/139 tests on Ubuntu and 139/139 on Windows** (Python 3.13). See [failure and limitations](REVIEW_PACKET_BINDING_V08.md) and [machine-readable registry](REVIEW_PACKET_BINDING_V08_REGISTRY.json).

**Not cryptographic authentication:** a coordinated packet/key forgery remains possible. The manual and structured packets still lack substantively different review aids, so no treatment effect can be inferred. Human review results, correction burden and real deployment remain **TBD**. Next: distinct interventions, independent reviewer assignment, private consented data, and separate authenticated sandbox gate. No maturity change or release.

## v0.9 — matched-case reviewer treatment contrast (2026-10-26)

The earlier v0.8 reviewer packets were **not meaningfully differentiated**. [v0.9](REVIEW_TREATMENT_V09.md) keeps all **16 identical fictional raw cases in the same order** across arms, but adds a deterministic field-comparison worksheet to the structured arm only. The manual arm sees raw event notes; neither arm receives a policy verdict. [Source](review_treatment_v09.py) · [adversarial tests](test_review_treatment_v09.py).

This is a **preregistered presentation contrast, not human evidence**. No reviewers have participated, no measured false-approval rate, time benefit, authenticated identity, production action, employer data, ROI, or external validation exists. Both packets and a separate gold key must be generated privately outside Git; the public demo shows counts/hashes only. **Verified executable-head CI [#40352437149](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40352437149): 156/156 tests passed on Ubuntu and Windows**, CPython 3.13.16; both logs inspected, and the public treatment demo produced identical packet hashes. [Registry](REVIEW_TREATMENT_V09_REGISTRY.json). Next: consented independent between-subject reviewer assignment and protected collection, plus Issue #14's independent sandbox identity/time/outbox gate. No stage change, release or deployment.
