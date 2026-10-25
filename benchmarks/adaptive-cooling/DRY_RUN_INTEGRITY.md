# Adaptive Cooling — raw logging dry-run integrity preflight (v0.2)

**Evidence class:** synthetic-only software checks; **not** a physical logging session, authenticated instrument record, thermal-performance measurement, or bench validation. Project stage remains **Prototype / Documented R&D**.

## Why this exists

A previously documented fictional negative control had nonzero reported power while the cumulative energy counter remained unchanged. A complete-looking CSV could therefore be mistaken for an internally coherent measurement. This preflight rejects that contradiction and other capture-integrity failures before anyone computes a cooling or efficiency comparison.

## Run against the existing committed raw schema

From the benchmarks/adaptive-cooling directory:

    python -B -m unittest -v test_dry_run_integrity.py
    python dry_run_integrity.py --raw path/to/existing_raw_capture.csv

The script reads the CSV without modifying it. It expects the exact columns of raw_data_template.csv, **one run and one condition per file**, timezone-aware ISO-8601 timestamps, and complete numeric measurements. It rejects missing/extra columns, malformed rows, nonfinite/negative physical quantities, RH outside 0–100%, invalid condition/condensation flags, nonmonotonic timestamps, a run shorter than 600 seconds, and sample gaps over 60 seconds. It also checks that cumulative energy does not decrease and compares the energy-counter change with trapezoidally integrated instantaneous power.

**Provisional consistency tolerances (not performance criteria):** absolute difference ≤0.5 Wh plus 30% of integrated power, maximum timestamp gap 60 s, minimum duration 600 s. These deliberately broad thresholds are for capture troubleshooting, not proof of meter calibration or physical accuracy. Power integration assumes representative sampling; intermittent loads and meter update latency can produce false alarms. Review raw records and meter documentation rather than silently relaxing thresholds after observing a result.

Exit 2 / REJECTED means at least one structural inconsistency; exit 0 / STRUCTURE_ONLY_PROVENANCE_UNVERIFIED means only these limited checks passed. **Neither outcome authenticates sensor origin, validates the measurement geometry, or permits a performance claim.** An invented CSV can pass if it is internally consistent.

## Raw-byte provenance binding (v0.2)

**Observed defect in v0.1:** the preflight reported structural checks but did not identify the exact bytes evaluated. A CSV could be edited after validation while a previous passing JSON report was reused. The report was therefore not independently bound to an input artifact.

**Correction:** v0.2 reads the raw CSV bytes **once**, calculates SHA-256 on that snapshot, and parses that same snapshot. JSON output includes `raw_sha256` and `raw_byte_count`. Pin the digest from the original preserved capture before analysis, then rerun:

    python dry_run_integrity.py --raw path/to/raw.csv --expected-sha256 64_HEX_DIGITS_FROM_CAPTURE_MANIFEST

A missing or malformed pinned digest is not a substitute for original raw capture. If `--expected-sha256` is supplied, an invalid digest yields `INVALID_EXPECTED_SHA256`; changed bytes yield `RAW_SHA256_MISMATCH` and exit 2. Without this option the report still records a digest but **cannot** prove it matches an earlier capture. A changed file after a completed audit can still be detected only by comparing its later digest with the preserved report. This mechanism authenticates **neither** the physical origin nor the recorder clock; an invented file can have a perfectly valid hash.

Five new fictional regression tests cover exact digest, post-pinning edit, malformed digest, uppercase digest and mutation between snapshot acquisition and parsing. Tests are software-only; no cooling equipment was used. Keep the v0.1 CI record in the experiment registry as historical evidence, not a v0.2 result.

## Negative controls and next physical gate

The original fourteen fictional-only tests exercise counter stalling/reset, timestamp order, insufficient duration, gaps, mixed runs/conditions, bad RH, missing or nonfinite values, extra columns, naive timestamps, and negative power. No measurements from an actual prototype or meter are included.

Before using real data, populate the existing instrument manifest with **actual** models, accuracy/uncertainty and check dates; freeze geometry; capture a genuine ≥10-minute timestamped dry run; retain original raw serial/logger output and a SHA-256 manifest; run both this preflight and fixture_origin_gate.py; and inspect failures. Then plan replicated ambient → fan-only → prototype trials, with predeclared metrics and condensation monitoring. Record all failures and exclusions.

**Limitations:** this tool does not verify the energy meter against a reference, distinguish synthetic from genuine data, check sensor synchronization or latency, or assess thermal safety. Do not interpret its synthetic demonstration's 10 Wh arithmetic as a physical energy measurement. Real data, cooling improvement, energy savings, human comfort, external review and release remain **TBD**.

## Finite-input overflow gate (v0.3; 2026-10-25)

**Reproduced defect:** a fictional 11-row, 600-second CSV with finite `power_w=1e308` at every sample and an unchanged energy counter returned `STRUCTURE_ONLY_PROVENANCE_UNVERIFIED` under v0.2. The expression `(a+b)/2` overflowed to `Infinity`; the subsequent comparison `Infinity > Infinity` was false, so the stalled counter escaped the consistency gate. Strict JSON serialization also failed with `ValueError: Out of range float values are not JSON compliant`. This is a software evidence-integrity bug, **not** a plausible cooling measurement.

**Correction:** compute the pairwise average as `a/2+b/2`, multiply by `dt/3600`, and reject any remaining nonfinite derived integral, counter delta or derived tolerance. A nonfinite derived energy is reported as JSON `null` with `NONFINITE_DERIVED_ENERGY`, not silently serialized as Infinity. The structural pass still does **not** establish physical origin.

**Regression evidence:** four new fictional-only adversarial/control tests cover a stalled counter with finite extreme power, a finite internally consistent arithmetic control, a pathological long-interval overflow with JSON-safe rejection, and overflow of a caller-supplied energy tolerance. A local independent reproducer (CPython 3.13.5/Linux) showed three failing cases before correction and four passing cases after correction, repeated twice; the committed regression suite passed **37/37 on Ubuntu and 37/37 on Windows** in [GitHub Actions run #40185598055](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40185598055). Job logs were inspected. Source Git blob: `f9c38f9b5308d16f4e22fac99d1ad5639d30f37e`; committed test Git blob: `1cd4cca06416cae4bcd34eb288398d5f9288a4af`.

**Boundary and next action:** these are numeric stress tests, not instrument readings or evidence of energy savings. The real instrument manifest, authenticated ≥10-minute logging capture, heat-rejection/condensation observations, and repeated ambient → fan-only → prototype comparisons remain **TBD** under [Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15). No maturity advancement, release or comfort claim.
