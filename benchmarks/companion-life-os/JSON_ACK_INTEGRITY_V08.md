# Companion — Stored-Acknowledgment and JSON Integrity v0.8

**Date:** 2026-10-26. **Scope:** public fictional SQLite outbox only, draft PR #10. **Stage:** Simulation / fictional software contract; no stage advancement, deployment, release or real external action.

## Predeclared hypothesis

The v0.7 local outbox should reject ambiguous JSON and refuse to report an `acked` record as success if the persisted acknowledgment is malformed or does not match the staged payload digest. Prior to the correction, its `json.loads` used default last-key-wins behavior, and the `acked` fast path returned stored JSON without validating nonce/digest/schema.

## Baseline: executable negative controls

At test-only commit `fae5cf5e8713af7d7bd9af4148814662a5327c6e`, four new regression tests were added without changing implementation:

1. Conflicting duplicate top-level `decision` keys were silently accepted.
2. Duplicate nested `audit.source` keys were silently accepted, despite the nested object not being used in dispatch.
3. A persisted `acked` JSON record with an incorrect `digest` was returned as a successful replay.
4. A persisted `acked` JSON array raised a raw `TypeError`, not a bounded contract rejection.

[Before-fix CI #40260628098](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40260628098): Ubuntu **75 tests, 3 failures + 1 error**, confirming all four cases. Other prior tests remained passing; the separate original benchmark workflow succeeded. This is deliberate red CI, not an unexplained flaky failure.

## Correction and verification

At implementation commit `43218f4c9e3c3275d1882ed6f24b83ddb2c51830`:
- `_decode` now uses a recursive JSON object-pairs hook rejecting duplicate keys, including nested objects.
- Fresh and persisted fictional adapter acknowledgments are checked for matching nonce, digest, `synthetic=true`, `external_actions=0` and one simulated action.
- Corrupted acknowledged rows fail closed with `OutboxContractError` instead of returning misleading success or an unrelated `TypeError`.

[After-fix CI #40260698802](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40260698802): **75/75 passed on Ubuntu and 75/75 on Windows**. Both test logs were inspected. CI runs on the code/test commit above; later documentation-only commits do not change executable behavior.

**Pinned code Git blob:** `8df81032b7473365836dcda5ffcd44c33648c9c0`  
**Pinned test Git blob:** `b80b560258271aba77490813adf20f3ca7d02e1d`  
**Runtime:** Python 3.13 GitHub-hosted Ubuntu/Windows; exact patch-level runtime and SQLite library versions: **TBD**.  
**Input provenance:** invented receipt, deliberately corrupted fictional SQLite rows. No real person, consent, employer system, account, device or external connector was used. Random seed: N/A.

## Reproduce

From `benchmarks/companion-life-os`:

```bash
python -m unittest -v test_authorization_guard_v02 test_authorization_store_v03 test_correction_ledger_v05 test_actual_receipt_integration_v06 test_fictional_outbox_v07
python demo_fictional_outbox_v07.py
```

The negative-control baseline is retained as commit history and the four regression tests remain in the suite.

## Limitations and next evidence gate

SHA-256 is a consistency check, **not an authenticated signature**. An actor who controls both stored payload and digest may still forge a coherent record. SQLite persistence is not proof of power-loss safety or real connector exactly-once behavior. No authenticated principal, trusted time, tamper-resistant event ledger, human review, real action, rollback, latency or benefit has been demonstrated.

**Next gate:** integrate a separate trusted fictional identity issuer and a durable policy-consumption/outbox transaction; test forged identities, nonce replay, clock manipulation, power interruption and a deliberately non-idempotent adapter. Reframe as read-only advisory if safe authorization cannot be demonstrated at measured acceptable cost.

**Four lenses:** hiring—reviewable negative controls; technical—parser ambiguity and replay integrity are bounded, not cryptographically authenticated; innovation—reusable provenance guard, not novelty claim; founder—real-world reliability and reviewer burden remain **TBD**.
