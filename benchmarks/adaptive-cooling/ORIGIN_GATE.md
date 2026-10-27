# Adaptive Cooling — explicit synthetic-origin preflight

**Maturity:** Prototype / Documented R&D. **Physical data:** none in this change. **Version:** v0.1, 2026-10-23.

## Failure reproduced

The local pre-bench validator v0.1 could report `BENCH_STRUCTURE_PASS_AUTHENTICITY_UNVERIFIED` on an explicitly **FICTIONAL** 45-row CSV when instrument and geometry fields were populated with plausible declarations. The pass was structural only, but the positive status risked accidental presentation of a demonstration as a physical benchmark. The frozen public raw and instrument templates are unchanged.

## Narrow correction

`fixture_origin_gate.py` rejects bench-mode inputs with explicit `FICTIONAL`, `SYNTHETIC`, `SIMULATED` or `MOCK` markers in the plan, raw notes/run IDs, or instrument manifest. It also rejects missing instrument coverage, required instrument provenance, or declared geometry, and checks exact committed CSV column order. It never authenticates physical origin: **absence of markers is not evidence of a real experiment**. A structural pass must not be used for thermal, energy-efficiency, condensation-safety or comfort claims.

Run the 11 synthetic-only regression tests with `python -B -m unittest -v test_fixture_origin_gate.py` from this directory. For a 60-second reviewer demonstration, show the `test_fictional_raw_rejected`, `test_synthetic_plan_rejected` and `test_unverified_even_when_structure_passes` tests, then inspect their source and the output. The tests execute much faster than 60 seconds.

Example invocation:

```bash
python fixture_origin_gate.py --raw measurements.csv --manifest instrument_manifest.csv --plan run_plan.json --mode bench
```

Exit code 2 means rejected; exit code 0 means **structure-only origin unverified**. This is an extra preflight, **not** a substitute for the full timestamp/energy/uncertainty checks, instrument calibration, genuine ten-minute logging dry run or repeated ambient → fan-only → prototype comparisons.

## Reproducibility and boundaries

- Source: public repo `Vermicare/Haridas-Satheesh`, `benchmarks/adaptive-cooling/raw_data_template.csv` and `instrument_manifest_template.csv`, inspected on `main` commit `775e2398c2d7256b1888398f415eb269ad40c202` (2026-10-23 inspection). No template changes.
- Environment: CPython 3.13.5, Linux, standard library only. CI reruns the tests with a separate GitHub-hosted environment; CI result is TBD until a run is inspected.
- All tests use fictional in-memory/temporary CSVs. No sensor, power meter, calibrated instrument, real data, comfort validation, human participant or cooling performance result.
- Negative result: the original local validator accepted explicitly fictional CSV as **structure-only**, not authenticated. New preflight refuses explicit fictional origin in bench mode.
- Limits: textual markers can be removed; this tool cannot detect fabricated/replayed unmarked data. Instrument metadata are declarations, not authenticated calibration certificates. A complete bench report requires independently documented provenance and physical comparisons.
- Advance: only after a real instrument manifest, fixed geometry, logged dry run and replicated controls with raw data and analysis.
- Reframe: if controlled measurements cannot distinguish prototype benefit from fan-only or energy/condensation constraints erase any advantage.

No release, stage upgrade, patentability claim or real-world performance claim is authorized by this artifact.

## v0.2 — adversarial full-row marker coverage (2026-10-25)

**Reproduced negative controls:** the previous origin-only gate accepted an explicitly `FICTIONAL` marker placed in a raw column other than `notes` or `run_id`; it also accepted an explicitly `MOCK` optional instrument because only the eight required measurement rows were screened. Both inputs received `STRUCTURE_ONLY_ORIGIN_UNVERIFIED`, despite containing overt synthetic markers. The separate numeric/timestamp preflight can reject some malformed values, but the origin-only gate must not silently miss explicit markers.

**Correction:** scan all values of every structurally parsed raw row and all instrument rows for the same four existing marker strings. Keep the required-instrument coverage and provenance checks restricted to the eight required measurements; a legitimate unmarked optional instrument must not cause rejection. Do not change the dry-run mode's documented fictional-fixture allowance.

**Evidence:** two pre-fix negative controls failed as expected, then three focused tests passed on CPython 3.13.5/Linux after correction. Hosted [GitHub Actions #40143976331](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40143976331): **33/33 tests passed on Ubuntu and 33/33 on Windows** (14 origin + 19 dry-run, fictional only); final tested source blob `25378c7160a840e71164f5b8153976364550f38e` and test blob `4092816ad5c051e898593a1e09fc0ba1feac55e1`. The tests are fictional only; a malicious actor can remove markers. This is a narrow evidence-presentation guard, **not** physical sensor authentication, calibrated instrument validation, energy efficiency, safety, comfort, or cooling performance evidence. No maturity advancement.

[Versioned experiment registry](ORIGIN_GATE_V02_REGISTRY.json). **Next physical gate remains Issue #15**: actual instrument inventory, geometry, ≥10-minute original logging capture and repeated ambient/fan-only/prototype trials.
