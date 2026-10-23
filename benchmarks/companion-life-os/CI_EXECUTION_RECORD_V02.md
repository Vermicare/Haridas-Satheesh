# Companion authorization v0.2 — CI execution record

**Recorded:** 2026-10-24 (Asia/Kolkata); GitHub execution timestamps 2026-10-23 UTC. **Evidence type:** fictional software contract checks, **not** authenticated approval, external security assessment, production integration or human-consent validation.

- Proposed change: [Draft PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10).
- Tested head: `b6a1a8a7435c5f42dc0e20fd7c03dedf58f083c3`.
- Baseline validator blob: `ca0a3dbd2fba2ab1a7f55d978a13d7202f56cda0` (unchanged).
- Baseline fictional fixture blob: `c703e17ccccf11c76867d2e5c2e4c7e9d0f8d40f` (unchanged).
- New guard blob: `005ee4a1850c465aee2598342c921a79da70e4fc`.
- New regression tests blob: `bb55786627ea5d7daa389d9d9f80f78e02e73509`.
- New demonstration blob: `cb7af6347997197f9bbdbe26561ff434b60395ad`.

## Independent CI environments

| Workflow run | Environment | Regression log | Demo step | Result artifact |
|---|---|---|---|---|
| [Push #40013441837](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40013441837) | GitHub-hosted Windows, Python 3.13 | **16 tests, OK** (job 120619357799) | passed | `companion-authorization-v02-windows-latest` |
| [Push #40013441837](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40013441837) | GitHub-hosted Ubuntu, Python 3.13 | **16 tests, OK** (job 120619357928) | passed | `companion-authorization-v02-ubuntu-latest` |
| [PR #40013470946](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40013470946) | Pull-request workflow | completed successfully | passed | inspect run artifacts |

The original [Companion Life OS benchmark](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40013470934) also passed on this PR head. GitHub reported two generated demo artifacts on the push workflow; their byte-level cross-platform equivalence was **not** checked and remains **TBD**.

## Decision / limitations

Two regression tests intentionally **succeed** by demonstrating the old `can_execute` function accepts a spoofed fictional `approved_by` string and repeat calls. The separate v0.2 candidate blocks these inputs under simulated trust assumptions. It does **not** implement identity proof, signed authorization, durable atomic consumption, safe concurrent execution, a real connector, or an authenticated correction receipt.

**Decision:** preserve the negative evidence and leave PR draft. No maturity advancement, release, operational value or security certification. Next gate: [Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11).
