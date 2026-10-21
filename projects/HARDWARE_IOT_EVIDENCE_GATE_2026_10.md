# Hardware / IoT — October 2026 evidence gate

**Stage: Prototype / Hardware Architecture. No physical telemetry run is represented here.**

Local-only packages `iot_capture_to_telemetry_gate_v03_2026-10-21.zip` and `iot_evidence_sufficiency_gate_v04_2026-10-21.zip` describe synthetic serial-capture integrity and sufficiency checks. Their fictional 600-second timestamp span is **not** a measured ten-minute hardware recording. Tests indicate that empty, one-sample and wall-clock-only captures must not be accepted as sufficient evidence.

**Next:** capture genuine BH1750 and SCD40 readings for ten minutes with firmware hash, device identity, timestamp source, sensor settings, power interruptions, monotonic timing, and an independent capture audit. Accuracy and physical logging reliability: **TBD**. **Reframe** if the evidence cannot distinguish physical samples from replayed or fabricated records.
