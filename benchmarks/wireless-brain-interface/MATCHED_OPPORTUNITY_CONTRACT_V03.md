# WBI — matched-opportunity action safety contract v0.3 (2026-10-26)

**Stage:** Research / Simulation (unchanged). **Evidence class:** fictional, hand-constructed action/abstention decisions. **No EEG decoding, real false-action rate, device/clinical safety, or gate superiority established.**

## Hypothesis / decision problem

A policy can appear to reduce incorrect actions simply by abstaining more. The earlier [rest-exposure contract](REST_EXPOSURE_RATE_V02.md) correctly normalized false rest actions by T0 sample-time but did not record **opportunities to act**, wrong-direction imagery actions, or whether policies saw the same opportunities. Comparing its outputs alone could overstate safety benefit.

This **additive** v0.3 contract evaluates all three policies (ungated, confidence abstention, authorization gate) on the **identical explicit timestamp grid**. Each policy must record exactly one decision per opportunity: `T1`, `T2`, or `None` (abstain). Missing/extra/duplicate decisions fail closed. Annotation intervals must partition the recording exactly and include both T0 and imagery exposure. T0 is **excluded from imagery correctness** but **included in rest-action safety**.

## Predeclared metrics and gate

- **Imagery coverage** = actions taken on T1/T2 opportunities / all T1/T2 opportunities.
- **Incorrect-action risk** = (actions on T0 + wrong-direction T1/T2 actions) / all actions; `null` when there are no actions.
- **Correct-action recall** = correct-direction T1/T2 actions / all imagery opportunities.
- **Rest false actions per minute** = actions on T0 × sample rate × 60 / annotated T0 samples; integer numerator/denominator retained.
- **Matched-coverage comparison** = compare abstention vs gate only when absolute held-out imagery coverage difference is <= **0.05** and both act at least once; otherwise risk delta is `null`, **not zero**. This is a diagnostic tolerance, not a clinical criterion.

The shared grid controls observation opportunities, not decoder training or threshold selection. The evaluator does **not** choose thresholds. Predeclare and select those on calibration subjects, then freeze them before held-out evaluation. One fictional recording is not an independent subject-level statistical unit.

## Reproduce

From `benchmarks/wireless-brain-interface`:

```sh
python -m unittest -v test_matched_opportunity_contract_v03.py
python matched_opportunity_contract_v03.py > matched_opportunity_v03_demo.json
sha256sum matched_opportunity_v03_demo.json
```

Local execution on **CPython 3.13.5 / Linux**, 2026-10-26: **18/18 tests passed**. Deterministic demo SHA-256 (LF): `74196ae82435526dfb21cf2a7a50606de5dd1484fb3eb611d504f1e42d41372b`. Tests include rest rate, imagery misdirection, coverage mismatch withholding, zero-action withholding, segmentation invariance, half-open boundaries, duplicate/missing/extra decisions, invalid metadata and annotations. **GitHub CI #40227676669** passed all 18 new tests and the pinned demonstration checksum on **Ubuntu and Windows (Python 3.13)** at code-bearing commit `b02b52f9945b056777ad95766f2b448bb4b9100d`; both job logs were inspected. Independent technical review: **TBD**.

**Deliberately unfavorable comparison:** fictional abstention acts on both imagery opportunities (coverage 1.0, incorrect-action risk 0.5); fictional gate acts on one (coverage 0.5, risk 0.0). Coverage gap **0.5 > 0.05**, so **no gate advantage is reported** (`null` delta). Ungated makes 4 fictional T0 actions over 40 seconds of T0 exposure = **6/minute**. These are invented inputs to test arithmetic, not observations.

## Provenance / failure and limitations

- Additive to `rest_exposure_rate_v02.py` (existing Git blob `1a1540f2469814720ad4b3d8e71b44f611fc1712`). Does not alter the frozen synthetic evaluator, CSV, published stronger cross-platform execution, or checksum-verified real S001R04 annotation evidence.
- A full-looking annotation partition may still conceal a **mislabelled initial T0**. The previously observed EDF+ 30 vs WFDB 29 event discrepancy must be reconciled from the original publisher bytes before real analysis.
- Explicit decisions are **fictional**, not time-synchronized decoder outputs. Real clock alignment, decision opportunity cadence, refractory handling, annotation provenance, threshold calibration, subject-level uncertainty and matched-coverage superiority are **TBD**.
- A zero-action policy has undefined incorrect-action risk; treating it as zero would falsely reward permanent abstention. Unmatched coverage must not yield a risk delta. Both negative controls are executable tests.
- **Next experiment:** lock a subject-disjoint real EEG preprocessing pipeline, verify all T0 annotations and decision opportunity timestamps, freeze calibration-selected policies and matched-coverage tolerance, and score held-out subjects with uncertainty intervals. A separate multi-session dataset is required for drift claims.

**Kill/reframe:** if the gate is no better than simple abstention at comparable imagery coverage, or loses too many useful actions, narrow the claim to an unproven diagnostic. Do not claim clinical/device safety or novel algorithmic invention.

**Four lenses:** Hiring manager—transparent fail-closed engineering; technical reviewer—denominator and decision-grid correctness but no statistical evidence; innovation leader—clear falsification gate; founder—no demonstrated user outcome, safety certification, or commercial value.
