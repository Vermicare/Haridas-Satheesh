# CORTEX — synthetic source-span completeness falsification v0.1

**Date:** 2026-10-27. **Stage:** Architecture / R&D, unchanged. **Data:** author-created fictional governance fixture only. **Human reviewers / real-workflow outcomes:** TBD.

## Question and negative control

Does the frozen CORTEX evaluator's `source_span_traceability` metric require **all** gold-cited utterances, or does it award full credit when only a nonempty subset is cited?

The original `evaluator.py` computes `ps and ps.issubset(gs)`. That is a legitimate *subset-validity* check, but it is not a completeness check. A missing required supporting utterance can receive full traceability credit. This matters for the portfolio's auditability claims, even when exact-field extraction F1 is unchanged.

**Predeclared test:** use the original committed `fixture.json` and untouched `baseline.py`. In a deep-copied synthetic candidate only, remove the second required source (`u07`) from the decision that originally cites `u06` and `u07`. Run the frozen evaluator and an **additive** strict exact-source audit side by side. Do not modify the fixture, baseline, evaluator or historical score record.

## Reproduce

From `benchmarks/cortex` with CPython 3.13 (stdlib only):

```bash
python -B -m unittest -v test_source_span_completeness_v01.py
python -B source_span_completeness_v01.py demo
```

The executable auditor classifies exact, partial, extra, mixed, missing, invalid and unsupported/duplicate candidate citations for exact-field-matched fictional objects. It rejects duplicate gold signatures and malformed gold sources; it emits aggregate counts only. A matched field signature is **not** proof of semantic equivalence. The original evaluator remains frozen.

## Verified result

| Measurement | Untouched frozen candidate | One required citation omitted |
|---|---:|---:|
| Matched fictional governance objects | 7 | 7 |
| Frozen evaluator `source_span_traceability` | 1.000000 | **1.000000** |
| New exact-source completeness | 7/7 = 1.000000 | **6/7 = 0.857143** |
| Partial-source objects | 0 | **1** |
| Frozen evaluator category F1 values | Unchanged | Unchanged |

**Interpretation:** the frozen metric overcredits an intentionally incomplete source citation in this controlled fictional negative case. This does **not** establish that the baseline extracts real meetings accurately, nor does it imply that every citation must always be identical to one subjective gold span in production. The stricter measure is an *additional diagnostic*, not a replacement for semantic adjudication.

**Execution evidence:** [GitHub Actions #40439644368](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40439644368), executable commit `85e6c406f010f91d776cd10f026c5e42e1d47a33`: **135/135 tests passed on Ubuntu and 135/135 on Windows**, including all 12 new adversarial controls; both job logs inspected. The CI demo printed strict completeness 1.0 before and 0.857143 after omission, while frozen traceability stayed 1.0. These are software/fixture results only.

**Pinned Git blobs:** original `fixture.json` `6540101a695ddeae1eb9832e627dbbff67394e00`; `baseline.py` `080fd86a451e2175c88c46339e8390072e3dcab6`; `evaluator.py` `8119649def3e893da5371a55e3baae519477b908`; new audit `f83fabe83fd6f031f402cf970abbf7bf6ccf03fa`; 12 tests `e328cf7be6acca23de0bc61634e87b0444241a72`. Machine-readable provenance: [registry](SOURCE_SPAN_COMPLETENESS_V01_REGISTRY.json).

## Failure and decision

- **Observed failure:** missing a gold-required source is not reflected in frozen source traceability, although source exactness decreases. Preserve the original score and identify its metric definition rather than silently changing historical results.
- **What remains unknown:** true semantic support, source-span ambiguity, reviewer agreement, annotation reliability, independent reviewer time, production impact, and external validation — all **TBD**.
- **Next decisive experiment:** Issue #12. Obtain voluntary blinded annotations of the unseen fictional case, adjudicate which spans are necessary versus merely relevant, freeze labels, and compare a general extractor against manual structured notes with measured correction burden.
- **Advance only when:** independent source/lineage labels and timed review support reproducible extraction with acceptable false positives and burden. **Kill/reframe:** restrict CORTEX to provenance-assisted review if unsupported records or correction effort exceed manual notes.

## Four-lens review

**Hiring manager:** a concrete falsification and regression test is more credible than a perfect self-fixture F1. **Technical reviewer:** distinguish nonempty-subset validity from complete evidence support; inspect frozen versus strict metrics separately. **Innovation leader:** provenance completeness is a precondition for governance trust, not demonstrated business value. **Founder:** no human adoption, product-market fit, legal compliance, novelty or customer benefit is established.

No employer data, reviewer submissions, identities, private outreach or confidential material were used. No release, stage advancement or merge is justified.
