# CORTEX — gold-denominator citation coverage v0.2

**Date:** 2026-10-28. **Stage:** Architecture / R&D, unchanged. **Inputs:** original author-created fictional `fixture.json`, deterministic `baseline.py`, frozen `evaluator.py`, additive v0.1 source audit. No employer records, human participants, private reviewer submissions or real meetings.

## Question / preregistered falsification

Does the previous exact-citation metric, whose denominator is *matched candidate records*, remain perfect when an entire correct record disappears? Can a duplicate candidate coexist with a perfect exact-source ratio?

The v0.1 strict source audit measures citation quality **conditional on exact-field matching**. It does not measure missing gold objects. A deletion can therefore leave its matched-only ratio at 1.0; a duplicate can leave the same ratio at 1.0 while appearing in a separate unsupported count.

**Frozen inputs and controls:** do not modify the original fixture, baseline, evaluator or v0.1 audit. Deep-copy the candidate, (A) remove one gold-matching decision, (B) append a duplicate of a gold-matching decision, and (C) remove one required source as an independent check. The new v0.2 diagnostic reports exact citations over **all gold records**, the number of omitted gold records and the number of unsupported/duplicate predictions. The boolean clean gate requires all gold records to have exactly cited matched predictions **and** zero unsupported/duplicate predictions.

## Reproduction

From `benchmarks/cortex` in Python 3.13 (standard library only):

```bash
python -B -m unittest -v test_source_span_gold_coverage_v02.py
python -B source_span_gold_coverage_v02.py demo
```

The draft workflow `.github/workflows/cortex-fixture-integrity.yml` also executes both. Expected falsification on the seven-object fixture: original 7/7; deletion 6/7 although the legacy traceability and matched-only exact ratio stay 1.0; duplicate 7/7 but clean gate fails due to one duplicate. **Observed and verified:** [GitHub Actions #40616836860](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40616836860) at executable commit `90c990c9c23e8297551b08991081117f941b7d4d` passed **174/174 regression tests on Ubuntu and 174/174 on Windows**, including 11 new adversarial tests. Both job logs were inspected. The omission preserved legacy traceability 1.0 and matched-only exactness 1.0 but reduced gold-denominator exactness to **6/7 = 0.857143**; a duplicate left 7/7 exact citations but failed the clean gate. The test execution is synthetic-only.

## Provenance and boundaries

Source files: `fixture.json` blob `6540101a695ddeae1eb9832e627dbbff67394e00`; `baseline.py` `080fd86a451e2175c88c46339e8390072e3dcab6`; frozen `evaluator.py` `8119649def3e893da5371a55e3baae519477b908`; v0.1 audit `f83fabe83fd6f031f402cf970abbf7bf6ccf03fa`. New source blob `764e1f2f9357b4f88a08feeb5086678641a30eb0`; test blob `96cc5b9ee00d13c1adc9d69a4d0a4632cf829e09`, both reread from the draft branch. Hosted Ubuntu and Windows CI passed at the executable commit above; final documentation-head CI is checked separately. No random seed; deterministic fixture. Exact hosted Python patch version: **TBD**.

**Interpretation:** a matched-only citation-quality score is not evidence of recall. The new gold-denominator diagnostic is still exact-field and exact-citation matching against author-created labels, not proof of semantic equivalence, authentic historical provenance or human accuracy. Perfect synthetic results do not justify a general extraction or deployment claim.

**Decision:** preserve frozen historical metrics, add the recall-aware diagnostic, and keep CORTEX Architecture / R&D. Advance only after independent voluntary source-span annotations and a measured comparison with manual notes. Reframe as provenance-assisted review if unsupported records or correction burden exceed manual notes. Next decisive experiment: [Issue #12](https://github.com/Vermicare/Haridas-Satheesh/issues/12).

**Four lenses:** hiring manager — tests that challenge a perfect benchmark score; technical reviewer — explicit denominator and duplicate handling; innovation leader — no novelty conclusion; founder — no user or business outcome demonstrated. No outreach, release or merge is authorized by this experiment.
