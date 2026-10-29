# SCD40 v3 supplemental UTC/monotonic clock-concordance negative control

**Date:** 2026-10-29. **Stage:** Adaptive Cooling remains Prototype / Documented R&D. **Evidence class:** fictional software regression, no sensor, no real 600-second wait, no thermal benefit claim.

## Gap and decision

The existing [v2 capture verifier](SCD40_CAPTURE_VERIFY_V2.md) checks that UTC strings parse with zero offset and that declared monotonic sample times increase. It does **not** check whether UTC time advances consistently with monotonic elapsed time. Its own positive fictional fixture uses the same UTC timestamp for all 120 samples while claiming 600 seconds elapsed. That fixture is useful for structural verification but should **not** be mistaken for clock-concordant acquisition.

The independent [v3 diagnostic](scd40_clock_concordance_v3.py) supplements rather than replaces v2. It compares each declared sample/completion UTC delta against the corresponding declared monotonic elapsed time, flags UTC regressions and deviations exceeding a declared default **10-second diagnostic tolerance**, and requires an independently supplied preexisting SHA-256. A clock-review flag is **not** proof of tampering: NTP corrections, clock configuration and logger timing may also explain it. A clean flag is **not** proof of real time or genuine hardware: both clocks and sensor data can be fabricated consistently.

**Why this matters:** a capture with frozen UTC but declared 600-second monotonic duration must not be presented as independently corroborated wall-clock logging. The existing 600-second v2 structural gate remains necessary but not sufficient for physical evidence.

## Reproduce — fictional data only

From `benchmarks/adaptive-cooling`:

```bash
python -B -m unittest -v test_scd40_clock_concordance_v3.py
```

Seven tests cover aligned fictional timestamps, frozen UTC, backward UTC, forward UTC jump, incorrect digest, non-increasing monotonic time and small (<10-second) UTC skew. On 2026-10-29, local Linux x86_64 / CPython 3.13.5 completed **7/7 tests**. Source Git blob: `6c617905b50f0825d81021d6ab7151d547ead3a1`; test Git blob: `3e2e08f07e1d5d18e08593a4f08741f1b62b2a08`. Hosted cross-platform outcome: **TBD until CI has completed**.

### 30–90 second demonstration

Run the seven-test command. The aligned fictional capture passes the clock diagnostic. A 600-second fictional stream with all UTC stamps frozen at the start returns `clock_review_required=true` and `max_utc_monotonic_skew_s=600`; a backward UTC jump is separately flagged. The tests do not assert that a real sensor was sampled.

## Use on a future real private capture

First run the existing v2 verifier with a SHA-256 recorded independently **before** review. Then run:

```bash
python -B scd40_clock_concordance_v3.py PRIVATE_CAPTURE.jsonl --expected-sha256 PINNED_LOWERCASE_SHA256
```

Keep raw JSONL, original logger receipt, instrument identity, wiring/placement, clock-sync state, calibration/reference checks and actual elapsed-time corroboration **private**. A review flag requires investigation and documentation; do not edit raw observations to make the check pass. Do not substitute this diagnostic for real instrument verification, independent ambient/target thermometers, airflow/surface/power measurement or controlled balanced fan-only comparison.

**Next gate:** actual Raspberry Pi + SCD40 >=600-second capture, verified provenance and a separate temperature/RH reference check. The manufacturer's [SCD4x design-in guide](https://sensirion.com/media/documents/0D0C9129/623B1183/Sensirion_CO2_Sensors_SCD4x_design-in_guide.pdf) warns that enclosure coupling and nearby heat sources can alter temperature and humidity readings. No physical measurements have been made by this experiment.
