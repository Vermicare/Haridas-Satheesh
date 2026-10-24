# BH1750 + SCD40 capture preflight

**Maturity: Prototype / Hardware Architecture. No physical measurements are provided.**

This Python standard-library preflight rejects obviously incomplete or mislabeled ESP32-S3 environmental sensor logs. It does **not** establish sensor identity, authenticity, accuracy, reliability, or successful physical acquisition. Even a fabricated CSV dishonestly declared as physical can pass. Every successful structural report is labeled STRUCTURAL_PASS_PROVENANCE_UNVERIFIED.

## Reproduce

Run from this directory:

    python -m unittest -v test_capture_preflight.py
    python capture_preflight.py manifest.json samples.csv > preflight.json

The second command requires independently acquired files. Exit code 0 indicates only structural acceptance; exit code 2 indicates rejection. All unit-test readings are fabricated, including the test with a misleading physical-origin declaration. There is deliberately no purported real-world example.

## Manifest contract v1

Required JSON keys:
- schema_version = iot-capture-preflight-v1
- capture_origin = physical or synthetic (synthetic always rejected as physical evidence)
- device_id, boot_id, firmware_sha256 (64 lowercase hex), csv_sha256
- timestamp_source = device_monotonic_ms
- sensor_modes = {"BH1750":"continuous_high_res","SCD40":"periodic_5s"}
- recorded_start_utc = timezone-aware UTC ISO 8601
- optional instruments: model, address, check_status (unknown = TBD)

Exact CSV header:

    boot_id,sensor,seq,elapsed_ms,value,unit,ready

One row per new ready sensor sample. Each sensor's seq must increment independently; elapsed_ms must be monotonic from the device within one boot, not derived from host wall-clock strings. BH1750 uses lux and SCD40 uses ppm. Checks include raw-byte CSV hash, minimum 600000 ms span, at least 100 samples per sensor, gaps <=15000 ms, consecutive sequence, plausible values, and no SCD40 ready readings less than 4 seconds apart. This version assumes SCD40's normal ~5-second periodic mode, **not** ~30-second low-power mode. Values outside the SCD40 400–2000 ppm specified accuracy range produce a warning, not a fabricated calibration result.

## Real evidence gate — pending

Capture a genuine ten-minute ESP32-S3 BH1750/SCD40 session with firmware binary hash, device/boot identity, sensor configuration, recorded UTC start, power interruptions and a separate raw serial capture. Preserve hashes and run metadata. Reproduce the preflight, then independently inspect device wiring, raw bytes, setup and a controlled BH1750 light perturbation. Report failed captures. A CSV hash is not an attestation: independent provenance remains TBD.

No physical measurements, sensor-accuracy claims, energy claims or bench-validation status are established by these tests. See the parent hardware evidence gate in projects/HARDWARE_IOT_EVIDENCE_GATE_2026_10.md.

## Source / decision-changing parameter

Sensirion SCD4x official datasheet documents normal periodic updates at about 5 seconds and low-power periodic updates at about 30 seconds:
https://sensirion.com/en/media/documents/E0F04247/631EF271/CD_DS_SCD40_SCD41_Datasheet_D1.pdf

This explains why a fixed 5-second sampling-mode declaration is necessary; the validator must be revised before using low-power captures.

## 30–60 second demonstration

Run the unit tests and show that explicit synthetic origin, empty/single-sample logs, missing SCD40, duplicate sequence, clock reversal, fast SCD40 samples, 20-second gaps and CSV tampering are rejected. Show the provenance-unverified status even for the structurally valid fabricated fixture.

## v0.2 — dual-sensor coverage-window and malformed-row negative controls (2026-10-24)

The original v0.1 validator accepted **fabricated** logs where BH1750 covered the entire 600,000 ms window but SCD40 stopped after 500,000 ms or began at 100,000 ms. SCD40 still had at least 100 samples, no interior gap exceeded 15 seconds, and the global span appeared valid. It also accepted a row containing an extra CSV field when the manifest hash was recomputed. All three adversarial cases were reproduced as unexpectedly accepted **before** the correction.

v0.2 requires each sensor to appear within 15,000 ms of the global first and last device-monotonic timestamps; rejects extra/missing CSV columns; and reports per-sensor span and leading/trailing coverage gaps. A 5,000 ms start/end offset remains accepted as a tolerance control. The 15-second boundary is a **predeclared structural tolerance**, not a claim about sensor synchronization accuracy. It does not detect a fabricated capture, an omitted intermediate event, replay, a device clock fault, or physical provenance.

Reproduce with `python -B -m unittest -v test_capture_preflight.py`. Four added tests bring the local synthetic-only suite to **22**. Two independent process executions on CPython 3.13.5/Linux passed 22/22 each; published GitHub CI results require separate verification. Source/test Git blob SHAs: `792aa151aa37caaa6c0584319e364d1c1286264f` and `4400f47550839225d393ec0289c7a1df57d4d0e7`.

**Decision:** retain Prototype / Hardware Architecture. The next evidence-producing step is still a genuine, independently inspectable ten-minute BH1750 + SCD40 hardware capture with raw serial evidence and firmware provenance. Physical accuracy, calibration and device authenticity: **TBD**.
