# Companion — Fictional Outbox Crash-Window Contract v0.7

**Date:** 2026-10-25. **Evidence type:** local, synthetic SQLite contract test only. **Public stage:** Simulation / fictional software contract. **Branch:** `research/companion-auth-negative-controls-20261024`; [draft PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10). No private system or real connector was tested.

## Question and baseline

Can a **v0.3-generated fictional authorization receipt** be staged for dispatch and acknowledged durably, with a recoverable crash window between the fake adapter's write and the outbox acknowledgment? The v0.6 integration already connected the real v0.3 receipt producer to the v0.5 correction ledger, but **no dispatch/ack contract** existed. This v0.7 candidate leaves the original authorization and correction implementations untouched.

## Method, provenance, and predeclared checks

- Source: `authorization_store_v03.py`, `scenario.json`, `fictional_outbox_v07.py`, `test_fictional_outbox_v07.py`. The demo uses the **actual v0.3 producer**, while most negative controls seed a clearly fictional receipt.
- Two separate disposable on-disk SQLite databases: authorization/outbox and fake adapter. A UNIQUE nonce and payload SHA-256 bind a **synthetic** fake sink effect. They do **not** attest identity or prevent an operator from editing either database.
- Test crash at **after sink commit / before outbox acknowledgment**; restart with fresh objects, retry, and check a single fake sink row. Test 16 concurrent dispatch requests, missing source, changed source, malformed/non-finite JSON, invalid acknowledgments, nonce collisions and dispatch-before-stage.
- Negative control: a deliberately non-idempotent in-memory fake sink records **two** simulated effects after the same crash/retry sequence. This proves the outbox alone cannot guarantee exactly-once behavior for an arbitrary adapter.
- Metrics: test pass count; fake sink row count after crash/retry; outbox status; simulated non-idempotent effect count. Real throughput, latency, actual connector semantics, power-loss durability, user benefit and external validation: **TBD**.
- Environment: local CPython 3.11+ standard-library `sqlite3`; exact local Python/SQLite build: **TBD**. CI requests Python 3.13 on Ubuntu/Windows; exact runner patch versions: **TBD**. Seed: N/A (deterministic fictional data).

## Reproduce

From `benchmarks/companion-life-os`:

```bash
python -m unittest -v test_fictional_outbox_v07
python demo_fictional_outbox_v07.py
```

The existing `.github/workflows/companion-authorization-v02.yml` includes the v0.7 tests in the Ubuntu/Windows matrix and uploads `demo-v07.json` with the earlier demos. Do not infer CI success until the **final commit** run is inspected.

## Observations and limitations

The locally tested synthetic outbox checks passed **13/13** after a failing overflow-JSON assertion was reproduced and the error handling corrected. The test of `1e400` revealed that Python can decode an overflowing JSON number to infinity even without a literal `Infinity`; the final parser rejects non-finite floats recursively. The non-idempotent negative control produced **two** simulated effects; the idempotent fake sink retained **one** row after crash/retry and 16 concurrent attempts. These are local simulated observations, **not external-action measurements**.

This architecture has **at-least-once delivery with a cooperative idempotent fake sink**, not generic exactly-once execution. There is no authenticated principal, trusted timestamp, distributed transaction, real task mutation, correction/reversal, tamper-resistant audit, physical power-cut test, or real adapter acknowledgment. An independent reviewer must inspect whether a real adapter actually provides durable idempotency and whether source and outbox data are independently authenticated. A forged fake receipt remains possible if the database owner can modify the original row.

**Decision:** remain Simulation; no release, deployment or maturity advancement. **Next experiment:** isolate a sandbox identity issuer and trusted clock, then test authenticated nonce-bound authorization and adapter acknowledgment under duplicate delivery and injected process crashes. Reframe as read-only advisory if the required safety properties cannot be established at acceptable measured complexity.

## Four-lens review

Hiring manager: runnable, reproducible crash/retry integration, not production automation. Technical reviewer: inspect duplicate-delivery failure mode and absence of an independent trust anchor. Innovation leader: reusable evidence-lineage/outbox pattern; no novelty or patentability claim. Founder: liability, operator effort, support cost and user value remain **TBD**.
