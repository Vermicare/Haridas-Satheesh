# CORTEX — fictional archive-reference and transfer stress gate

**2026-10-24 | Synthetic-only | Stage remains Architecture / R&D**

## Decision-changing result

The committed v0.1 baseline has exact-signature F1 **1.0 in each of five categories** on the original fixture, despite its unresolved predecessor `D0`. On a separately authored, fictional meeting with new utterance IDs and a new context, the same frozen-only baseline emits **zero governance objects**: exact-signature F1 **0.0 in each of five categories**. This is an *expected limitation of a deliberately hard-coded demonstration baseline*, not a performance estimate for a general CORTEX extractor or a statistically valid distribution-shift study.

The earlier additive fixture preflight accepts a historical `record_ref` as soon as it is nonempty. A negative control removes the purported archive record while retaining the string reference: the earlier preflight returns no errors. The new `audit_archive` checks that each declared historical record reference resolves to an actual *fixture-internal* archive object with matching decision ID and nonempty text. It rejects missing records, duplicate references, wrong IDs and empty text. **An internally consistent fictional archive is not authenticated history.**

## Reproduce

Run from `benchmarks/cortex` with CPython 3.13 (stdlib only):

```bash
python -B -m unittest -v fixture_integrity_preflight.py test_lineage_shift.py
python -B run_lineage_shift.py
sha256sum synthetic_lineage_shift_results.json
```

The original `fixture.json`, `baseline.py` and `evaluator.py` are unchanged. `independent_scenario_v03.json` is **author-created fictional data** derived from a local October 23 test fixture, with a newly declared *fictional* archive record. It was not blinded or human-adjudicated. The generated report is deterministic JSON (LF, UTF-8, sorted keys) with the expected SHA-256 `2c3d060df1932318cc64dba980946ebaad3c47fd56a7509b488f9f53e2dc6180`.

## Limits, advancement and stop rule

- Structural source-ID and archive-reference checks are not semantic, legal, provenance-authenticity or employer-data validation.
- The exact-match legacy evaluator may award high F1 even when lineage is unresolved. Present fixture readiness alongside score; do not silently rewrite historical evidence.
- No real workflow, external review, measured reviewer time, business impact, model generalization, production authorization or deployment evidence exists.
- Next: have independent reviewers annotate a **new unseen fictional meeting** and genuine fictional archive documents, freeze labels before extractor execution, record disagreements, traceability and correction minutes. Compare a general extractor to a manual structured-note baseline. Do not advance without reproducible unseen-case quality and acceptable review burden.
- Reframe if structured-memory false positives or correction time outweigh the value of traceable decisions.

**No release, stage change, public real-world performance claim, or employer information.**
