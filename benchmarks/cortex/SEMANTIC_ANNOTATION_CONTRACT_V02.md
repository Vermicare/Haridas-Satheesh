# CORTEX — prospective semantic annotation contract v0.2

**Prepared:** 2026-10-27. **Maturity:** Architecture / R&D (unchanged). **Inputs:** entirely fictional. **Human reviewers, adjudicated gold labels, correction-time measurements, extractor accuracy:** TBD.

## Decision-changing evidence gap

The existing v0.1 blinded-review intake verifies packet hashes, source IDs, record IDs, a reviewer pseudonym, and archival predecessor citations. It **does not require a decision statement, action description, risk statement, dependency statement, or conditional-follow-up description**. Therefore a source-only submission can pass the structural gate but cannot support a later semantic extraction/annotation comparison. Source-signature overlap is not semantic agreement.

This additive v0.2 contract requires **semantic fields to be present** without asserting that their contents are correct. The original blinded packet, archive, frozen baseline, evaluator and v0.1 submission template remain unchanged.

## Versioned, prospective shape

The new `reviewer_submission_template_v02.json` is intentionally **unfilled and invalid**: `R00` and `TBD` are placeholders, not reviewer evidence. Completed submissions must be kept **outside the Git checkout**, with private reviewer codes and no public outreach log.

The `annotation_schema_version` must equal `cortex-fictional-annotation-v0.2`. The `method` is `manual_structured_notes`. All objects retain the v0.1 source/record-ID checks and v0.4 archive-citation check. Additional fields:

| Kind | Required semantic fields | Explicit unknowns |
| --- | --- | --- |
| decision | `statement`, `status` | `status: null` if not supported |
| action | `action`, `owner`, `due` | `owner: null`, `due: null` if not supported |
| risk | `statement`, `status` | `status: null` if not supported |
| dependency | `statement` | No unsupported invented dependencies |
| conditional follow-up | `condition`, `action` | Omit the object if not a supported follow-up |

Text is nonblank, bounded to 500 characters, and rejects NUL/control characters. Owner is at most 120 characters. Due dates are valid ISO calendar dates or `null`. Unknown fields are rejected to prevent undocumented scoring assumptions. The v0.1 source/citation gates still apply. A **valid empty object list is allowed**: no annotation should be fabricated to fill a quota.

## Reproduce (Python 3.13, standard library)

From `benchmarks/cortex`:

```bash
python -B -m unittest -v test_semantic_annotation_contract_v02.py test_semantic_annotation_integration_v02.py
python -B semantic_annotation_contract_v02.py check blind_case_20261024.json blind_archive_20261024.json /outside-git/private-reviewer-v02.json
```

The second command must return nonzero for an unfilled template. It checks the frozen case/archive SHA-256, existing v0.1/v0.4 provenance gates, and v0.2 semantic shape. It returns only aggregate error codes, never annotation text, IDs, paths, identities, or measured human results. It cannot authenticate the author of a submission.

**Local evidence:** 20/20 direct shape tests passed on the prepared exact-source Python file on this run; Python/runtime version for that local container is not yet pinned in a published registry. The six additional integrated tests and full cross-platform CI are **pending verification**; do not claim those passed until inspected.

## Predeclared next experiment

Two voluntary independent reviewers, if recruited, annotate the already frozen fictional packet without seeing model output or one another's labels. Freeze private submissions and adjudicated source spans **before** evaluating a general extractor. Then compare correction burden with independently timed manual notes using counterbalanced cases/reviewers; one case alone supports descriptive findings only. Report per-kind precision/recall/F1, unsupported claims, source completeness, lineage, disagreements, actual times, and provenance. All values are **TBD**.

**Advance only when** independent labels and measured correction burden support the claim. **Kill/reframe** toward provenance-only assistance if unsupported records or correction burden exceed manual notes. This is a schema-readiness improvement, not independent review, semantic validity, actual efficiency, product deployment or a maturity upgrade.

## Provenance / boundaries

Original blinded packet hashes: case `f6357accbd87e11ffcaf1a2d39a085b0611719de6953cd3e4789ccacbb96344d`; archive `897ba394a392ffd63b5561500e5350573570c835fc699c0fd453148d4e3c8046`. Frozen evaluator, synthetic results and original v0.1 reviewer template were not modified. The contract cannot verify semantic truth, reviewer independence, real elapsed time, confidentiality of a malicious caller, or external effectiveness. No employer data or personal reviewer records are included.
