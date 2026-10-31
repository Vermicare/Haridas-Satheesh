# ESP32-S3 BH1750 + SCD40 raw-capture firmware candidate (unflashed)

**Evidence status (2026-10-27):** source candidate, host CRC/CSV framing checks, and a **verified ESP-IDF v6.1 compile-only build**. **Flashed device: none; physical samples: zero.** This is not hardware validation or sensor calibration. It is an executable starting point for [physical capture issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) and the [PR #7 host-to-bundle verifier](../../host_bundle_chain.py).

## Fixed experimental contract

- ESP32-S3, ESP-IDF **6.1 intended** (not built in this run); 100 kHz I2C, SDA **GPIO8**, SCL **GPIO9**, common 3.3V/GND **only after checking each breakout's electrical ratings** and pull-ups.
- BH1750 address `0x23`, continuous high-resolution `0x10`; emits approximate lux every ~1 s.
- SCD40 address `0x62`, normal periodic `0x21B1` (~5 s); checks ready `0xE4B8`, reads `0xEC05` with CRC-8 (poly `0x31`, init `0xff`); emits only CRC-valid CO₂ ppm.
- Output lines are exactly `IOTCSV,boot_id,sensor,seq,elapsed_ms,value,unit,1` with **independent consecutive per-sensor sequence numbers** and **device-monotonic milliseconds**. The logger prints no Wi-Fi credentials, host identity, network data or sensor serial numbers. A pseudorandom boot token distinguishes sessions, **not** authenticates hardware.
- No imputation: I2C/CRC errors create **missing samples** and console warnings. SCD40 temperature/humidity are read for CRC but deliberately **not** represented as measured output. No precision, accuracy or calibration claim.

## Host-only tests already executed

From `benchmarks/hardware-iot`:

```sh
python -m unittest -v test_firmware_wire_contract.py
```

The Python wrapper compiles a portable C test with a detected host compiler; if no compiler exists it **skips**, which is not a pass. It checks CRC and exact framing including truncation refusal. Local GNU C 14.2.0 on Linux compiled with `-std=c11 -Wall -Wextra -Werror -pedantic` and the executable exited 0. This does **not** compile the ESP-IDF application, exercise I2C, verify hardware or establish serial timing.

**Source-document discrepancy to verify on real hardware:** the official SCD4x datasheet's example shows CO₂ word `0x01F4` followed by `0x7B`, while its documented CRC-8 polynomial `0x31` with initialization `0xFF` computes `0x33` for those two bytes. Other sample vectors (`0x6667 → 0xA2`, status `0x8000 → 0xA2`) match the polynomial. The implementation follows the polynomial; this discrepancy is **not** an empirical sensor result. Source: [Sensirion SCD4x datasheet](https://sensirion.com/en/media/documents/E0F04247/631EF271/CD_DS_SCD40_SCD41_Datasheet_D1.pdf).

## ESP-IDF v6.1 compile-only execution (2026-10-27; no board)

The actual ESP32-S3 application compiled in the official Espressif v6.1 Docker toolchain on a GitHub-hosted Ubuntu runner: [Actions #40421852576](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40421852576), source commit `79426a5ba1245264c386565dd5911d3a578180f8`. The log reports `ESP-IDF v6.1`, `Project build complete`, binary size **196080 bytes** and SHA-256 `28637965c44fcbe86fb441fafc553b6f4f7c4a8d68505a528faeefa49e877a55`. The runner pulled official `espressif/idf:v6.1` image digest `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`. The binary hash is **run-specific provenance**, not a claim of deterministic/reproducible binary bytes or proof of a flashed image. No binary artifact was retained for download.

The same source head also passed [host-only CI #40421852619](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40421852619): **83/83 synthetic/host tests on Ubuntu and 83/83 on Windows**. The compile is **not** an I²C transaction, sensor measurement, electrical review, flash verification, 600-second capture, or calibration. See [execution record](ESP_IDF_COMPILE_V11_EXECUTION_2026_10_27.md) and [registry](EVIDENCE_REGISTRY.json).

## Physical experiment (operator action; NOT performed)

1. In a **separate** ESP-IDF 6.1 terminal, review wiring and component dependencies, then from this directory run `idf.py set-target esp32s3`, `idf.py build`. Resolve any actual build errors; record full version, command and build log. Do not run the QHAP mining firmware simultaneously on the same ESP32-S3.
2. Compute SHA-256 of **the exact built firmware binary**, e.g. PowerShell `(Get-FileHash -Algorithm SHA256 .\build\iot_dual_sensor_capture.bin).Hash.ToLower()`. Independently review flash command and output. Flash with `idf.py -p COM7 flash` only after confirming the correct board/port. **Do not claim a file hash proves what was flashed.**
3. Close `idf.py monitor` and any serial-port application. From `benchmarks/hardware-iot`, use the exclusive raw-byte logger: `python serial_acquire.py --port COM7 --baud 115200 --seconds 660 --out PATH_OUTSIDE_GIT_TO_NEW_PRIVATE_HOST_DIR`. Keep the board powered and log interruptions. A 660 s request gives margin for >=600 s first-to-last-byte and device-monotonic coverage; success is not guaranteed.
4. Preserve the unmodified `raw_serial.log`, host manifest, firmware binary and build logs **privately**. Inspect for unexpected sensitive boot output. With the host manifest's actual UTC start, build a **new separate private** bundle: `python serial_bundle.py build --raw HOST_DIR/raw_serial.log --firmware PATH_TO_EXACT_BUILT_BINARY --out NEW_PRIVATE_BUNDLE_DIR --device-id OPERATOR_PSEUDONYM --recorded-start-utc ACTUAL_UTC --capture-origin physical`.
5. Run `python host_bundle_chain.py HOST_DIR NEW_PRIVATE_BUNDLE_DIR` and retain its JSON and failures. If capture resets, spans are too short, CRC fails or SCD40 cadence is wrong, **preserve the failure**; do not stretch/interpolate timestamps. Independently review firmware/wiring, raw bytes, SHA declarations and a recorded controlled BH1750 light change before describing any physical origin. CO₂ accuracy, reliability and calibration remain **TBD**.
6. Do not commit raw logs, personal locations, private device identifiers or network credentials. Publish only reviewed aggregates and a redacted reproduction record, with explicit unknowns.

## Stop/advance rule

Until a real >=600-second dual-sensor session and independent setup review pass, stage stays **Prototype / Hardware Architecture**. If the candidate fails to compile or acquire continuous data, preserve the failure and fix instrumentation; if provenance cannot be established, reframe the result as software logging tooling. No release, deployment, safety, performance or patentability claim.
