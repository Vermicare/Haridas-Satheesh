# ESP32-S3 dual-sensor firmware — ESP-IDF compile-only execution v1.1

**Run:** 2026-10-27 (UTC log start 2026-10-26 23:45); **evidence type:** hosted compile, no hardware. **Stage:** Prototype / Hardware Architecture (unchanged).

## Reproducible question

Does the existing unflashed BH1750/SCD40 ESP32-S3 application compile using the actual intended ESP-IDF 6.1 toolchain, rather than only a portable host C test?

## Provenance / run conditions

- Repository: `Vermicare/Haridas-Satheesh`; draft PR #7; exact source commit `79426a5ba1245264c386565dd5911d3a578180f8`.
- Workflow: [`.github/workflows/iot-espidf-compile.yml`](../../../../.github/workflows/iot-espidf-compile.yml); [Actions run #40421852576](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40421852576).
- Runner: GitHub-hosted `ubuntu-latest`; official `espressif/esp-idf-ci-action@v1`; Docker `espressif/idf:v6.1`, observed image digest `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`.
- Commands: `idf.py --version && idf.py build && sha256sum build/iot_dual_sensor_capture.bin`; target `esp32s3`.
- Log: `ESP-IDF v6.1`; `Project build complete`; application binary `iot_dual_sensor_capture.bin` size `0x2fdf0` = **196080 bytes**; SHA-256 `28637965c44fcbe86fb441fafc553b6f4f7c4a8d68505a528faeefa49e877a55`.
- No downloadable firmware binary artifact retained. SHA-256 is **one-run provenance**, not evidence of byte-reproducible builds or actual flash identity.
- Independent host regression workflow on same commit: [Actions #40421852619](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40421852619), **83/83 tests passed on Ubuntu and 83/83 on Windows**; portable C test executed.

## Result and negative/unknown evidence

**Compile: PASS.** ESP-IDF compilation was previously **TBD**; this gate is now satisfied in a hosted build. There is no physical board, I²C transaction, flashed image, raw sensor byte, 600-second recording, sensor calibration or field reliability result. Flash identity, CO₂/lux accuracy, continuity, independent setup review and physical origin are **TBD**. No new failure was observed in the compile; the earlier host-only signedness and datasheet CRC example discrepancies remain recorded separately. A successful build does not imply correct timing, sensor behavior or reproducible binary bytes.

## Next decision

No maturity advancement or release. Operator should review the intended ESP32-S3 board/port and 3.3V/I²C electrical connections, flash a locally preserved and SHA-256-recorded firmware binary, and collect a genuine private >=600-second dual-sensor session under [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8). Preserve raw serial bytes outside Git; run the existing host-to-bundle checks; record failures and controlled light perturbation. Reframe as software instrumentation if physical provenance cannot be established.
