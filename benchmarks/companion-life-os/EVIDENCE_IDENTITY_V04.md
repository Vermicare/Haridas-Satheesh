# Companion — ambiguous fictional evidence and trust-container controls (v0.4)

**2026-10-24 · Synthetic contract only · No real identity, connector or action.** This is a narrow follow-up to [v0.3](DURABLE_SQLITE_V03.md), not a replacement for its verified SQLite concurrency/restart results. Original `authorization_guard_v02.py`, `scenario.json`, `validator.py`, and frozen v0.1 benchmark are unchanged.

## Hypothesis and before-fix negative controls

The v0.3 durable store called the v0.2 guard without validating evidence-ID uniqueness or the **type** of the supplied principal allowlist. The v0.2 guard builds an evidence dictionary by ID and uses Python `principal in trusted_principals` membership.

Three independently executable *fictional* negative controls failed as expected against the published v0.3 source (`fc52ef2d4aaf157b0ded2f330d3c742df5ad579f`):

1. Two evidence records with the same `E1` ID, one untrusted and one trusted, were accepted after dictionary overwrite. A decision reference was therefore ambiguous.
2. A single string containing `fictional-user` as a substring was accepted as a principal allowlist, even though no set of approved identities was supplied.
3. A decision referencing `E1` twice was accepted, creating duplicate source citations.

These are **structural contract failures in a fictional simulator**, not observed production security vulnerabilities.

## Correction and reproduction

`authorization_store_v03.py` now rejects duplicate/empty/non-string evidence IDs, repeated decision references, and non-set/non-frozenset `trusted_principals` before evaluating the grant or returning a stored receipt. A valid `frozenset` remains accepted. No new external action capability is introduced.

From `benchmarks/companion-life-os` with Python 3.13 and stdlib:

```bash
python -m unittest -v test_authorization_guard_v02 test_authorization_store_v03
python demo_authorization_store_v03.py
```

| Evidence field | Value |
|---|---|
| Before-fix source Git blob | `fc52ef2d4aaf157b0ded2f330d3c742df5ad579f` |
| Corrected source Git blob | `910374f1d643d45199c961c48bed29b6f2fd265f` |
| Corrected tests Git blob | `18726f6a523ef1de937f83b0829c5eeee7707651` |
| Runtime | CPython 3.13.5, Linux x86_64; Python standard library; temporary SQLite database per test |
| Before-fix result | 3/3 new negative controls **failed to reject** invalid inputs (expected failing tests) |
| After-fix local result | 31/31 v0.2 + v0.3/v0.4 tests passed in each of two isolated temporary directories |
| Normalized test-log SHA-256 | `699e9a5084049cd828c781edeca2a8d61db58d95724f7ebd3b53227c463bc4a6` (both runs; elapsed seconds normalized only) |
| Fictional demo SHA-256 | `f167367cd7489479cf85a0028a16468b97c79c4926faa90d7eb603e962313349` (both runs, byte-identical) |
| Randomness | None in fixtures; concurrent scheduling is not deterministic but receipt count is asserted |
| GitHub Actions | **TBD until the final branch head completes Linux/Windows CI** |
| Actual identity, signed source, trusted clock, real connector, multi-host exactly-once, correction lineage, reviewer burden | **TBD** |

## Decision and limits

**Retain synthetic Simulation / contract-testing evidence only.** An attacker who controls `scenario`, `trusted_principals`, local SQLite bytes or the caller's clock can still fabricate the entire experiment. A set of strings is not authentication. The validator cannot verify real-world provenance, physical data or consent. SQLite transactions do not make external connector effects atomic. The correction improves *local input-contract consistency*, not the private Companion implementation.

Next evidence gate remains [Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11): authenticated sandbox principal and issuance, durable outbox/ack reconciliation with fault injection, append-only correction lineage and independent review. Reframe toward read-only advice if these boundaries cannot be enforced.
