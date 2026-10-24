# Hardware / IoT — October 2026 evidence gate

**Stage: Prototype / Hardware Architecture. No physical telemetry run is represented here.**

Local-only packages `iot_capture_to_telemetry_gate_v03_2026-10-21.zip` and `iot_evidence_sufficiency_gate_v04_2026-10-21.zip` describe synthetic serial-capture integrity and sufficiency checks. Their fictional 600-second timestamp span is **not** a measured ten-minute hardware recording. Tests indicate that empty, one-sample and wall-clock-only captures must not be accepted as sufficient evidence.

**Next:** capture genuine BH1750 and SCD40 readings for ten minutes with firmware hash, device identity, timestamp source, sensor settings, power interruptions, monotonic timing, and an independent capture audit. Accuracy and physical logging reliability: **TBD**. **Reframe** if the evidence cannot distinguish physical samples from replayed or fabricated records.

## October 23, 2026 — dual-sensor capture preflight (draft)

[Draft PR #7](https://github.com/Vermicare/Haridas-Satheesh/pull/7) adds a standard-library **synthetic-contract-only** capture validator and 18 adversarial regression tests. The first [Linux/Windows CI run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/39996795979) passed on Python 3.13. These tests check raw-CSV hash binding, device-monotonic span, per-sensor sequence/cadence, missing samples and explicit synthetic origin; they **do not authenticate physical readings**. Even fabricated input falsely declared physical can pass structural checks. No physical sensor measurements have been added.

[Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) scopes the actual ten-minute ESP32-S3 BH1750/SCD40 capture with raw serial/firmware provenance and independent review. **Stage remains Prototype / Hardware Architecture; physical accuracy/reliability TBD.**
