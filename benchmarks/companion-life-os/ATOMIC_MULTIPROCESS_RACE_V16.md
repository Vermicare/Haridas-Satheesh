# Companion v1.6 — independent operating-system processes, fictional SQLite authorization races

**Date:** 2026-10-29. **Scope:** clean-room synthetic software experiment only; draft [PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10). **Maturity:** unchanged (In Progress; implementation private). **External actions:** zero.

## Falsifiable question

The v1.4 fictional delivery adapter and v1.5 actual child-process termination tests operate in one SQLite database. Does its revocation/dispatch ordering still produce an internally consistent state when **separate Python processes**, rather than threads, compete for the same file? Do six independent dispatcher processes produce at most one fictional sink row?

This is a regression check, not an attempt to certify an authorization system.

## Predeclared experiment and acceptance

- On each of **six fresh databases**, stage a signed **fictional** grant, hold a parent BEGIN IMMEDIATE write transaction, start two child processes (one revocation, one dispatch), wait until **both children report ready**, release the parent lock, then inspect the persisted state. The readiness marker precedes database initialization and does **not** guarantee both operations begin at the same instant or exercise both possible winners.
- Accept **either** serialized outcome: (a) dispatch wins, then revocation persists, status acked, **one** fake sink row, subsequent idempotent replay; or (b) revocation wins, dispatch is denied, status cancelled, **zero** fake sink rows, subsequent replay denied. Any inconsistent mixture, missing revocation, unexpected child exception or SQLite integrity-check failure is a test failure.
- On a separate fresh database, start **six** dispatcher processes against the same fictional nonce. Require exactly one first delivery, five idempotent replays and exactly one fake sink row.
- All child processes use disposable local files and public test-only signing keys; no network or real connector.

## Reproduce

From benchmarks/companion-life-os with Python 3.13 and the checked-out draft PR:

    python -B -m unittest -v test_atomic_multiprocess_v16
    python -B demo_atomic_multiprocess_v16.py

The second command emits one JSON object with actual test count, elapsed time, SHA-256 of the test source, success/failure and explicit limits. The automated workflow also parses and asserts this JSON before uploading it.

## Execution evidence and provenance

The **code-bearing** test head 2fc88f09a532a070184456b7e88390f7ef10bc45 passed [GitHub Actions #40788961543](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40788961543): **131/131 total tests on Ubuntu and 131/131 on Windows**, including both new tests. Both job logs were inspected. This is two new tests over the previously verified 129-test suite. Source Git blob: 3a53f0d44a1133928946072a788971e210b50a7d. Existing v1.4 adapter Git blob (unchanged): 46c194432d4d620e6929d84da5dd7bf468e0a7b0. The added demonstration and workflow-log JSON assertion passed [GitHub Actions #40789289224](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40789289224) on **both Ubuntu and Windows**, at demo-bearing head ed74e1027810638525c43fb72a2049cc448869a4: **131/131 full tests per OS**, plus **2/2 JSON-demo rerun tests per OS**, zero errors and zero external actions. Both logs were inspected; the artifact-upload steps succeeded. ZIP archive bytes were **not** independently downloaded or inspected.

The [SQLite transaction specification](https://www.sqlite.org/lang_transaction.html) and [isolation documentation](https://www.sqlite.org/isolation.html) explain why BEGIN IMMEDIATE serializes writers **within one SQLite database**. This is a documented property, not a new algorithm or a claim of patentable novelty.

## Reproducibility finding: checkout newline normalization

The v1.6 demo exposed a **non-substantive but important cross-platform byte difference**: Ubuntu checked out the test file with LF newlines (raw SHA-256 26b3b4d7c8e39de6957bec5fcca5f1177128d1d7af9339fd56daabc08fab0ece), while Windows checked it out with CRLF (raw SHA-256 11e18f5d89be483c25834bc04bb090d818dcc1ea355f5e3257b827efb03151a0). The **LF-normalized SHA-256 matched on both**: 26b3b4d7c8e39de6957bec5fcca5f1177128d1d7af9339fd56daabc08fab0ece. Both logs printed the normalized and raw digests. The Git blob identity remained pinned; never claim raw checkout-byte identity across operating systems.

**Four-lens review:** hiring manager — runnable no-network, machine-readable demonstration; technical reviewer — check same-file transaction serialization and untested interleavings; innovation leader — established SQLite locking, **not novel**; founder — known legacy bypasses and absent real authentication prevent an execution-capable deployment claim.

## Negative evidence / remaining gaps

**The old v0.7 direct outbox and v0.3 base-store entry points still bypass the v1.4 revocation boundary.** The passing tests do not remove either path. This experiment does **not** test physical power failure, multi-host synchronization, independent databases/external sinks, real identity, human consent, trustworthy time, independent security review or production authorization. SQLite runtime version, journal mode, synchronous mode and runner image revision: **TBD**. The child-readiness barrier does not force a specific interleaving; it checks allowed results only for observed executions.

**Next decisive step:** introduce a separately versioned **deny-by-default** fictional execution surface that refuses every legacy write/dispatch path, prove the previously observed unsafe direct calls now fail before any fake sink effect, and independently review the complete entry-point inventory. If the bypass cannot be closed, keep the real system read-only. No maturity upgrade, merge or release.
