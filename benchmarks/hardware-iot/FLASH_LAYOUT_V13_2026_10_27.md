# Hardware/IoT — unflashed firmware layout audit (2026-10-27)

**Status:** independent static inspection of an existing GitHub Actions artifact. **Not a flashed-device result.** Stage remains **Prototype / Hardware Architecture**.

## Source and reproduction

- Source: [draft PR #7](https://github.com/Vermicare/Haridas-Satheesh/pull/7), head `9061ed016a359d6ddf2d6b2fc38412f2dc396140`; [successful build #40457717468](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457717468); [downloadable artifact #12713162757](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457717468/artifacts/12713162757).
- Independently inspected ZIP SHA-256: `0a7b0fa13fb80ea7d63f85d756c1729636ffbfe8bd1cda6ff5fdb0985afdd7f3`; matches previously preserved evidence. Four internal SHA-256 checks matched `SHA256SUMS.txt`.
- ZIP provenance: `checked_out_sha=b26cc0cc12eba8317bb7f97fa202b7356f221349` (PR merge checkout); `pr_head_sha=9061ed016a359d6ddf2d6b2fc38412f2dc396140`. These are **not supposed to be identical**.
- Toolchain request: ESP-IDF v6.1; target: ESP32-S3. Exact physical board flash size: **TBD**, no device probe performed.

## Observed binary layout (bytes, end-exclusive)

| Component | Offset | Size | End |
|---|---:|---:|---:|
| Bootloader | `0x00000` | 21,120 | `0x05280` |
| Partition table | `0x08000` | 3,072 | `0x08C00` |
| Application | `0x10000` | 196,080 | `0x3FDF0` |

Parsed partition entries: NVS `0x9000..0xF000` (24,576 bytes); PHY init `0xF000..0x10000` (4,096 bytes); factory application `0x10000..0x110000` (1,048,576 bytes). Application **fits** its factory partition; the three flashed-file spans do not overlap.

**Important configuration review:** `flasher_args.json` explicitly declares `--flash-size 2MB`, while the proposed ESP32-S3-DevKitC-1-N8R8 board designation suggests a different nominal flash configuration. A 2 MB build declaration does **not by itself prove incompatibility** with a larger chip, and this audit does **not** establish the actual device capacity. Do not automatically change the flash setting or flash the ZIP based on the model designation. Confirm the exact board and its **independently detected** flash size, bootloader/partition layout, PSRAM settings and source before any device write.

## Independent test boundary and decision

A local Python standard-library ZIP auditor was run against the **actual downloaded** artifact, checking exact archive members, four hashes, duplicate JSON keys, declared flash size, offsets, binary headers, parsed partition boundaries and build provenance. It returned `STATIC_PACKAGE_PASS_FLASH_NOT_AUTHORIZED` and `HOLD_PENDING_OPERATOR_AND_DEVICE_REVIEW`. A separate fictional-package regression suite passed **14/14** locally; those fixtures are **not physical firmware**. No GitHub CI is claimed for these new tests unless separately published and run.

**Largest gap:** actual device flash capacity and binary/port identity, followed by a genuine independently reviewable >=600-second BH1750 + SCD40 capture. **Next experiment:** operator checks flash chip and board configuration without writing to the device, records probe output, then reviews/builds a board-matched firmware and preserves its exact hashes. Flashing, calibration, sensor data and independent hardware review remain **TBD**. Reframe as software-only tooling if physical provenance cannot be established.

No release, merge, real sensor result, novelty or performance claim.
