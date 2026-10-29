# CORTEX v0.5 — incomplete-source negative control and gold-aware audit

**Date:** 2026-10-29. **Stage:** Architecture / R&D (unchanged). **Inputs:** invented fictional records only. **Human reviewers:** 0. **External actions:** 0. **Private submissions:** none.

## Falsifiable finding

The original `evaluator.py` reports `source_span_traceability = 1.0` for a semantically exact object whose `source` is only a **nonempty proper subset** of the frozen ground-truth source IDs. This follows from its `ps.issubset(gs)` criterion. Thus `1.0` does **not** mean full-span provenance. A second concern is that the predecessor `D0` referenced by the fixture is absent from its ground-truth decision list and cannot be authenticated from that fixture alone. Neither finding invalidates the narrower original exact-match extraction score.

The additive `provenance_oracle_v05.py` performs a stricter, **post-hoc gold-aware** check. It counts incomplete source spans, invented source IDs, negative-example contamination, duplicate IDs, malformed/empty spans and semantic-signature mismatches. Its JSON output contains counts only, never source strings, source identifiers, reviewer IDs or original texts. An empty candidate yields `NOT_EVALUABLE`, not a spurious pass. External predecessor validation remains `TBD` when the fictional archive is not supplied.

## Reproduce

From `benchmarks/cortex` with Python 3.13 and standard library only:

```sh
python -B -m unittest -v test_provenance_oracle_v05.py
python -B baseline.py fixture.json > /tmp/cortex-fictional-candidate.json
python -B provenance_oracle_v05.py fixture.json /tmp/cortex-fictional-candidate.json
```

`/tmp` is illustrative on Unix; use a private temporary directory on other platforms. **Do not publish completed human annotations or real meeting data.** This is a diagnostic for frozen synthetic ground truth, **not** a production validator: it deliberately reads gold labels and must not be used on unseen predictions or represented as blinded semantic accuracy.

## Predeclared checks and evidence boundary

Thirteen local adversarial tests exercise: partial-span false pass in the original evaluator, exact-span success, unknown IDs, negative-source contamination, duplicated IDs, empty/malformed sources, unmatched semantic signatures, empty-candidate handling, non-fictional rejection, duplicate fixture IDs, private-text suppression and input immutability. The original `evaluator.py` and frozen fixture are unchanged.

**Local development environment:** Linux, Python 3.13.5; exact runner image TBD. **CI cross-platform results:** TBD until a hosted run is observed and its job logs inspected. **Physical/human review:** none. **Human correction burden, semantic accuracy, independence and external validation:** TBD.

**Decision:** retain Architecture / R&D. Next, freeze a separate fictional archive containing explicit predecessor history and independently adjudicated source-span requirements; recruit voluntary reviewers only with privacy safeguards and measure real correction time against manual structured notes. Reframe if source lineage cannot be authenticated or correction burden exceeds the manual baseline. No release or patentability assertion.
