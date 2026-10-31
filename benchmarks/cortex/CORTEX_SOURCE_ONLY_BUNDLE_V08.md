# CORTEX v0.8 — source-only reviewer bundle preflight (fictional, unscored)

**Prepared:** 2026-10-31. **Maturity:** Research / Architecture, unchanged. **Human reviewers, annotation agreement, correction time, external review:** TBD. This is a packaging/control artifact, not a validation study.

## Why this exists

[Issue #12](https://github.com/Vermicare/Haridas-Satheesh/issues/12) requires two genuinely independent first-pass source annotations before scoring extraction or claiming reviewer benefit. The public research branch already exposes author interpretations, example labels, expected graph edges and tests. Therefore a public link to the branch is **not** a blinded reviewer packet. Sending source-only files is necessary but **not sufficient**: reviewers must privately declare any prior exposure, and already-exposed reviewers must not be counted as blinded.

## Executable source-only package

[Builder](source_only_reviewer_bundle_v01.py) accepts **only** the exact original, author-created fictional case and archive, SHA-256 pinned to the [v0.1 protocol](BLINDED_REVIEW_PROTOCOL_V01.md):

- Case: f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d
- Archive: 897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046

It rejects byte changes (including CRLF conversion), ambiguous JSON members and malformed fictional source structure. The deterministic, uncompressed ZIP contains exactly the original case and archive plus neutral reviewer instructions. Its member names, order, timestamps and permission metadata are fixed. A manifest reports SHA-256 hashes and **TBD** study fields; it contains no private review, identity, label, outcome or timing data. The builder cannot prove that a reviewer has not previously seen public interpretations.

**Offline reproduction** (on the unmerged CORTEX research branch, Python 3.13 standard library):

```sh
cd benchmarks/cortex
python -B -m unittest -v test_source_only_reviewer_bundle_v01.py
python -B source_only_reviewer_bundle_v01.py --output /path/outside/repository/cortex-source-only-v01.zip
```

The output path must be **outside** the public Git repository, must not already exist and must have an existing private parent directory. Do not commit, upload or attach completed reviewer submissions. The hosted CI exercises the builder **in memory only**, without creating/uploading a ZIP artifact. To reproduce its exact SHA-256, rerun on an LF-preserving checkout; any byte mismatch is a failure, not a normalization opportunity.

## Negative controls and study boundary

[Nine fictional-only regression tests](test_source_only_reviewer_bundle_v01.py) cover exact ZIP members, byte determinism, source tampering, line-ending drift, injected expected labels, duplicate JSON members, refusal to write inside the repository, refusal to overwrite a private file, and aggregate-only manifest output. Initial local isolated tests: **9/9 passed** (test-only fictional fixtures, not the original full repository dependency graph). **Hosted cross-platform CI and actual pinned-source bundle verification: pending** until the modified [existing CORTEX workflow](../../.github/workflows/cortex-fixture-integrity.yml) completes successfully. Do not report a hosted PASS before inspecting both jobs.

**Before voluntary reviewer recruitment:** privately record prior exposure to the public branch and any expected interpretations; provide only the generated source-only bundle and separate blank annotation schema; lock each first-pass response independently before exposing either reviewer's labels; separately preregister adjudication and manual-note versus correction-time comparison. Any exposed reviewer must be excluded from a blinded claim or explicitly analyzed as unblinded. No reviewer is committed or contacted by this artifact.

**Advance:** only on genuinely independent source-span annotations, adjudicated disagreements and measured correction burden. **Stop/reframe:** if prior exposure makes independence unverifiable, replace the case with a newly authored unexposed fictional packet before recruitment; if unsupported governance claims or correction burden exceed manual notes, narrow to a provenance tool. No real employer/client records, claimed human result, production deployment, novelty or patentability.
