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

Reproduce with `python -B -m unittest -v test_capture_preflight.py`. Four added tests bring the local synthetic-only suite to **22**. Two independent process executions on CPython 3.13.5/Linux passed 22/22 each; [GitHub Actions #40045980176](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40045980176) independently passed **22/22 tests on both Python 3.13 Linux and Windows**; both job logs were inspected. This CI was triggered at test commit `d0cbf227a03f67bd4c70ca003f50f2572a0e66df` and verifies the source/test blobs recorded below. Source/test Git blob SHAs: `792aa151aa37caaa6c0584319e364d1c1286264f` and `4400f47550839225d393ec0289c7a1df57d4d0e7`.

**Decision:** retain Prototype / Hardware Architecture. The next evidence-producing step is still a genuine, independently inspectable ten-minute BH1750 + SCD40 hardware capture with raw serial evidence and firmware provenance. Physical accuracy, calibration and device authenticity: **TBD**.


## v0.3 — raw-serial bundle packaging (2026-10-24; synthetic tests only)

The separate [serial_bundle.py](serial_bundle.py) takes **already captured** raw UTF-8 serial bytes, a locally supplied firmware binary, an operator-declared device identifier and an explicit UTC session start. It extracts lines that begin exactly with `IOTCSV,` followed by the seven fields listed above. Other serial lines remain in `raw_serial.log`; prefixed ESP-IDF monitor lines are intentionally rejected rather than silently transformed. This script **does not open COM ports, flash firmware, acquire sensor readings or attest origin**. Capture raw serial with a suitable local serial logger configured to preserve bytes and without monitor prefixes.

Example after a **genuine physical session**, with the operator verifying these values against actual hardware (replace every placeholder):

```bash
python serial_bundle.py build --raw /path/to/actual_raw_serial.log \
  --firmware /path/to/exact_flashed_firmware.bin \
  --out /path/to/new_session_directory \
  --device-id YOUR_DEVICE_ID \
  --recorded-start-utc 2026-10-24T00:00:00Z \
  --capture-origin physical
python serial_bundle.py verify /path/to/new_session_directory
```

The timestamp above is an **example**, not an actual session time. Without `--capture-origin physical`, the default is `synthetic` and the physical preflight rejects it. The origin flag is an **operator assertion**, not proof; a fabricated stream falsely declared physical can still pass. Do not publish a real session until independent wiring, source, flashed-binary identity, operator clock, perturbation and instrument checks are reviewed.

The new directory contains `raw_serial.log`, `samples.csv`, `manifest.json`, and `preflight.json`. It refuses to overwrite an existing directory; records raw, CSV and supplied firmware hashes; verifies that CSV is exactly re-extracted from preserved raw bytes; and then calls the existing v0.2 structural validator. It does **not** embed or verify the flashed firmware binary, authenticate device-monotonic timestamps, prove sensor calibration, or guarantee crash-atomic multi-file publication. If interrupted, retain the partial directory as a failed capture; do not infer a pass.

**Tested:** 14 new adversarial fictional tests plus 22 existing tests = **36/36 local passes** in two isolated CPython 3.13.5/Linux directories; normalized output SHA-256 `89fd2364b76a43759d8368419377306a91c40d308a6aaae25b33a82662971a8c`. Exact executed source Git blobs: `serial_bundle.py` `28ecfb570f42c3a50b68f8e3e918803fe7440df8`, `test_serial_bundle.py` `bd9af27c95715c055fc60876216b0ba407aca1b7`. [GitHub Actions #40079273378](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40079273378) **passed 36/36 tests on Ubuntu/Python 3.13 and 36/36 on Windows/Python 3.13**; both job logs were inspected at head `4134b0ee90ec22fc57fef1ca5f9641e6a73f0978`. All readings in these tests are fictional. Physical session count remains **zero**. **No stage change.**

## v0.4 — direct host serial acquisition (2026-10-24; injected-port tests only)

[serial_acquire.py](serial_acquire.py) closes the practical gap between an ESP32-S3 USB serial port and the existing [raw-byte bundle builder](serial_bundle.py). It captures **unmodified host-received bytes** to a private, newly created directory, records UTC and host-monotonic timing, a local SHA-256, serial settings and byte count, and preserves a partial file plus failure manifest on read/port/size errors. It refuses to write raw logs under a Git worktree. The default 10 MB cap is a safety limit, not a guaranteed capacity for every baud rate.

**Prepare the ESP32 firmware first** to emit exactly `IOTCSV,<boot_id>,<sensor>,<seq>,<elapsed_ms>,<value>,<unit>,<ready>` with no ESP-IDF monitor prefixes. Both BH1750 and SCD40 must be ready; SCD40 normal periodic mode should provide approximately one new ready reading per five seconds. This acquisition script **does not program the ESP32, verify sensor wiring, authenticate firmware or parse telemetry**.

On the operator's own computer (not CI), install the separate optional dependency `pyserial==3.5`, close any program holding the COM/tty port, create a private parent folder **outside the Git repository**, and run one actual 630-second session:

```bash
python -m pip install pyserial==3.5
python serial_acquire.py --port COM7 --baud 115200 --seconds 630 --out /path/to/private/new_session
# On Linux/Raspberry Pi, replace COM7 with the actual /dev/ttyACM0 or /dev/ttyUSB0.
```

The output directory must not exist; its parent must exist. On success it contains `raw_serial.log` and `capture_manifest.json`; on failure retain `raw_serial.partial` and `capture_manifest.json` as negative evidence. The manifest status `HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED` establishes only a completed host-port read, **not** ten minutes of valid device-monotonic data. Check the downstream device span separately. Raw bytes may contain Wi-Fi credentials or other private debug output: **never commit or publish raw logs before manual confidentiality review**.

After an actual session, preserve an independently identified exact flashed firmware binary, device/wiring photos and operator notes **privately**, then run `serial_bundle.py build --raw <private/raw_serial.log> --firmware <exact_binary> --out <new_private_bundle_dir> --device-id <operator_verified_id> --recorded-start-utc <actual_UTC_start> --capture-origin physical` and `serial_bundle.py verify <bundle_dir>`. The origin field remains an operator assertion, not independent attestation. Do not reuse the example date or fabricate physical evidence. Any incomplete, interrupted or structurally rejected session stays a failure; do not cherry-pick it away.

**Verification boundary:** `test_serial_acquire.py` has 11 fictional injected-port tests (exact bytes, non-UTF8 preservation, no data, read/port failure, size cap, invalid inputs, preexisting directory, and Git-tree privacy guard). Two CPython 3.13.5/Linux process runs passed 11/11 each. Locally executed Git blobs: acquisition source `3088ea54c4dda40ee7e8849bf688b846dce8c2b2`; tests `42606fb3863dacaf13cf3da31b38d2b04a25a321`. [GitHub Actions #40091162076](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40091162076) passed **47/47 tests on Linux and 47/47 on Windows (Python 3.13)**, with both job logs inspected at commit `ead998e183a27600d830b45d58087c80c373c340`. Physical capture remains **TBD**. Maturity stays **Prototype / Hardware Architecture**. Next gate remains Issue #8: a genuine ten-minute dual-sensor session, firmware provenance, controlled BH1750 light perturbation and independent review.

## v0.7 host-to-bundle integrity chain — 2026-10-25

After collecting private raw serial bytes with `serial_acquire.py` and deriving a bundle with `serial_bundle.py`, run:

```sh
python host_bundle_chain.py PRIVATE_HOST_CAPTURE_DIR PRIVATE_DERIVED_BUNDLE_DIR
python -m unittest -v test_host_bundle_chain_v07.py
```

The new verifier binds the exact host raw bytes to the derived bundle, requires at least 600 seconds of host elapsed time **and** first-to-last byte arrival **and** 600,000 ms of device-monotonic telemetry, and rejects short-burst replay, mismatches, incomplete sessions and invalid bundles. These are **operator-controlled structural checks, not physical authentication**. All 75 tests passed on [Ubuntu and Windows CI #40217485476](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40217485476), including two fictional full-chain integration tests per OS. [Evidence and failure record](HOST_BUNDLE_CHAIN_V07.md) · [Registry](HOST_BUNDLE_CHAIN_V07_REGISTRY.json). No real hardware was accessed. The genuine instrumented session remains [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8).
