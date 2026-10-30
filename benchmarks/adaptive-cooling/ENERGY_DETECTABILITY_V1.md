# Adaptive Cooling — energy-counter detectability boundary v1 (fictional)

**Date:** 2026-10-30. **Evidence class:** deterministic fictional negative-control test against the *unchanged* `dry_run_integrity.py`. **Stage:** Prototype / Documented R&D. **Physical captures, thermal effect, meter calibration, and energy-efficiency measurements:** TBD.

## Why this matters

The historical dry-run preflight compares the whole-run cumulative energy counter against trapezoidally integrated power with default tolerance `0.5 Wh + 30% × estimated Wh`. It correctly labels any accepted trace `STRUCTURE_ONLY_PROVENANCE_UNVERIFIED`, never physical validation. However, a frozen counter can be indistinguishable from a valid low-energy reading within that absolute tolerance. This is a **measurement detectability limit**, not a newly established physical defect.

For a fictional 600-second run with constant power `P`, zero counter increment, and exact 60-second sampling, estimated energy is `E = P × 600 / 3600 = P / 6 Wh`. The whole-run comparison detects the frozen counter only when `E > 0.5 + 0.30 E`, equivalently `P > 0.5 × 3600 / (600 × 0.70) = 4.2857142857 W`. Equality is accepted. Individual 60-second interval tolerances do not resolve the low-power case.

## Executable fictional controls

Run from `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_energy_detectability_v1.py
```

The four tests exercise the **existing checker**, without changing its historical logic:

| Fictional 600-second trace | Whole-run counter | Expected checker result |
|---|---:|---|
| Constant 1 W | Stuck at 0 Wh | `STRUCTURE_ONLY_PROVENANCE_UNVERIFIED` (not a physical PASS) |
| Constant 5 W | Stuck at 0 Wh | `REJECTED` / `POWER_ENERGY_INCONSISTENCY` |
| Constant 1 W | Increments to 1/6 Wh | `STRUCTURE_ONLY_PROVENANCE_UNVERIFIED` |
| Analytic boundary | N/A | 4.2857142857 W for the stated default settings |

**Assumptions:** constant power, exact 600-second sample span, 60-second cadence, zero counter movement, no meter latency/quantization model, no timestamp or calibration error. A real meter may have different precision, reporting cadence and response; no assertion about actual devices follows.

## Decision and physical acceptance gate

A structural dry-run acceptance **cannot** be treated as evidence that the cumulative energy channel is working, particularly below this envelope. Before selecting instruments or claiming an energy comparison:

1. Record actual whole-system meter identity, resolution, uncertainty, sample interval and response behavior in the existing instrument manifest. Record a separate reference measurement or a documented functional counter check. If unavailable, mark cumulative energy as **TBD / unverified**.
2. Freeze the trial duration, expected power envelope and a *meter-specific* detection/uncertainty criterion **before** looking at device results; do not lower tolerances post hoc to manufacture a pass.
3. Preserve original logger bytes, timestamped CSV, declared electrical boundary, independently pinned hashes, and any disagreement. Run the preexisting origin, capture-chain, timestamp/energy and SCD40 sample-span gates.
4. Only after a genuine >=600-second instrumented dry run, pursue predeclared order-balanced ambient/fan-only/prototype trials with heat-rejection and condensation observations.

**Reframe/kill:** if power/counter resolution cannot distinguish the hypothesized energy effect, do not claim efficiency; increase independent metrology quality or report energy comparison inconclusive. If controlled prototype-vs-fan-only effects are absent, reframe the thermal concept. No comfort, safety, performance, patentability, commercial, or stage-advance claim.

**30–90-second demonstration:** execute the four tests, then show the 1 W stuck counter returning a structural-only status while the 5 W counter is rejected. The distinction is *detectability*, not an actual measurement.

**Four lenses:** hiring manager—transparent negative control; technical reviewer—reproducible tolerance boundary and explicit assumptions; innovation leader—prevents a misleading physical claim; founder—meter quality and controlled physical tests remain cost/feasibility gates.
