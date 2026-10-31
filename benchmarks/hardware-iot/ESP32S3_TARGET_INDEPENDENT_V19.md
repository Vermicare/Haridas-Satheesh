# Hardware/IoT v1.9 — explicit ESP32-S3 target and independent immutable-image builds

**Preregistered 2026-10-31. Execution result: PENDING at authoring.** This document records an experimental plan, **not** measured firmware reproducibility or hardware validation.

## Decision-changing reason

[Version 1.8](IMMUTABLE_IMAGE_INDEPENDENT_RUN_V18.md) independently verified four byte-identical unflashed firmware outputs across Ubuntu 22.04/24.04 under an immutable ESP-IDF v6.1 image. However, its logs explicitly selected default `esp32`, and its flasher arguments specified 2MB flash, so the outputs were not verified for the intended ESP32-S3 DevKitC-1 N8R8. The earlier v1.6 nondeterminism remains a genuine negative result. Neither result is overwritten.

## Frozen v1.9 protocol

- **Source:** a separate research branch stacked on the v1.8 draft, preserving the prior execution record and source. Pull-request jobs check out the exact event SHA; compare both jobs' checkout hashes.
- **Independent hosts:** GitHub-hosted Ubuntu 22.04 and 24.04, one clean build per runner. Neither runner flashes a board.
- **Immutable build image:** `espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`; fail closed if unavailable. Record the image config digest, source, compiler and ESP-IDF version.
- **Target intervention:** run `idf.py -D SDKCONFIG_DEFAULTS=<absolute pinned v1.9 defaults> set-target esp32s3`, then build with the same defaults. Assert `CONFIG_IDF_TARGET="esp32s3"`, `CONFIG_IDF_TARGET_ESP32S3=y`, `CONFIG_ESPTOOLPY_FLASHSIZE="8MB"`, and parse generated `flasher_args.json` to assert chip `esp32s3` and flash size `8MB`. The 8MB figure is the **nominal intended hardware configuration**, not a physical flash-ID measurement. PSRAM detection is **TBD**.
- **Reproducibility controls:** fixed app version `iot-repro-v19-s3`, reproducible-build Kconfig, SHA-256 of effective `sdkconfig` and v1.9 defaults, retained original logs, application, bootloader, partition and flash arguments. Independently validate each artifact's SHA-256 and compare member bytes, not ZIP archive bytes.
- **Failure preservation:** save logs and partial artifacts even on failure; never silently fall back to `esp32`, mutable image tags, or another flash size.

## Predeclared acceptance, stop and reframe

**PASS (bounded):** both runners complete; source/config/defaults/image identity match; effective target and nominal flash-size assertions pass on both; all four unflashed members have valid independently checked SHA-256 manifests and match byte-for-byte; logs and artifacts are inspected outside the workflow. This supports **only reproducible ESP32-S3-targeted software builds under one pinned toolchain**.

**FAIL:** target remains ESP32, nominal flash setting differs, config/image/source differs, missing or mismatched artifact, checksum failure, or incomplete hosted run. Record exact failure and isolate it in a subsequent version. A green workflow alone is insufficient without independent inspection.

**Still unverified after PASS:** board flash-ID, PSRAM mode/size, actual boot, electrical safety, sensor calibration, BH1750/SCD40 provenance, genuine ten-minute dual-sensor capture, and any deployment, product, performance, novelty or patentability claim. **No flashing or physical testing is authorized by this protocol.** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) governs physical capture; [Issue #21](https://github.com/Vermicare/Haridas-Satheesh/issues/21) governs build reproducibility.

## Evidence registry (pre-execution)

| Field | Value |
|---|---|
| Protocol | v1.9, 2026-10-31 |
| Code | [v1.9 workflow](../../.github/workflows/iot-esp32s3-target-independent-v19.yml) |
| Intended target | ESP32-S3; 8MB nominal flash |
| Build image | `espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c` |
| Independent host conditions | Ubuntu 22.04, Ubuntu 24.04 |
| Workflow run ID / event SHA / job IDs | TBD |
| Resolved image config digest / compiler | TBD |
| Effective target / flash args | TBD |
| Four output SHA-256 values | TBD |
| Independent artifact verification | TBD |
| Physical device observations | None |
| Stage | Prototype / Hardware Architecture; unchanged |

**Four-lens review:** hiring manager—corrective engineering after a discovered target mismatch; technical reviewer—independent checks must include effective target and member bytes; innovation leader—no novelty or invention inference; founder—no customer, deployment, hardware reliability or economic evidence. No merge, release, stage promotion or external commitment follows automatically.
