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

## Next evidence gate

The blank raw-data and instrument-manifest schemas are already committed. Do not create duplicate templates.

Before collecting benchmark evidence:

1. Populate the instrument manifest with the actual instrument model/identifier, stated accuracy, calibration or check status, and the date of the check where known. Leave unknown fields blank/TBD.
2. Freeze and document the measurement geometry and sensor positions so ambient, fan-only and prototype conditions are comparable.
3. Run a clearly labelled logging dry run using the committed raw-data schema. A dry run validates capture only and is **not** benchmark evidence.
4. Validate timestamp ordering, units, run IDs, missing-value handling and condition labels before any derived calculation.
5. Only after the logging path passes, collect repeated ambient → fan-only → prototype trials under comparable starting conditions and preserve every raw run, including unfavorable results.

The first evidence-bearing milestone is a reproducible bench package containing populated provenance, repeated raw observations and an analysis artifact derived from those observations. Until then, measured results remain **TBD** and the project remains **Prototype / Documented R&D**.

## Synthetic-fixture origin preflight (draft research contribution)

[Explicit synthetic-origin gate](ORIGIN_GATE.md) checks the committed CSV headers and rejects inputs **marked fictional/synthetic** from bench-mode structural acceptance. This is not device authentication, physical logging, instrument calibration, thermal-performance validation, or evidence of energy savings. Run a real logging dry run and controlled comparisons before performance claims.

## Dry-run timestamp and energy consistency preflight (draft)

[Dry-run integrity contract](DRY_RUN_INTEGRITY.md) adds a **fictional-test-only** check of timestamp ordering, minimum capture duration, sampling gaps, fixed run/condition identity, numerical units/ranges and consistency between logged power and the cumulative energy counter. [Executable tests](test_dry_run_integrity.py) and [versioned experiment registry](DRY_RUN_EXPERIMENT_REGISTRY.json) document the limits and negative controls. This software is preparation for a **genuine** instrumented logging dry run; no physical data have been captured or authenticated. Passing a consistency check does **not** demonstrate thermal benefit, energy efficiency or safety. Keep all real metrics TBD until repeated controlled measurements are independently inspectable.

## Measurement endpoint and standards decision (2026-10-24)

The physical bench endpoint is **instrumented local environmental change**, not perceived comfort, clinical benefit, standards compliance, or room-AC energy superiority. Temperature alone cannot support a comfort claim: the [ASHRAE Standard 55-2023 official overview](https://www.ashrae.org/technical-resources/bookstore/standard-55-thermal-environmental-conditions-for-human-occupancy) identifies temperature, thermal radiation, humidity, air speed, clothing and activity as interacting factors. The current single surface-temperature field is **not** a complete mean-radiant-temperature measurement. A later human-comfort study would require its own predeclared protocol and appropriate participant protections; it must not be inferred from the engineering CSV.

For instrument selection, consult the published [ISO 7726:2025 official scope](https://www.iso.org/standard/78238.html), which concerns instrument characteristics and methods for measuring thermal-environment physical quantities. It supersedes ISO 7726:1998; this project has **not** purchased, implemented, or certified compliance with the full standard. The immediate decision is to document actual instrument uncertainties, locations and measurement methods before the physical dry run. Do not invent tolerances or assert conformance from the abstract.

**Decision:** retain separate gates: (1) authenticated, hashed logging dry run; (2) repeated ambient/fan/prototype physical comparison with uncertainty and heat-rejection accounting; (3) only if justified, a separately designed thermal-comfort evaluation. All real outcomes remain TBD.
