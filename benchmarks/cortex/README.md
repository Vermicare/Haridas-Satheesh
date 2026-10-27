# CORTEX Synthetic Governance Benchmark

**Project stage:** Architecture / R&D  
**Benchmark status:** Frozen fictional exact-match harness committed; additive fixture-integrity and fictional archive/transfer stress are under draft PR #4. Real-workflow and human-review results are TBD.

## Purpose

Test whether a bounded governance-memory pipeline can extract and preserve decisions, actions and their lineage from a fully fictional workflow without creating unsupported governance facts. This benchmark uses synthetic content only; no employer, client, meeting, personal or proprietary data belongs here.

## Evidence question

Can CORTEX produce auditable governance records with useful precision and traceability while keeping false positives and human correction burden low enough to justify structured memory?

## Synthetic fixture

The repository contains a fictional meeting/transcript fixture with explicit ground truth for:
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

## Next evidence gate

The frozen fixture's `D2` refers to missing historical decision `D0`. The original hard-coded baseline may score perfect exact-match F1 on that fixture without valid history. Draft PR #4 adds structural preflight and a separately authored **fictional** archive-linked scenario: the frozen-only baseline returns zero objects there, an expected generalization limitation. The new archive check detects dangling fixture-internal historical references, but does not authenticate them. See [archive and transfer evidence](LINEAGE_SHIFT_EVIDENCE.md).

**Next:** independently adjudicate a genuinely unseen fictional meeting and historical record with at least two reviewers, freeze labels/source spans before evaluating a general extractor, and measure disagreements, false positives, lineage validity and correction time against manual notes. All real-workflow metrics and human review time remain **TBD**. No stage advancement or release.

## Unseen fictional reviewer packet (2026-10-24; pre-review only)

[Blinded review protocol](BLINDED_REVIEW_PROTOCOL_V01.md) links a new **label-free**, entirely fictional meeting, a separately versioned fictional archive, an SHA-256-bound reviewer intake checker and 18 adversarial tests. It is deliberately **not** a scored dataset: independent annotations, gold-label adjudication, reviewer time, real-world extraction quality and external validation are all **TBD**. [Issue #12](https://github.com/Vermicare/Haridas-Satheesh/issues/12) remains open; no stage advancement follows from packet or CI readiness. Raw completed reviewer submissions and outreach records must never be committed publicly.

## Strict JSON and manifest intake regression (2026-10-25)

[Fail-closed v0.3 evidence](CORTEX_JSON_INTAKE_INTEGRITY_V03.md) and its [machine-readable registry](CORTEX_JSON_INTAKE_INTEGRITY_V03_REGISTRY.json) preserve nine test-only negative controls. Earlier CLI manifest parsing could raise on malformed structures and the JSON reader accepted duplicate keys and non-finite values. Before-fix CI reproduced 4 failed assertions plus 5 errors per OS; corrected [CI #40199139641](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40199139641) passed 69/69 tests on both Ubuntu and Windows. This is **input integrity only**, not a human-review study or general extraction result. Issue #12 remains the evidence gate; no maturity advancement.

## Illustrative provenance interoperability (2026-10-26)

[PROV-O mapping v0.1](PROV_O_MAPPING_V01.md) adds a dependency-free, synthetic-only JSON-LD-shaped mapping from the **author-created fictional ground truth** of `independent_scenario_v03.json` to provenance entities and derivation edges. The decision-supersession edge remains a distinct `cortex:supersedes` term, **not** `prov:wasRevisionOf`. [Executable mapping](prov_o_mapping_v01.py) and [19 regression tests](test_prov_o_mapping_v01.py) now include six v0.2 negative controls for duplicate historical/current decision nodes and invalid negative-example source lists. [v0.2 failure-and-repair evidence](PROV_O_MAPPING_INTEGRITY_V02.md) and [registry](PROV_O_MAPPING_INTEGRITY_V02_REGISTRY.json) record two clean local 19/19 runs; hosted latest-head Ubuntu/Windows CI is **pending verification**. This is not a general extractor, RDF/OWL conformance result, authenticated archive or human-review result. Issue #12 remains the maturity gate.

## Frozen-packet two-reviewer preflight (2026-10-26; no participants)

[Private pair preflight](reviewer_pair_preflight_v01.py) and [14 synthetic regression tests](test_reviewer_pair_preflight_v01.py) add a fail-closed readiness gate for the existing fictional blinded packet. The tool requires both original SHA-256-pinned case/archive files, distinct pseudonyms, valid archive citations, manual-note method, positive review duration, and zero correction duration. It prints only aggregate counts of exact source/signature overlap, never reviewer codes, source text or object identifiers. **It cannot verify reviewer independence, semantic agreement, actual timing or annotation quality.** Completed submissions must stay outside public Git; no reviewer data or human results were used. [Hosted CI #40372166423](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40372166423) passed 123/123 synthetic tests on both Ubuntu and Windows, including the 14 new pair controls; both job logs inspected. The CI tests use fabricated inputs only. Issue #12 and Architecture / R&D maturity remain unchanged.

## Synthetic source-span completeness negative control (2026-10-27)

[Strict citation audit v0.1](SOURCE_SPAN_COMPLETENESS_V01.md) and [machine-readable registry](SOURCE_SPAN_COMPLETENESS_V01_REGISTRY.json) preserve a **metric-definition failure** in the frozen evaluator without rewriting its code or historical scores. On the author-created seven-object fixture, deliberately omitting one of two required sources leaves the frozen `source_span_traceability` at **1.0** (it accepts a nonempty subset), while an additive exact-source diagnostic falls from **7/7 to 6/7 (0.857143)**. [GitHub CI #40439644368](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40439644368) passed **135/135 tests on Ubuntu and Windows**, including 12 new adversarial tests; both job logs inspected. This is **not** semantic support, human reviewer agreement, real extraction quality or product validation. Independent blinded source-span adjudication and measured correction burden remain **TBD** (Issue #12). No maturity change.

## Prospective semantic annotation shape gate (2026-10-27; pre-review only)

The existing v0.1 blinded intake can accept a fictional source-only governance object without any decision/action/risk text, so source-signature overlap is insufficient for later semantic comparison. [Versioned v0.2 contract](SEMANTIC_ANNOTATION_CONTRACT_V02.md), [executable shape validator](semantic_annotation_contract_v02.py), [unfilled template](reviewer_submission_template_v02.json), and [fictional negative controls](test_semantic_annotation_integration_v02.py) now require per-kind semantic fields and explicit unknown values while preserving the frozen packet and predecessor provenance gates. The template is deliberately invalid until a real private submission exists. This is annotation readiness, **not** semantic accuracy, independent reviewers, measured correction time or external validation. Issue #12 remains open; no stage change.
