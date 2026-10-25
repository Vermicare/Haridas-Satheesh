# Retail v1.0 — forecast-horizon-bounded cohort eligibility (2026-10-26)

**Stage: Research / Architecture — unchanged. Evidence class: fictional software correctness only.** No publisher Parquet bytes were read and no real retail forecast, stockout-recovery, revenue or decision-uplift claim is made.

## Hypothesis and defect

The frozen benchmark evaluates origins 42, 56 and 70 with seven-day forecasts. Its latest required observation is **day 76** (77 daily records indexed from day 0). Both the in-memory and SQLite cohort selectors previously checked calendar continuity across **every supplied row**, including rows after day 76. A missing day 81 incorrectly rejected a cohort whose entire scored 77-day interval was intact. This makes cohort eligibility depend on irrelevant post-horizon data, contrary to the declared benchmark rule.

## Preserved negative evidence

The new [four regression tests](test_horizon_bounded_selection_v10.py) were committed before modifying either engine, at `b22a9fa0304b9ba8ab41bec4f1d4239291a40794`. [Before-fix CI #40236967445](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40236967445) **failed**: the Ubuntu job reported **two expected errors** (post-horizon gap rejection and incorrect cohort invalidation). The Windows job was cancelled after logging the same two test errors; it is **not** counted as a complete Windows before-fix run.

The first repair limited continuity checks to the first 77 records **but accidentally returned a truncated list**, breaking an existing test that intentionally mutates day 80 to establish future-stockout invariance. [Intermediate CI #40237039496](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40237039496) failed on both operating systems with `IndexError`. This regression was preserved and corrected rather than hidden.

## Final correction and verification

Both engines now check **only the first 77 dates** for eligibility, while preserving the original full selected-series return value. The selection key remains based on the first 42 training days. Gaps within the scored horizon still fail closed; gaps after day 76 cannot disqualify or switch the cohort. Scored folds remain unchanged by post-horizon observations.

- Final code-bearing commit: `c1e307ae9558e11c83434509d6e3465c072a3036`.
- [Final CI #40237113875](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40237113875): **71/71 tests passed on Ubuntu and 71/71 on Windows**, Python 3.13 matrix; both job logs inspected.
- New tests: post-horizon gap invariance, no future-based cohort switch, inside-horizon gap rejection, and post-horizon sales invariance.
- Previous benchmark tests and fictional demo also passed. No change to the forecast definitions, scores, source-provenance boundary or real-data status.
- Raw source dataset: **TBD**. Publisher-file SHA-256: **TBD**. Real-data MAE and decision metrics: **TBD**.

## Reproduce / 60-second demo

From `benchmarks/retail-demand/observable_baseline`:

```sh
python -m unittest -v test_horizon_bounded_selection_v10.py
python -m unittest discover -v
python demo_60s.py
```

The first command demonstrates the four fictional negative/positive controls; the second checks both benchmark engines and the full suite. The historical red CI links are preserved as before/after evidence.

## Decision and next experiment

**Decision:** retain the narrow fix on draft PR #9; do not merge without review. Next acquire a publisher-pinned, license-checked FreshRetailNet-50K Parquet snapshot; hash the actual bytes; validate the documented 16-hour stock-status rule against the publisher schema; and run a chronological, held-out, leakage-safe baseline. Do not infer latent demand from censored sales as if it were observed truth.

**Advance:** only reproducible public-data forecast and decision comparisons justify a new evidence claim. **Reframe:** if stockout-aware correction cannot outperform a simple seasonal-naive baseline or stockout observability is insufficient.

**Four lenses:** hiring manager—visible before/after reproducibility; technical reviewer—explicit horizon boundary and API regression; innovation leader—negative CI preserved and fixed; founder—no fabricated data, performance, customer or patentability claim.
