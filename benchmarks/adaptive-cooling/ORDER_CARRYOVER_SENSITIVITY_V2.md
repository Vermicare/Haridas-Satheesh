# Adaptive Cooling — exhaustive balanced-order carryover sensitivity v2

**Date:** 2026-10-28. **Evidence class:** deterministic fictional software model only. **Physical observations: 0.** No thermal performance, comfort, safety, energy, or prototype validation. **Stage remains Prototype / Documented R&D.**

## Why this changes the experimental design

The [v1 order-confounding experiment](ORDER_CONFOUNDING_V1.md) showed that using all six permutations of ambient, fan-only, and prototype cancels *linear run-order drift* under its simplified assumptions. It also warned that a preceding prototype run can contaminate the next trial. **This experiment quantifies that remaining design risk without choosing a favorable schedule.**

The script enumerates all **6! = 720** ways to arrange the six distinct three-condition blocks. Each schedule is position-balanced. It reuses the [unchanged v1 simulator](order_confounding_v1.py), with a hypothetical one-slot additive carryover following prototype runs, including across block boundaries. No true prototype effect, no noise, 10-minute slots, a global −0.02 °C/min linear drift, and fictional carryover values −0.6, 0, or +0.6 °C are **assumptions, not instrument readings**.

| Hypothetical carryover after prototype | Range of apparent prototype minus fan-only | Schedules with zero bias / 720 |
|---|---:|---:|
| −0.6 °C (cooling of next trial) | 0.0 to +0.4 °C | 48 |
| 0 °C | 0.0 °C | 720 |
| +0.6 °C (warming of next trial) | −0.4 to 0.0 °C | 48 |

The ambient comparator has the same *distribution* of biases across the 720 orders, although the two comparator biases differ for a given individual schedule. For the already published seed 20261027 schedule, the **fictional** +0.6 °C carryover produces −0.1 °C apparent prototype-versus-fan-only and −0.2 °C versus ambient, despite **zero true treatment effect**.

**Decision:** complete position balance is insufficient to guarantee unbiased cooling comparisons if carryover is present. Do **not** pick one of the 48 apparently zero-bias schedules based on this assumed model. Freeze an operational schedule before outcomes; establish stabilization/washout or separate sessions from observed physical return-to-baseline; inspect run-order residuals and record deviations. If carryover is not controlled, report a confounded contrast rather than a clean causal prototype advantage.

## Reproduce (Python standard library)

From `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_order_carryover_sensitivity_v2.py
python -B order_carryover_sensitivity_v2.py > ORDER_CARRYOVER_SENSITIVITY_V2_RESULT.json
```

The seven tests check all 720 permutations, linear-drift cancellation with no carryover, warming/cooling sign symmetry, a nonzero seeded-schedule bias, invalid numeric inputs and strict JSON serialization. Source/test/output SHA-256 and exact execution conditions are in the [registry](ORDER_CARRYOVER_SENSITIVITY_V2_REGISTRY.json). The local prepublication check used a compatible reimplementation of the v1 simulator; **hosted workflow tests against the exact committed v1 source are the authoritative cross-platform check and remain TBD until the new run completes.**

## Limitations and next evidence gate

This is a deterministic stress test of an intentionally simplistic, immediate one-slot additive model. Real thermal inertia can be nonlinear, multi-slot, state-dependent, affected by humidity/heat rejection and subject to meter latency and sensor synchronization. The 0.6 °C scenario is not an estimate of actual carryover; the frequency of biased schedules is not a real-world probability. Nothing here establishes which order to choose or a minimum washout duration.

**Next physical experiment remains unchanged:** complete [Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15) with a genuine ≥600-second timestamped instrument/logger dry run, raw-byte provenance, actual instrument uncertainties and fixed geometry. Only then run predeclared, repeated ambient/fan-only/prototype comparisons with carryover checks. All physical measurements and performance results are **TBD**.
