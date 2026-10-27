# Hardware/IoT v1.5 — read-only flash identification transcript gate (2026-10-28)

**Scope:** operator preparation for [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8), **not a hardware observation**. Draft PR #7 only. Maturity stays **Prototype / Hardware Architecture**.

## Decision-driving problem

The retained unflashed ESP-IDF v6.1 bundle reports a **2 MB flash-size setting**, while the proposed ESP32-S3-DevKitC-1-N8R8 designation has a nominal **8 MB** flash configuration. Neither establishes the flash capacity of the connected physical board. Before any flash, the operator needs a read-only flash-ID transcript and a fail-closed review of the reported chip and flash capacity. A difference is a **hold for configuration review**, not proof that the existing image will fail.

## Procedure — NOT performed by automation

1. Stop any active serial monitor, QHAP mining/experiment on the **same ESP32-S3**, or other process holding the port. Identify the correct board and actual COM port in Device Manager. The commands below can temporarily reset/interrupt the connected board but do not request a flash write.
2. In an ESP-IDF/esptool terminal with the correct board connected, run **only** the identification command appropriate to the installed version:
   - esptool v5: `python -m esptool --chip esp32s3 --port COM7 flash-id`
   - esptool v4: `python -m esptool --chip esp32s3 --port COM7 flash_id`
   Replace COM7 only after checking the actual port. **Never** substitute `write-flash`, `erase-flash`, `burn-efuse` or a firmware-update command.
3. Privately preserve the complete stdout/stderr and actual tool version in a location **outside Git**; it may contain a device MAC or serial. Review for warning/error text. Do not upload or paste the raw transcript publicly.
4. From `benchmarks/hardware-iot`, run `python read_only_flash_probe_v15.py PATH_TO_PRIVATE_TRANSCRIPT --build-flash-mb 2`. The parser reads a saved transcript; it does **not** open COM ports or contact a device. Its JSON deliberately excludes MAC/serial, but its output is still only an **unverified operator assertion**.
5. If the output reports a different flash size, stop for independent board/bootloader/partition/PSRAM/image review. **Even if sizes match, the gate remains `TRANSCRIPT_PARSED_FLASH_NOT_AUTHORIZED`.** Confirm binary provenance, source, flash mode and wiring separately before considering a write. Preserve failures rather than modifying the transcript to force a pass.

## Evidence and regression

- Local isolated test command: `python -m unittest -v test_read_only_flash_probe_v15.py`
- **15/15 fictional transcript tests passed locally** under CPython 3.13.5/Linux. [GitHub Actions #40581083385](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40581083385) passed **119/119 tests on Ubuntu and 119/119 on Windows** (both job logs inspected), including all 15 new cases. The fixtures are synthetic strings resembling common esptool v4/v5 output, not captured from a physical ESP32-S3.
- Negative controls: wrong/missing/multiple chip identifications; missing/multiple/unsupported/malformed flash sizes; error and warning text; unsupported build size; oversized transcript; redaction of fictional MAC, and non-disclosure of private paths when a transcript cannot be read.
- No real `flash-id` command was run, no board was connected, no firmware was flashed, and **zero physical BH1750/SCD40 readings** were acquired. Firmware flashed identity, actual flash size, sensor accuracy and 600-second coverage remain **TBD**.
- Known limitations: a forged transcript can pass; esptool output formats can change; text parsing is not hardware attestation; a successful size comparison cannot authorize flashing.

## Primary manufacturer references

- [Espressif esptool flash size detection and flash-id](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/flash-modes.html).
- [Espressif esptool command reference](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/).
- [Espressif ESP32-S3 DevKitC-1 module variants](https://docs.espressif.com/projects/esp-idf/en/v5.3.1/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html).

## Next evidence gate

Obtain a **genuine, private, independently reviewed** device/flash-ID transcript and source/board configuration record, then decide whether a board-matched rebuild is necessary. Only after an approved flash and wiring review attempt a >=600-second raw dual-sensor session with host/device continuity, hashes, light perturbation and independent physical-origin review. No stage change, release, physical-performance claim or novelty assertion.
