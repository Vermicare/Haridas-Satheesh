# CORTEX — semantic reviewer-pair readiness v0.3 (2026-10-28)

**Stage:** Architecture / R&D, unchanged. **Evidence:** deterministic fictional-only negative controls, not independent human annotation. **Actual reviewers, semantic agreement, annotation accuracy, measured correction burden:** TBD. **External actions:** none.

## Falsifiable integration gap

The existing [v0.1 pair preflight](reviewer_pair_preflight_v01.py) accepts two well-formed, hash-bound fictional reviewer submissions containing only object type, source ID and historical citation. It reports `pair_valid=true` and source-signature overlap even when neither decision has a semantic statement. The separately available [v0.2 individual annotation contract](SEMANTIC_ANNOTATION_CONTRACT_V02.md) rejects this incomplete shape, but the v0.1 pair command did not call it. A caller using the older pair command alone could misinterpret structural readiness as readiness for semantic adjudication.

**Preserved red control:** two source-only fictional decision submissions are accepted by v0.1. **Additive green gate:** [v0.3 pair checker](reviewer_pair_semantic_gate_v03.py) requires the unchanged v0.1 pair checks **and** the unchanged v0.2 semantic contract for **both** submissions. The same two incomplete submissions now return `pair_ready=false` and per-reviewer error codes. A complete fictional pair returns `pair_ready=true` with only aggregate source-signature counts; `semantic_agreement`, `human_independence`, `adjudicated_gold` and `correction_burden` remain `TBD`.

The new command is **not** an extractor, semantic equivalence evaluator, reviewer identity check or privacy guarantee. The old v0.1 command is intentionally preserved for historical reproducibility; consumers must explicitly use v0.3 for pair semantic readiness. A structurally valid empty annotation list is permitted: do not force fabricated records.

## Reproduce — no private inputs required for tests

From `benchmarks/cortex` in CPython 3.13:

```sh
python -B -m unittest -v test_reviewer_pair_semantic_gate_v03.py
```

For actual voluntary submissions, run **locally outside the repository**:

```sh
python -B reviewer_pair_semantic_gate_v03.py check blind_case_20261024.json blind_archive_20261024.json /private/reviewer-A.json /private/reviewer-B.json
```

Never commit completed submissions, reviewer identifiers, contacts or outreach logs. The CLI returns error codes and aggregate counts, not source text, object IDs, reviewer codes or paths. It cannot establish actual reviewer independence or authentic elapsed time.

## Executed evidence and provenance

- [GitHub Actions run #40689993941](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40689993941) at executable commit `0cb760bcfbff6596a1211c3069b998b54e0942b4`: **189/189 tests passed on Ubuntu, 189/189 on Windows**, including **15 new v0.3 adversarial tests per platform**. Both job logs and job conclusions inspected. Frozen case/archive raw-byte checks and the previously pinned synthetic lineage-output digest checks also completed successfully.
- Negative controls include source-only false readiness, missing semantic fields/schema, wrong status, unsupported fields, duplicate pseudonym, missing archival citation, mismatched source hash, malformed/oversized input, and private-string non-disclosure. No actual human annotation was used.
- Source Git blob: `ab895d8ec042783350d4e31ac940e194121ec2e8`. Test Git blob: `7d92ba59ee72816ea1e56c7dbfe27938d1d16c99`. Workflow Git blob: `68e3b268b1a4f1545de2f0121575c7e2ee12c200`. All three reread from the draft branch.
- Execution: GitHub-hosted Ubuntu and Windows; `actions/setup-python@v5` requests Python 3.13; standard-library only. Exact Python patch versions, runner image revisions and timing measurements: **TBD**. Fixed fictional fixtures, no random seed. No external dataset or private reviewer data.
- Frozen case SHA-256: `f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d`; archive SHA-256: `897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046`. Neither input was changed.

## Decision

**No maturity advancement.** The strongest evidence is that a previously permissive two-reviewer structural gate can now reject semantic-field omissions reproducibly. The largest remaining gap is two independent, voluntary, blinded annotations with adjudicated source spans and actual review/correction times. [Issue #12](https://github.com/Vermicare/Haridas-Satheesh/issues/12) remains the decisive next experiment: freeze private labels before testing a general extractor and compare against independently timed manual notes. Reframe toward provenance-assisted review if unsupported decisions or correction burden exceed manual notes.

**Four lenses:** hiring manager — inspectable negative control and repair; technical reviewer — composition of two pre-existing contracts, not semantic validation; innovation leader — no novelty or patentability conclusion; founder — no user, deployment or commercial benefit measured. Do not merge or release based solely on this synthetic readiness gate.
