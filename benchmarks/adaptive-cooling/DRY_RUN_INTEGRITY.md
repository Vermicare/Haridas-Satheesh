# Adaptive Cooling — raw logging dry-run integrity preflight (v0.1)

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

## Negative controls and next physical gate

Fourteen fictional-only tests exercise counter stalling/reset, timestamp order, insufficient duration, gaps, mixed runs/conditions, bad RH, missing or nonfinite values, extra columns, naive timestamps, and negative power. No measurements from an actual prototype or meter are included.

Before using real data, populate the existing instrument manifest with **actual** models, accuracy/uncertainty and check dates; freeze geometry; capture a genuine ≥10-minute timestamped dry run; retain original raw serial/logger output and a SHA-256 manifest; run both this preflight and fixture_origin_gate.py; and inspect failures. Then plan replicated ambient → fan-only → prototype trials, with predeclared metrics and condensation monitoring. Record all failures and exclusions.

**Limitations:** this tool does not verify the energy meter against a reference, distinguish synthetic from genuine data, check sensor synchronization or latency, or assess thermal safety. Do not interpret its synthetic demonstration's 10 Wh arithmetic as a physical energy measurement. Real data, cooling improvement, energy savings, human comfort, external review and release remain **TBD**.
