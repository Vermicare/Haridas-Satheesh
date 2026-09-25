# CORTEX Synthetic Governance Benchmark

**Project stage:** Architecture / R&D  
**Benchmark status:** Specification — results are TBD

## Purpose

Test whether a bounded governance-memory pipeline can extract and preserve decisions, actions and their lineage from a fully fictional workflow without creating unsupported governance facts. This benchmark uses synthetic content only; no employer, client, meeting, personal or proprietary data belongs here.

## Evidence question

Can CORTEX produce auditable governance records with useful precision and traceability while keeping false positives and human correction burden low enough to justify structured memory?

## Synthetic fixture

Create a fictional meeting/transcript fixture with explicit ground truth for:
- decisions and superseded/reversed decisions,
- actions, owners and due dates,
- risks, assumptions, issues and dependencies,
- approvals and source spans,
- ambiguous statements and discussion that must not become an action/decision,
- missing fields that must remain unknown.

The fixture and ground truth must be versioned separately.

## Baselines

1. Deterministic/rule-oriented extraction baseline.
2. Structured CORTEX extraction pipeline.
3. Optional model-assisted variant only after the deterministic evaluation harness is reproducible.

## Predeclared metrics

| Metric | Result |
|---|---:|
| Decision precision / recall / F1 | TBD |
| Action precision / recall / F1 | TBD |
| False-positive rate | TBD |
| Unsupported-field rate | TBD |
| Owner attribution accuracy | TBD |
| Due-date attribution accuracy | TBD |
| Source-span traceability | TBD |
| Decision/reversal lineage accuracy | TBD |
| Follow-up completeness | TBD |
| Human correction/review burden | TBD |

Metric definitions and matching rules must be fixed before publishing results.

## Minimal reproducible package

- synthetic input fixture and machine-readable ground truth,
- deterministic baseline and CORTEX evaluator,
- pinned environment/dependencies,
- fixed configuration/seed where applicable,
- machine-readable output and benchmark table,
- failure/learning log,
- test instructions and limitations.

## Acceptance criteria

- A clean environment can reproduce the evaluation.
- Every extracted governance object can be traced to a source span or explicitly marked unsupported.
- Ambiguous/non-action text is tested as a negative case.
- Reversed/superseded decisions preserve lineage rather than silently overwriting history.
- Unknown fields remain unknown rather than being inferred without evidence.
- Results come from the evaluator and are never manually invented.
- No private or employer-derived content is required.

## Advance criterion

CORTEX remains **Architecture / R&D** until a reproducible synthetic benchmark demonstrates useful extraction and lineage performance with explicitly measured review burden.

## Kill / reframe criterion

Simplify or reframe the structured-memory approach if false positives, unsupported attribution or correction burden erase its governance value, or if reliable source lineage cannot be maintained.

## Next implementation step

Build the smallest executable fixture + evaluator before expanding the architecture or adding more narrative documentation.
