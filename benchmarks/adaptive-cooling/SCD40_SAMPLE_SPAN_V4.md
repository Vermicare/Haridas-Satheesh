# SCD40 sample-span boundary negative control v0.4 — October 30, 2026

**Evidence class:** fictional software-only test. **Adaptive Cooling stage:** Prototype / Documented R&D; **no advancement**. No Raspberry Pi or SCD40 was connected; no actual ten-minute period elapsed; no temperature, humidity, energy, cooling, calibration or safety result is asserted.

## Reproduced failure mode

The existing v1 SCD40 logger and independent v2 verifier compute a 600-second quality flag using *logger elapsed time*, a maximum 60-second intersample gap and first/last sample margins of up to 60 seconds. Those conditions do not guarantee ten minutes of actual sensor-sample coverage.

A deterministic injected **fictional** sensor with valid sample values only from elapsed second 60 through 540 produced **97 samples**, 600 seconds of simulated logger elapsed time, but only **480 seconds between first and last sample**. The **unchanged v1 logger** reported `capture_quality_gate_passed=true`, and the **unchanged v2 verifier** independently recomputed `recomputed_capture_quality_gate_passed=true`. Both remain correct against their original, weaker contract; neither attests physical provenance.

Source blobs independently checked against published research branch with `git hash-object`:
- v1 logger: `820b686da1e2541f8d8d1654f7cda2d7fed8b4ae`.
- v2 verifier: `2021b7b23c3a6a05cc5565a75969cbef8509715b`.

Fictional negative-control raw JSONL SHA-256: `d4828479a9bf3e87ce9622d0da0c76f40edd9e78ed46baa48b6eb26e5257c617` (only reproducible with the exact frozen fixture). The injected UTC clock advances with simulated monotonic time; this still does not establish a real clock or sensor.

## Supplemental v0.4 decision guard

[`scd40_sample_span_gate_v4.py`](scd40_sample_span_gate_v4.py) invokes the existing pinned-hash v2 verifier, checks the same raw-byte digest again, and **requires manual review** when sample span is less than `max(600, requested_duration) - max(10, 2*poll_interval)` seconds. This is a **provisional engineering review tolerance**, not an SCD40 manufacturer limit, an acceptance standard, or a claim that exact timing is attainable for every configuration. The fictional 480-second case is `REVIEW_REQUIRED` with a 590-second provisional minimum; a separate fictional 590-second span is `SAMPLE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED`. Neither status authenticates physical origin.

This is deliberately a supplemental guard: do not rewrite the historical v1/v2 records or retroactively reinterpret their original quality flags. For a future genuine capture, run v2, the independent [v3 clock diagnostic](SCD40_CLOCK_CONCORDANCE_V3.md), and v0.4 using a SHA-256 pinned before independent review. Investigate any review flag rather than editing raw observations to force success.

## Reproduction (fictional only)

From `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_scd40_sample_span_gate_v4.py
python -B scd40_sample_span_gate_v4.py PRIVATE_CAPTURE.jsonl --expected-sha256 <independently-pre-pinned-sha256>
```

**Local verification:** CPython 3.13.5, Linux, 2026-10-30: **4/4 new fictional regression tests passed**. Separate source-blob reconstruction and the full 7-test local negative-control suite also passed. **Hosted cross-platform verification:** [GitHub Actions #40968518413](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40968518413) at code/workflow head `0643766943fa5a7eb63ec09ba39dce1167817b32` completed successfully on Ubuntu and Windows. Both job logs were inspected: **131/131 fictional tests passed on each OS**, including all four new v0.4 tests, and the preexisting canonical-LF fictional carryover digest matched. No physical hardware was used. See [registry](SCD40_SAMPLE_SPAN_V4_REGISTRY.json) for exact known/unknown boundaries.

**30–90 second demonstration:** run the first command and show the test in which v2 accepts the 600-second logger receipt while v0.4 flags 480 seconds of sensor-sample coverage. Then show the normal fictional span control and byte-tamper rejection.

## Decision

The next physical gate remains an independently inspectable **genuine** Raspberry Pi/SCD40 >=600-second raw logging session, actual instrument manifest and wiring review, pre-pinned raw SHA-256, independent timestamp checks and a separate temperature/RH reference. Only then preregister repeated ambient/fan-only/prototype trials with heat rejection, energy and uncertainty. **No thermal performance or project maturity claim.**

**Kill/reframe:** if the logger cannot establish near-complete sample coverage, preserve the failed capture, diagnose startup, cadence and dropout, and repeat rather than counting host runtime as continuous sensor observation. The sample-span tolerance must be frozen or justified before real observations, not tuned after seeing a run.

## Four-lens review

**Hiring manager:** demonstrates a reproducible defect and bounded correction, not a finished thermal product. **Technical reviewer:** exact historical source blobs, adversarial control and hosted test logs are inspectable; the provisional 10-second tolerance needs review before real use. **Innovation leader:** separates measurement-window integrity from sensor/thermal claims. **Founder:** a clean software gate cannot substitute for actual instrument provenance, economics, power, heat rejection or a controlled fan-only comparison.
