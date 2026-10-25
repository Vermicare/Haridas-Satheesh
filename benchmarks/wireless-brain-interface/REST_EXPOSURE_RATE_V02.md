# WBI — Sample-normalized rest exposure contract v0.2 (2026-10-25)

**Evidence class:** fictional timestamp arithmetic and annotation-integrity tests only. **Not** real EEG waveform decoding, measured false-action rates, patient/device safety, clinical validation, or evidence of gate superiority. Public stage: **Research / Simulation**, unchanged.

## Decision-changing correction

The prior [rest-aware event evaluator](REST_AWARE_ACTION_DENOMINATOR_V01.md) reports false actions **per T0 event**, not per minute. Event counts depend on how a recording is segmented. A long rest interval split into two shorter T0 intervals can change the event denominator without changing actual idle exposure. Do not treat that metric as a physical false-action rate.

The additive [sample-time implementation](rest_exposure_rate_v02.py) instead accepts a declared integer sample rate, recording length, a full ordered partition of half-open T0/T1/T2 annotation intervals, and independent action timestamps for each policy. It reports rest-action counts divided by **actual T0 sample exposure** in minutes. Exact integer rate numerator/denominator are preserved alongside the rounded display value. A rest interval split into adjacent rest intervals does **not** change the result. Actions at a segment boundary belong to the interval starting at that sample.

## Reproduction and observed fictional results

```sh
cd benchmarks/wireless-brain-interface
python -m unittest -v test_rest_exposure_rate_v02.py
python rest_exposure_rate_v02.py > rest_exposure_v02_demo.json
sha256sum rest_exposure_v02_demo.json
```

**Local preparation:** CPython 3.13.5/Linux, 2026-10-25, 17/17 unit tests passed. Fictional demo SHA-256: `120229c77704bc4c23229f932513176d15f38f1153724319f34f63c1299aaae2`. Fictional 100 Hz / 6000-sample recording, 4000 T0 samples (40 seconds): ungated **3** rest actions → **4.5 per minute**, confidence abstention **0**, drift gate **0**. These deliberately constructed timestamps do not demonstrate a real safety advantage. Repository CI result: **TBD until final-head workflow execution and independent review**.

Adversarial controls: initial/final annotation truncation, gaps, overlaps, unsorted/zero-length intervals, absent rest or imagery exposure, invalid recording metadata, invalid/duplicate/out-of-range action timestamps, invalid policy/direction, exact half-open boundaries, segmentation invariance, and deterministic JSON without real-data claims.

## Critical limitations and next experiment

- **Annotation correctness is not proven.** Relabeling a missing T0 interval as imagery can create a complete-looking partition; publisher provenance, source checksum and independent annotation reconciliation remain mandatory. The previously observed publisher companion missing the initial T0 is not repaired by this module.
- The demonstration emits **one action timestamp per fictional decision**; real continuous-time detector logic, refractory periods, episode grouping, action deduplication, latency, and synchronized clock drift are unimplemented. Real rates are **TBD**.
- Integer sample rate is currently required; any dataset with non-integer frequency needs an explicit rational-time adaptation rather than rounding.
- This is a standalone additive preflight, **not** a modification to the frozen [synthetic evaluator](SYNTHETIC_EVALUATOR.md), its independently reproduced CSV, or real EDF annotation findings.
- For actual held-out EEG, freeze sample/time alignment and full T0 exposure; train only on disjoint training subjects, select thresholds on calibration subjects, then compare policies at **matched imagery coverage**, with subject-level uncertainty and rest false actions per minute. Use a separate multi-session dataset before discussing drift.

**Advance gate:** reproducible real-data held-out decoding and policy comparison, not fictional arithmetic. **Reframe/kill gate:** no improvement beyond confidence abstention at matched coverage or unacceptable useful-action loss.

**Four-lens review:** Hiring—clear numerical denominator; technical—boundary and provenance controls; innovation—testable falsification gate; founder—no user benefit or product validation established. No personal, employer, collaborator or proprietary data.
