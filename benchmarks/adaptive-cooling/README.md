# Adaptive Personal Cooling — Evidence Plan

**Project stage:** Prototype / Documented R&D  
**Evidence status:** Benchmark design defined; results are TBD.

## Research question

Does the localized cooling prototype create a repeatable measurable thermal-zone benefit relative to ambient and fan-only controls, and what energy input, humidity behavior and persistence accompany that benefit?

This is an engineering benchmark, not a medical or physiological validation.

## Comparison conditions

1. Ambient control.
2. Fan-only airflow baseline.
3. Localized cooling prototype.

Use the same measurement geometry for every condition and record starting ambient conditions.

## Evidence registry

| Measure | Unit | Result |
|---|---:|---|
| Ambient temperature | °C | TBD |
| Ambient relative humidity | %RH | TBD |
| Target-zone temperature | °C | TBD |
| Target-zone relative humidity | %RH | TBD |
| Air velocity at target point | m/s | TBD |
| Representative surface temperature | °C | TBD |
| Input power | W | TBD |
| Energy per trial | Wh | TBD |
| Active duration | min | TBD |
| Post-run persistence | min | TBD |
| Condensation observed | yes/no + notes | TBD |

## Reproducibility requirements

Record:
- test-space and target-zone geometry,
- fixed sensor positions,
- prototype configuration,
- instrument models and stated accuracy/calibration status,
- starting conditions,
- stabilization period,
- sampling interval,
- timestamped raw observations,
- interruptions or configuration changes,
- repeated trials under comparable conditions.

Keep raw observations separate from derived outputs. Do not omit unfavorable runs without recording why they were excluded.

## Derived comparisons

Calculate from recorded observations:
- target-zone temperature delta relative to concurrent ambient,
- target-zone humidity delta,
- prototype delta relative to fan-only baseline,
- energy per trial,
- post-run persistence,
- dew-point margin when the required surface and humidity measurements exist.

Record the exact calculation method in the analysis artifact.

## Suggested raw-data schema

```text
run_id,timestamp,condition,ambient_temp_c,ambient_rh_pct,target_temp_c,target_rh_pct,
air_velocity_m_s,surface_temp_c,power_w,energy_wh,condensation_flag,notes
```

## Evidence package

A reviewable bench package should contain:
- setup diagram or photo with measurement points,
- instrument manifest,
- raw CSV observations,
- run/configuration manifest,
- analysis script or notebook,
- generated benchmark table,
- failure/learning log,
- limitations.

Unknown values remain blank/TBD.

## Advance criterion

Remain at **Prototype / Documented R&D** until repeated instrumented trials show a localized thermal effect relative to both ambient and fan-only controls, with energy use, humidity behavior and persistence reported.

Numerical pass thresholds must be declared before evaluating the final benchmark rather than chosen after seeing results.

## Kill / reframe criteria

Simplify or reframe if repeated evidence shows that fan-only airflow explains essentially all benefit, humidity or condensation dominates the design, heat rejection or energy demand erases the localized advantage, persistence is impractically short, or added complexity produces no measurable gain.

## Next artifact

Create the instrument manifest and blank CSV run template, then validate that the logging and analysis path works before collecting benchmark evidence.
