# SCD40 raw-capture receipt verification v2 — structural integrity only

**2026-10-29.** This is an independent, standard-library verifier for the [v1 Raspberry Pi SCD40 JSONL logger](scd40_dry_run_capture_v1.py). It is **not** a sensor-origin authenticator, a calibration certificate, a temperature-reference comparison or evidence of cooling effectiveness.

## Evidence-producing finding

A logger's terminal capture_quality_gate_passed field is a claim. The independent verifier recomputes it from **the entire raw record sequence** rather than trusting that field. It rejects tampered raw bytes against an independently pre-pinned SHA-256; missing, duplicated or out-of-order samples; forged completion counts, durations or maximum gaps; invalid timestamps; interrupted or truncated streams; out-of-range sensor values; duplicate JSON keys; and unsupported physical-authenticity assertions.

A complete but zero-sample file can be **structurally valid** while the 600-second sample-quality gate is **false**. The verifier reports those conditions separately. A fictional 600-second stream with fabricated sensor values can still pass structural verification: **byte integrity is not hardware provenance**.

## Reproduce without hardware

From benchmarks/adaptive-cooling:

~~~bash
python -B -m unittest -v test_scd40_capture_verify_v2.py
~~~

The 19 new fictional tests include a direct integration test that invokes the unchanged v1 logger with an injected fake sensor and a simulated monotonic clock. This generates no real observations and consumes no actual ten-minute interval.

**Independent hosted execution:** [GitHub Actions run #40782430636](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40782430636), code-bearing head b1ff360f6f889e4a1bbe51fa69c85c0d31e778e4, completed successfully on Ubuntu and Windows. Both job logs were inspected; the full cooling suite passed **120/120 tests on each system** (including all 19 new tests). Exact code/test blob IDs, workflow, job IDs and unknowns are in [the registry](SCD40_CAPTURE_VERIFY_V2_REGISTRY.json). No hardware was connected in hosted tests.

### 30–90 second demonstration

Run the test command above and point to three cases: test_integration_with_actual_logger_mock_only passes a fictional v1 logger receipt; test_tamper_after_hash rejects a byte modification against the earlier digest; and test_false_early_dropout_pass rejects a forged positive completion. The distinction between record_structure_valid and recomputed_capture_quality_gate_passed is the central demonstration.

## Independently verify an actual private file later

After a genuine run of the [v1 logger](SCD40_PHYSICAL_DRY_RUN_V1.md), independently preserve the logger's **original raw JSONL bytes** and its SHA-256 in a separate private instrument manifest **before** handing the file to a second verifier. The following command is illustrative; the digest is **TBD** until a real file exists:

~~~bash
python -B scd40_capture_verify_v2.py "$HOME/cooling-private/scd40_run_001.jsonl" \
  --expected-sha256 "<64-character-pre-pinned-lowercase-hex>"
~~~

A verification pass proves only that the supplied file matches the supplied digest and that its **declared** internal record structure and duration-quality flag are consistent. If the digest was computed after modification, or the clock/sensor data were fabricated, the verifier cannot detect that. It does not independently authenticate the SCD40, actual wall-clock duration, calibration, measurement accuracy or cooling. Do not upload raw files containing private location or hardware identifiers. Preserve failures, original bytes, and real instrument uncertainties.

## Decision / next gate

**Stage remains Prototype / Documented R&D.** No physical executions, thermal measurements or comparator trials were performed. This verifier removes a software-only receipt-consistency gap but **does not satisfy Issue #15's physical evidence gate**. Next: a real Raspberry Pi + SCD40 >=600-second dry run with independently checked wiring and source hash, then independent ambient/target temperature and humidity, airflow, surface and electrical-energy instruments before balanced ambient/fan-only/prototype comparisons. Reframe the cooling thesis if fan-only, heat rejection or measurement uncertainty erases a repeatable benefit.
