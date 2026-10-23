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
