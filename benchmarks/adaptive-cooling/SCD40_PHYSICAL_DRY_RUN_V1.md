# Cooling physical logging bridge v1 — **not a thermal benchmark**

**2026-10-29.** This standalone Raspberry Pi script addresses the first physical-logging bottleneck in [Cooling Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15). It can acquire actual SCD40 temperature, relative humidity and carbon dioxide readings into an **exclusive-create private local JSONL file**. It does not simulate readings in the live command, control a cooling actuator, transmit data, or assert that a real device was run. **Physical executions: TBD; calibrated thermal measurements: TBD; thermal performance: TBD.**

## Supported device and limits

- The SCD40 provides an internal temperature/RH measurement in addition to CO₂. Its internal temperature can be affected by **self-heating, airflow, enclosure and offset configuration**, per [Sensirion SCD4x datasheet](https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf). It is **not** a calibrated independent ambient-versus-target comparison, surface probe, airflow meter or power meter.
- The [Adafruit CircuitPython SCD4x driver](https://docs.circuitpython.org/projects/scd4x/en/latest/api.html) documents start/stop periodic measurement, data-ready, temperature, relative humidity and CO₂. It updates approximately every five seconds. This script does not modify sensor calibration or persistent settings.
- The JSONL stream deliberately uses scd4x_temperature_c, **not** the existing benchmark's target_temp_c column. Never relabel one sensor as two independent measurement points. **Do not use this stream to calculate cooling superiority or energy efficiency.**

## On the Raspberry Pi 5, when the actual SCD40 is wired and I²C enabled

Install the documented driver in a Python virtual environment (python3 -m venv .venv, then .venv/bin/pip install adafruit-circuitpython-scd4x). Confirm correct 3.3 V-compatible wiring for your specific breakout and a common ground; do not connect 5 V signals directly to Pi GPIO. Confirm that the sensor is reachable at I²C address 0x62. Save the script locally, then:

~~~bash
.venv/bin/python scd40_dry_run_capture_v1.py \
  --output "$HOME/cooling-private/scd40_run_001.jsonl" \
  --run-id "cooling-dry-run-001" \
  --placement "sensor at fixed marked ambient point, 0.5 m above desk"
~~~

**The placement above is an illustrative command argument, not an observed setup. Replace it with the real geometry.** The command runs for 600 seconds measured using a monotonic clock; it never overwrites an existing capture. Record the actual hardware model, position, clock synchronization, reference-temperature check and stated uncertainty in the existing private instrument manifest. The script prints a SHA-256 of the local raw file at completion. Retain the file privately and pin its hash before any conversion. An interrupted run remains a partial JSONL file with no complete event or with a capture_failed event. No uploads occur.

capture_quality_gate_passed means **only** elapsed >=600 s, at least two received readings and no inter-reading gap >60 s; it is not a calibration, provenance, timing-accuracy, thermal or safety pass. A capture with zero samples can reach 600 seconds but correctly fails this quality gate. Record actual sensor sampling gaps and errors; do not edit raw data to force a pass.

## Reproduction and next evidence

~~~bash
python3 -B -m unittest -v test_scd40_dry_run_capture_v1.py
~~~

Seven **fictional test-double** unit tests cover event ordering, no-data refusal, nonfinite/out-of-range values, partial failure preservation, no overwrite, mandatory provenance and the 600-second clock gate. They require only the Python standard library and do **not** establish hardware operation. This logger is a preliminary sensor integration step and cannot replace the existing 13-column cooling raw CSV, instrument manifest, original logger bundle or preflights. Before any cooling comparison, obtain independent target and ambient temperature/RH probes, airflow/surface and energy instruments, record calibration/uncertainty and geometry, then execute the original ≥600-second multi-instrument dry-run gate and controlled position-balanced trials. No maturity advancement.
