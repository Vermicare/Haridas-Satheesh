# Retail observable-sales finite-score integrity — v0.9 (2026-10-25)

**Evidence class:** FICTIONAL_TEST_ONLY. **Stage:** Research / Architecture (unchanged).
**Scope:** Numerical integrity of the frozen observable-sales forecasting evaluator, not new forecasting performance or official FreshRetailNet validation.

## Falsifiable failure

A JSONL record can contain 24 individually finite hourly sales and a finite business-hour aggregate, yet the evaluator can still produce invalid nonfinite results:

1. Seven held-out days each have finite absolute error `1e308`. The previous `mae` implementation computed `sum(errors) / 7`, overflowing the intermediate sum to `Infinity`, even though the true mean is finite (`1e308`).
2. The causal training-history substitution averaged two finite same-weekday values using `(a+b)/2`. For `a=b=1e308`, the intermediate addition overflowed, yielding an infinite substituted value.
3. Default Python `json.dumps` permits `Infinity` by default, so the CLI could emit a non-standard, apparently machine-readable report rather than fail closed.

The failure is about **valid-input numerical computation and evidence serialization**, not whether extreme sales are plausible in retail operations.

## Reproduced negative controls

New [four-test fictional regression suite](test_finite_score_integrity_v09.py) checks: finite seven-day MAE, finite same-weekday median, ordinary-input score preservation, and strict JSON output from both the in-memory and SQLite engines on an 84-day fictional dataset.

- **Before fix:** [GitHub Actions #40213211784](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40213211784), commit `d1e4267e33af78ec7fee1930c4261f278b74ac86`. Ubuntu reported two failing assertions and two erroring engine subtests; Windows was cancelled after the corrective commit. This is expected negative evidence, **not** a passing before-fix run.
- **After fix, code-bearing final head:** [GitHub Actions #40213275082](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40213275082), commit `f41d058627e5c0e6e63d4dd5cb3f5625cc2fd635`. **67/67 tests passed on Ubuntu and Windows, Python 3.13**; the fictional demonstration also passed on both.
- Independently reproduced the underlying arithmetic on CPython 3.13.5/Linux: the original sum and midpoint were `inf`; scaled-error summation and half-first midpoint both yielded `1e308`. This isolated check is **not** a full local repository reproduction.

## Correction and invariants

- [`retail_gate.py`](retail_gate.py) keeps the original `sum(errors)/N` path when the sum is finite, preserving ordinary/frozen metric output. Only when the sum overflows does it compute `math.fsum(error/N)`. Invalid individual errors are rejected.
- The corrected same-weekday median keeps its original path when finite; only overflow invokes `a/2 + b/2`.
- Both [in-memory CLI](retail_gate.py) and [SQLite CLI](retail_sqlite.py) now use `json.dumps(..., allow_nan=False)` to reject future nonfinite report values.
- The two engines still share the same evaluator; cross-engine agreement is **not** independent forecasting validation.

## Reproduce

From `benchmarks/retail-demand/observable_baseline/`:

```bash
python -m unittest discover -v
python demo_60s.py
```

Expected for the corrected code-bearing commit: 67 tests and a fictional demonstration on Python 3.13. Run conditions: GitHub Actions `ubuntu-latest` and `windows-latest`; standard library, no downloaded Parquet or private data. OS image build and exact patch versions: **TBD** beyond recorded CI logs. Random seed: not used by this deterministic test.

## Decision and limitations

**Decision:** retain as draft regression hardening; no maturity advancement or release. The new tests close a concrete finite-input/invalid-output defect without changing the frozen ordinary-input forecasting logic.

**Unknown = TBD:** pinned publisher Parquet bytes locally acquired; independently verified source hash; real-data MAE; forecast calibration; stockout-demand recovery; opportunity-ranking lift; intervention outcomes; deployment; commercial value.

**Next evidence-producing experiment:** obtain the exact publisher-pinned train Parquet, verify its SHA-256 locally, execute the documented exporter, run the frozen chronological baselines, and preserve negative results. If source schema cannot map cleanly, document and reframe rather than silently coerce.

## Four-lens review and next-gate acceptance

- **Hiring manager:** executable, public cross-platform regression evidence; no exaggerated real-world results.
- **Technical reviewer:** original finite-input failure, fail-closed output and normal-path compatibility are inspectable; both engines share forecast logic, so cross-engine agreement is not an independent model replication.
- **Innovation leader:** a falsifiable numerical integrity gap was closed, but the stockout-aware hypothesis is still untested on publisher data.
- **Founder:** no verified forecasting lift, realized revenue, customer use, or readiness to deploy; prioritize a real-data experiment over further fictional polishing.

**Next-gate acceptance:** immutable publisher revision and file hash verified locally; exact Python/`pyarrow`/OS versions recorded; converter schema mapped without silent coercion; frozen 42/56/70 chronological folds executed on a predeclared cohort; real-data MAE and baseline deltas retained whether positive or negative. If the pinned file cannot be acquired or its schema differs, document the blocker and reframe rather than claiming benchmark success.
