# Hardware/IoT v2.0 — effective ESP32-S3 Kconfig evidence, independently checked

**Date:** 2026-11-01. **Stage:** Prototype / Hardware Architecture, unchanged. **Scope:** unflashed, software-only ESP-IDF configuration and reproducibility; not device attestation.

## Why this experiment matters

The [v1.9 result](ESP32S3_TARGET_INDEPENDENT_V19.md) established byte-identical unflashed ESP32-S3-targeted firmware on two Ubuntu runners, but retained only the full effective `sdkconfig` hash and limited target assertions. In particular, it did not establish whether PSRAM was enabled in the effective build configuration. This is a verification gap, **not** proof of hardware malfunction.

The additive [v2.0 extractor](effective_config_attestation_v20.py) now retains a deterministic **allowlisted subset** of effective Kconfig values, full-config SHA-256 linkage, and explicit physical-identity `TBD` fields. It intentionally does not publish the complete `sdkconfig` (which might contain private values). The existing v1.9 firmware and historical evidence are not overwritten.

## Independently verified hosted execution

- **Workflow:** [GitHub Actions #41285524639](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41285524639), completed SUCCESS on 2026-11-01: Ubuntu 22.04, Ubuntu 24.04 and cross-host comparison all passed. The companion [IoT synthetic preflight #41285524613](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41285524613) also passed Ubuntu and Windows.
- **Source branch:** `research/iot-esp32s3-target-independent-v19-20261031`. Workflow commit `e0aec61004838dcfe81aea71dfb25fe759506e66`; exact checked-out PR merge commit **`2f1767587aa1da17b9b4818ea2c1a7b7099ea098`** on both independent builders.
- **Build:** ESP-IDF v6.1, GCC 15.2.0, immutable image `espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`; resolved image config digest `sha256:1001c0c42918725dcdacfbcfdaa17cbf95370f2d15359e402b99d0a6237cb99c`.
- **Full effective sdkconfig SHA-256:** `a29b13aa114a9664fdabfb05db6f9a6153754b7d0d5d2cf1f6190c51baf5e491` on both hosts. **Full config bytes were not retained**, so independent reconstruction of that full hash is still impossible; the allowlisted subset and its hash linkage are directly inspectable.
- **New extracted subset SHA-256:** `456fb5d75d5ce7aad1d3287dd334b04dc19a3185116cc0c3c0d67b0e2ac08a07` on both hosts, with independent ZIP download, ZIP SHA checks, extracted JSON SHA checks and byte-for-byte cross-host comparison.
- **Observed effective software settings:** `CONFIG_IDF_TARGET="esp32s3"`; `CONFIG_ESPTOOLPY_FLASHSIZE="8MB"` (nominal); **`# CONFIG_SPIRAM is not set`**. This means **PSRAM is disabled in this build's configuration**; it does **not** establish whether the physical board contains or successfully detects PSRAM. The current sensor logger may not need PSRAM.
- **Unflashed outputs:** `app.bin`, `bootloader.bin`, `partition.bin`, `flasher_args.json` all remain byte-identical across both hosts, with the same member hashes already recorded in v1.9. No flash or sensor measurement occurred.
- **Synthetic negative controls:** extractor self-test passed 4 positive/structural checks and 7 rejection controls locally (CPython 3.13.5) and in both hosted builds; checks reject wrong target/flash size, duplicate settings, oversized/empty/invalid UTF-8 inputs, and exclude an unrelated fictional password field.

## Artifact provenance and reproduction

| Hosted artifact | ID | Independently verified ZIP SHA-256 | Retention |
|---|---:|---|---|
| Ubuntu 22.04 | `13074079992` | `a32fda807c2693fafeef7e0efff7550fb4258eb9ff64fe98dd5e5abfa82d00f5` | expires 2026-11-15 |
| Ubuntu 24.04 | `13074739380` | `2ba5c2864a9b7a36da783848276aa2515fa8c4e3347a6a5ea179d8f2163d7cf5` | expires 2026-11-15 |
| Comparison | `13074877391` | `4d8db71206db011756e90513ca436b4c651e8f2d8ea9ebb018fe886857041e17` | expires 2026-11-15 |

For a short independent review, download the two build ZIPs from the linked run, verify the listed ZIP digests, inspect `effective_config_v20.json` in each, verify `CONFIG_SHA256SUMS_v20.txt`, compare the JSON bytes and inspect `comparison.log` from the third ZIP. The original v1.9 offline verifier remains pinned to **historical v1.9 ZIPs**; do not use its hard-coded ZIP digests to mislabel this newer run.

## Decision / largest gap / next experiment

**Decision:** v2.0 closes the **inspectability of a selected effective Kconfig subset** and confirms that the reproducible unflashed build has PSRAM **configured off**. It does not close physical N8R8 compatibility or demonstrate a real sensor capture. No stage advancement, external review, deployment, merge, release, or product claim.

**Largest gap:** actual board flash-ID/capacity, module marking, PSRAM presence/mode and safe firmware match; authenticated >=600-second BH1750 + SCD40 physical raw capture all **TBD**.

**Next experiment:** under [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8), obtain a genuine private **read-only** flash identity transcript and review existing backed-up firmware, flash mode, partition layout and whether PSRAM is actually needed. Do **not** flash based on nominal ordering labels. If PSRAM is required, separately preregister a new unflashed build with explicitly selected memory mode, preserve its effective configuration subset, test it, and obtain independent hardware compatibility review before any flashing decision. Then conduct the genuine ten-minute sensor logging experiment.

**Kill/reframe:** if measured flash/PSRAM identity disagrees with candidate assumptions, stop physical integration and rebuild/review; if the sensor capture lacks genuine origin or continuous host/device evidence, treat it as a tooling test rather than Bench Validation.

**Four lenses:** hiring—demonstrates measured correction of a reproducibility blind spot; technical—preserves actual software configuration rather than inferring from a target name; innovation—no novelty assertion; founder—no device performance, safety, user or commercial evidence.
