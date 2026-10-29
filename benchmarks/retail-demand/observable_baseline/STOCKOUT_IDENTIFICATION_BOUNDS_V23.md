# Retail v2.3 — sharp identification bounds under unobserved stockout demand

**Date:** 2026-10-29. **Status:** additive fictional mathematical diagnostic; **no new publisher-data evaluation**. **Maturity:** Research / Architecture, unchanged. **Parent:** [draft PR #19](https://github.com/Vermicare/Haridas-Satheesh/pull/19). **External actions:** zero.

## Why this experiment matters

The prior [v2.2 strongest-comparator analysis](FRESHRETAIL_LT_V22_EXPLORATORY_STRONGEST_COMPARATOR.md) found a small descriptive advantage for weekday median over causal stockout history on **1,766 observed in-stock days**, but its paired store interval crossed zero. **1,818 of 3,584 selected evaluation days were stockout-censored**. In-stock error is not the full-period error on *latent demand*. The true demand on censored days is not observed; filling it with sales would fabricate a target.

This v2.3 diagnostic asks a different, precisely limited question: **given two fixed forecasts on the same days and no knowledge of censored demand beyond nonnegativity (or an explicitly hypothetical global cap), what range of full-period paired mean-absolute-error differences is logically possible?** It does not estimate missing demand, select a winning model or provide a confidence interval.

## Derivation / exact estimand

Let forecast A be `a >= 0`, forecast B be `b >= 0`, and unobserved demand be `y >= 0` on a censored day. Define the paired absolute-error difference `d(y)=|a-y|-|b-y|`. Negative values favor A.

`d(y)` is continuous and piecewise linear, with possible kinks only at `a` and `b`. Therefore, on a hypothetical `0 <= y <= cap`, its exact minimum and maximum occur among `{0, cap, a, b}` after removing values outside the interval. Without a cap, `d(y)` becomes constant for `y >= max(a,b)`, so the extrema occur among `{0,a,b}`. Thus **the paired difference has finite sharp bounds even though each model's individual absolute error has no finite upper bound** when demand is unbounded. For observed days, the difference is exactly computed using the observed outcome.

Sum all per-day minima and maxima and divide by the **same full-period day count**. This yields a *sharp logical identification interval* if each unknown demand may vary independently within the stated domain. It is **not** a bootstrap confidence interval, causal effect, uncertainty about the forecasts, or a guarantee that any particular demand scenario occurred. Additional temporal/inventory constraints could narrow it, but are not assumed.

## Executable negative control (fictional, not publisher data)

[Executable with embedded 12-test contract suite](stockout_identification_bounds_v23.py) accepts strict JSON with `schema`, `cap` (null for no cap), and `rows` of opaque unique keys, nonnegative forecasts `a` and `b`, `observed` boolean and `y` **only when observed**. It rejects duplicate keys, NaN, infinities, impossible caps and any supplied censored outcome. It emits aggregate counts and bounds only, never keys, row-level forecasts or outcomes.

A deliberately fictional three-day example has one observed day (`a=1,b=2,y=1`) and two censored days (`a=1,b=2,y=unknown`). Observed-only paired error difference is **-1** (A appears better); full-period difference can be **[-1, +1/3]**, allowing either model to win depending on unknown outcomes. The program must report **undetermined**, not infer a lost-demand advantage.

Reproduce from this directory, Python 3.13 standard library only:

```sh
python -B stockout_identification_bounds_v23.py selftest
python -B stockout_identification_bounds_v23.py score /private/fictional_input.json /private/NEW_aggregate.json
```

The second command requires a deliberately prepared input file and refuses to overwrite its output. Use only public/fictional data; never commit private rows or private input digests. The [cross-platform fictional workflow](../../../.github/workflows/retail-stockout-bounds-v23.yml) runs the embedded tests and a disposable aggregate-only CLI example without downloading publisher labels.

## Provenance, limits, and decision

The local development prototype on **CPython 3.13.5/Linux** passed **12/12 embedded tests** and a separate seeded property probe covering 10,000 random forecast/cap cases and 21 candidate demand points each (**210,000 inequality checks**). The published source has minor nonsemantic cleanup; **hosted verification of the exact committed bytes must be inspected separately before declaring cross-platform PASS**. The [machine-readable registry](STOCKOUT_IDENTIFICATION_BOUNDS_V23_REGISTRY.json) records the committed source and workflow Git blobs, unknowns and execution scope. The exact source code was not used to score the public 2025 data during this experiment.

**Decision:** no stage advancement, no change to v2.1's preregistered in-stock PASS or v2.2's exploratory strongest-comparator INCONCLUSIVE result. Next integrate this diagnostic with the already-frozen 2025 forecast pairs **without using censored outcomes**, preserving model identities and full-day denominators; then pursue an independent, genuinely unseen cohort with measured inventory decision value. Reframe any claim of latent-demand superiority if identification bounds cross zero or if strong assumptions are required to make them exclude zero.

**Four lenses:** hiring manager — executable evidence discipline; technical reviewer — sharp partial-identification derivation and explicit assumptions; innovation leader — established missing-data logic, **no novelty or patentability claim**; founder — no revenue, latent-demand truth, pilot or customer benefit measured. No employer or personal data.
