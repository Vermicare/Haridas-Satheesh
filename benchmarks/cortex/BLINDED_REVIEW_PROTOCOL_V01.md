# CORTEX — unseen fictional governance review packet v0.1

**Prepared:** 2026-10-24. **Stage:** Architecture / R&D (unchanged). **Study:** NOT STARTED. **Reviewer annotations, independent adjudication, correction time, extraction performance, and external validation: TBD.**

## Research decision

The existing CORTEX `fixture.json` embeds its ground truth alongside the meeting, and the intentionally fixture-specific baseline emits no governance objects on a different fictional meeting. Neither can be used as an *unseen, independently labeled* effectiveness result. This additive packet creates a distinct, label-free case and separately versioned fictional archive for Issue #12. No original fixture, evaluator, scores or verified CI evidence are replaced.

## Inputs and provenance

- `blind_case_20261024.json`: 12 **author-created fictional** utterances about a greenhouse sensor rehearsal. The case includes an explicit correction, a proposal rejected as a decision, a conditional follow-up, an unassigned risk, a vague delivery prediction, and a referenced historical policy.
- `blind_archive_20261024.json`: two **author-created fictional** archived decisions H-11 and H-12 with separate source identifiers. Archive contents are *not* authenticated historical facts.
- `blind_review_preflight.py`: Python 3.13 standard-library-only integrity and private submission structural checks; **not** an extractor or semantic scorer.
- `test_blind_review_preflight.py`: adversarial tests using invented test-only submissions. A passing test is not a human-review result.
- `reviewer_submission_template.json`: incomplete schema illustration only. `TBD` timings deliberately fail the completed-submission check.

Reproduce packet manifest (no private inputs):

```bash
cd benchmarks/cortex
python -B -m unittest -v test_blind_review_preflight.py
python -B blind_review_preflight.py manifest blind_case_20261024.json blind_archive_20261024.json
```

Expected source byte SHA-256 from the prepared packet:

- case: `f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d`
- archive: `897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046`

Any source-byte change requires a **new case version** and invalidates existing hash-bound annotations. Unknown run conditions outside Python and OS: TBD. This is not an external data source.

## Prospective blinded evaluation — not yet performed

1. Freeze this exact label-free case and archive by SHA-256 **before** any independent reviewer sees extractor output or candidate labels. Do not release the eventual gold labels until independent annotations are locked.
2. If two independent reviewers voluntarily agree, supply only the fictional case and archive, the annotation schema, and definitions of decisions/actions/risks/dependencies/conditional follow-ups. Do not provide the original baseline's output or other reviewers' labels. Store reviewer contact information and raw submissions privately, not on GitHub. No reviewer is currently committed.
3. Record anonymized annotation records and actual wall-clock review seconds. Resolve disagreement using documented rules and source evidence; lock adjudicated gold with a timestamp and source hashes. **Never synthesize human timings or label consensus.**
4. Only after label freeze, execute a **general** extractor with frozen revision and configuration on the unseen case; preserve raw output, hashes, environment, negative cases and failures. The existing exact-string fixture-specific baseline is a *non-generalization control*, not a credible general extractor.
5. For correction burden, have independent reviewers correct extractor output without prior exposure to this case. Compare against separately timed manual structured notes from a non-overlapping reviewer group (or separate, complexity-matched cases with counterbalanced order). With only one case or two reviewers, report descriptive observations only and mark causal uplift **TBD**.

## Predeclared scoring rules and gates

For each kind: TP = an adjudicated object with semantically equivalent fields **and** defensible utterance/archive source, FP = unsupported or duplicate extracted object, FN = missed adjudicated object; report precision, recall and F1 (undefined denominator as `null`, never silently `1`). Source-span precision = supported cited utterance IDs / all cited utterance IDs; missing/unknown IDs are failures. Decision supersession must resolve to a real fictional archive decision and respect explicit correction statements; ambiguous forks require reviewer adjudication, not silent acceptance. Record negative-example promotions and unsupported field count. Reviewer correction time and manual-note time are measured seconds, not guessed.

**Advance to a larger independently reviewed study only if:** both annotations are source-traceable; all supersession references resolve; no fabricated historical decisions; all material disagreements are adjudicated; extraction code is general (not tuned to this packet); and correction burden can be compared with a fair manual comparator. Exploratory target for later larger evaluation: decision/action precision >=0.90, source-span precision >=0.95, no fabricated predecessor, and median correction time no greater than manual notes; these thresholds are **targets, not achieved results**. A single fictional case cannot establish general performance.

**Kill/reframe:** if unsupported governance records or reviewer correction time exceed the manual-note baseline, narrow CORTEX to a provenance/lineage tool rather than an autonomous extraction system. Do not upgrade maturity on structural tests or reviewer packet preparation.

## Limits and confidentiality

No actual people, meetings, employers, customer records, hardware measurements, model accuracy, reviewer results or deployments are represented. The source checker does not authenticate physical or organizational history, evaluate semantic correctness, verify reviewer independence, enforce confidentiality, or prevent a malicious author from falsifying times. Public source files may be published; completed reviewer submissions, contacts and outreach tracking remain private until separately consented and sanitized. This is a preparation artifact, not evidence of external review.
