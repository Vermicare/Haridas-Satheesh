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


## Verified execution — 2026-10-31 (bounded PASS)

**Post-preregistration result:** [GitHub Actions run #41177363687](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41177363687) finished SUCCESS: Ubuntu 22.04 job 124467573322, Ubuntu 24.04 job 124467573179, comparison job 124468171807. Event head: 22c16cbafa5e4d0219187424b43b76462f47a77d; both jobs checked out the same pull-request merge commit 7728c67e55bced481d25ddd765c3ffa4eb2134a3 (not the event head).

All three ZIPs were separately downloaded and checked against GitHub artifact metadata; all eight firmware-member checksums were recomputed and four output members compared byte-for-byte. The application and bootloader image headers each contain ESP32-S3 chip identifier 0x0009; parsed flash JSON specifies esp32s3 and nominal 8MB. Hosted logs explicitly passed effective sdkconfig target and flash-size assertions. The effective sdkconfig *bytes* were not retained, only its checksum and passing assertions; physical flash-ID and PSRAM remain unknown.

| Retained artifact | Artifact ID | Independently checked ZIP SHA-256 |
|---|---:|---|
| Ubuntu 22.04 | 13032714755 | d4115c3116443581a54378076eb75608fa369a305c2a465ddc87e661f6855227 |
| Ubuntu 24.04 | 13033870346 | 076e5cc6d1cf7a84a1fc84f62ed8d59f99aaf455189808d429f6e107a6fdd941 |
| Comparison | 13033129253 | 6072bc8216970bd6a5038c97feb479b67f441e749375848571d2600d70192e5d |

| Byte-identical member | Independently checked SHA-256 (both hosts) |
|---|---|
| app.bin | 050cb7ac2bf0fe94748cda4d744cd0ae2f7a38cb86ccaadf34749ffb3fda3183 |
| bootloader.bin | aff00d000954beee5e794e825bbfe0a639c6ba3d5bce0f4dee7a448fa030229f |
| partition.bin | 7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820 |
| flasher_args.json | 05e0e4b03c968992f46699ce25bb3ca7e033f828ba7e84456d6ee4806d5c1fc5 |

**Conditions:** ESP-IDF v6.1, xtensa-esp-elf-gcc 15.2.0, immutable image espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c, resolved image config digest sha256:1001c0c42918725dcdacfbcfdaa17cbf95370f2d15359e402b99d0a6237cb99c. Effective sdkconfig SHA-256 a29b13aa114a9664fdabfb05db6f9a6153754b7d0d5d2cf1f6190c51baf5e491; defaults SHA-256 6f604cf449f9120a0878c61dfd8ab8403e2daf5295a1508d7704acbf346a3d33. Artifacts expire 2026-11-14.

**30–90-second reproducibility package:** download the three ZIPs in the table and run the [standard-library offline verifier](verify_v19_artifacts.py) as: python3 verify_v19_artifacts.py ubuntu22.zip ubuntu24.zip comparison.zip. Its local verification passed on all three original ZIPs; four local negative controls rejected modified ZIP bytes, altered member bytes, wrong chip target and cross-host mismatch. These local controls are not independent external review.

**Decision:** Reproducible ESP32-S3-targeted *unflashed software* builds are established for this pinned environment; v1.6 nondeterminism and v1.8 wrong-target failure remain preserved. Hardware/IoT stays **Prototype / Hardware Architecture**. **Next evidence gate:** read-only physical board flash/PSRAM identity inspection, then genuine ≥600-second BH1750/SCD40 logging with raw provenance and checksums under [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8). Stop/reframe if physical identity or measurements disagree. No flashing, hardware validation, maturity change, release or merge.
