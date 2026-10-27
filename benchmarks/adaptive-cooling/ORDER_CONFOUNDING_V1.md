# Adaptive Cooling — order-confounding negative control v1

**Date:** 2026-10-27. **Evidence class:** deterministic fictional software experiment. **Not** physical instrument readings, cooling efficacy, comfort, safety, or energy-efficiency evidence. **Maturity unchanged:** Prototype / Documented R&D.

## Decision-changing design risk

A repeated **ambient → fan-only → prototype** sequence can confound treatment with elapsed time. If ambient conditions drift systematically, the final prototype condition may look better even when it has no causal effect. NIST warns that predictors systematically changing with run order can make process drift indistinguishable from a treatment effect; its engineering guidance recommends randomization and blocking.

Primary methods:
- [NIST: run-order residuals and drift](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd443.htm)
- [NIST: randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)

## Reproduce

From `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_order_confounding_v1.py
python -B order_confounding_v1.py > ORDER_CONFOUNDING_V1_RESULT.json
```

Python standard library only. Exact source/test hashes and local run conditions are in [registry](ORDER_CONFOUNDING_V1_REGISTRY.json); output in [result](ORDER_CONFOUNDING_V1_RESULT.json). **7/7 fictional-only tests passed locally.** Hosted CI result: TBD until executed and checked.

## Fictional negative control

A deliberately simplified model assumes zero true treatment effect, a linear background decline of **−0.02 °C/min**, 10-minute slots, six three-condition blocks, no noise and no carryover. These are **invented assumptions**, not measured temperatures.

| Six-block order | Simulated prototype minus ambient | Interpretation |
|---|---:|---|
| Fixed ambient → fan-only → prototype | **−0.400 °C** | False apparent prototype advantage under zero treatment effect |
| All six permutations, shuffled with seed 20261027 | **0.000 °C** | Linear position drift cancels under this simplified model |

Every condition occurs twice in every slot position in the balanced schedule. The test also verifies that a hypothetical −0.6 °C true treatment effect is recovered under this simplified linear model.

**Critical limitation:** balancing does not automatically eliminate carryover. An adversarial regression introduces a residual effect from the previous prototype run and shows that bias can remain. Nonlinear drift, thermal storage, condensation, heat rejection, meter lag, stabilization time and autocorrelation are not solved by this demonstration.

## Physical protocol consequence

1. Complete [physical evidence Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15) first: actual instrument inventory, uncertainty and fixed geometry, then genuine ≥600-second raw logger dry run with replayable conversion. All physical measurements remain **TBD**.
2. Before collecting comparative data, freeze a blocked/balanced order or explicitly justified alternative, its seed and operational constraints. Preserve every trial, including failures and excluded periods.
3. Establish and document stabilization/washout from observed return-to-baseline criteria, not an invented universal duration. If carryover cannot be controlled, separate sessions or explicitly model it; do not infer clean causal effects.
4. Measure concurrent ambient and target temperatures, humidity, airflow, surface temperature, total electrical input, stored/recharge energy, heat rejection, condensation and clock/timestamp integrity. Predeclare estimand, minimum meaningful difference and uncertainty handling before viewing results.
5. Plot outcome residuals against run order and evaluate a fan-only comparison. Do not select a favorable run order after seeing outcomes.

**Decision:** no maturity advance or performance claim. Highest-value next step remains a genuine instrumented logging dry run, then a preregistered order-balanced comparison with carryover checks.
