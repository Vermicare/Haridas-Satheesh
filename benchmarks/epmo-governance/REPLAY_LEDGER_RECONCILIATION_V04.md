# EPMO — fictional replay ↔ durable ledger reconciliation v0.4

**2026-10-25 (Asia/Kolkata) · additive read-only experiment · no maturity advancement**

## Research question

Can an independent read-only checker detect when the original **fictional** six-event governance replay disagrees with the separately committed SQLite receipt ledger? Prior v0.3 tests established ledger durability but did not compare its contents to the replay policy.

**Answer within tested synthetic scope:** yes. The checker recomputes the replay and its digest-linked audit, derives only **accepted** execute/correct events, and requires an exact field-for-field match against all persisted SQLite receipt rows. It fails closed on missing, extra, or changed receipts. Rejected attempts never become expected executions.

This is a **consistency checker, not an atomic authorization/consumption gate**. The fictional scenario, declared roles, and SQLite database can all be authored by the same party. A coherent forged pair can pass. A hash is not a signature.

## Reproduce (stdlib; fictional data only)

From `benchmarks/epmo-governance`:

```sh
python -B -m unittest discover -v
python -B demo_reconciliation_45s.py
```

The short demo generates an ephemeral ledger from the committed fictional fixture, confirms one accepted execution and one correction, injects an extra fictional ledger row, and confirms the independent checker rejects the mismatch. **Zero network or external actions.** The demo is suitable for a 30–90-second narrated walkthrough, not a timed human evaluation.

The CLI `reconcile_fictional_replay.py <scenario.json> <sqlite-file>` checks an existing, quiescent fictional ledger read-only; it does not create, fix, or mutate that ledger.

## Frozen inputs, provenance and verified results

| Item | Value |
|---|---|
| Fixture | Existing `synthetic_scenario.json` (six fictional events; unchanged) |
| Replay policy | Existing `governance_demo.py` (unchanged) |
| Ledger primitive | Existing `durable_receipt_sandbox.py` (unchanged) |
| Checker Git blob | `550d8d6849f319a8d12ff44ccbaa09adfcbb3504` |
| Checker tests Git blob | `d39434fc694aa06299795b2b64811f28edffc8fe` |
| Demo Git blob | `f7ea8da0898d6a12b7120448878226a5762c5085` |
| Demo tests Git blob | `5c7566ec1aa0196f7ceb14c317d41a6fd840ddfd` |
| GitHub CI | [Run #40135124046](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40135124046), commit `553cdefef836d872c4854e2c4521a1c89e37c7ff` |
| Cross-platform result | **52/52 passed separately on Ubuntu and Windows**, CPython 3.13 |
| Additive tests | **14** (12 checker + 2 demo) |
| Accepted/rejected replay events | **4 / 2** (fictional fixture, not live operations) |
| Matched executions/corrections | **1 / 1** (fixture) |
| External actions | **0** |
| Seed | N/A; deterministic fictional scenario |
| Identity, trusted time, policy consumption, compensation, reviewer burden | **TBD / not implemented** |

All four new published Git blobs were reread; final-head CI job/step results and test counts were inspected. Earlier v0.1–v0.3 evidence remains unchanged. The local test preparation used a reconstructed policy copy, so the **authoritative integrated test evidence is hosted CI against the actual committed policy**.

## Negative controls and learning

- Reject missing accepted receipt; reject an extra ledger receipt.
- Reject changed approval ID, scope, correction reason, or absent correction.
- Ignore rejected premature and replayed execute attempts when deriving expected ledger state.
- Reject an altered fictional scenario whose accepted action no longer matches the ledger.
- Reject nonfictional fixture origin.
- Preserve deterministic report output for identical quiescent inputs.
- Demonstrate an extra-row injection after a valid reconciliation; the second reconciliation rejects it.

The important learning is that durable receipt uniqueness and deterministic event-policy correctness **do not by themselves establish agreement between the two components**. This experiment detects divergence at an audit checkpoint; it does not prevent the divergence transactionally.

## Threat model, decision and next experiment

**Threats not addressed:** spoofed declared actors, forged/replaced fixture and ledger together, untrusted event timestamps, concurrent database mutation during a read, malicious SQLite administrator, trusted approval issuance, true atomic approval consumption, actual action/compensation receipts, and human correction cost. No Microsoft 365 integration or employer information is used. No production security or performance claim.

**Decision:** retain EPMO as an independent **Research / Simulation** demonstration. No merge, release, pilot, or maturity advance.

**Next evidence-producing experiment:** connect a fictional, policy-checked, **atomic one-time approval consumption** operation to the durable SQLite store, with scope/expiry/nonce/concurrent-worker/restart fault injection and a separately labeled nonproduction actor-identity stub. Only then introduce an isolated fake adapter with execution/compensation receipts and a blinded human review study. Stop/reframe if policy bypass remains possible or measured reviewer burden exceeds manual notes.
