# Hardware/IoT v1.7 — controlled ESP32-S3 reproducible-build experiment

**Status (2026-10-28):** Protocol committed; hosted compilation/result **TBD** until GitHub Actions logs and downloadable artifacts are independently inspected. **Stage:** Prototype / Hardware Architecture (unchanged). **No physical hardware, flashing, sensor readings, calibration or deployment.**

## Why this experiment exists

The retained v1.6 same-checkout comparison in [SAME_CHECKOUT_REBUILD_V16_2026_10_28.md](SAME_CHECKOUT_REBUILD_V16_2026_10_28.md) found **70 changed application bytes and 39 changed bootloader bytes** between two successful builds of the same checkout; compile timestamps and dependent digests were among the differences. It did **not** prove that timestamps caused every changed byte. Keep its original hashes and negative decision intact.

Espressif documents [CONFIG_APP_REPRODUCIBLE_BUILD](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/reproducible-builds.html) as suppressing build date/time and path dependencies. [ESP32-S3 v6.1 Kconfig](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/kconfig-reference.html) documents the reproducibility and project-version settings. This experiment changes those **declared configuration variables** on a separate research branch; it does not edit the historical v1.6 build artifacts.

## Frozen procedure (before execution)

- Source: research/iot-reproducible-build-v17-20261028, stacked on draft PR #7. Exact tested commit SHA and PR merge checkout: **TBD until hosted execution**.
- Firmware: the existing ESP32-S3 BH1750/SCD40 candidate, **unflashed**.
- Configuration: project-local `sdkconfig.defaults` sets `CONFIG_APP_REPRODUCIBLE_BUILD=y`, `CONFIG_APP_PROJECT_VER_FROM_CONFIG=y`, `CONFIG_APP_PROJECT_VER="iot-repro-v17"`.
- CI: [iot-reproducible-build-v17.yml](../../.github/workflows/iot-reproducible-build-v17.yml) uses the official Espressif ESP-IDF action requesting v6.1 and ESP32-S3. Exact resolved container digest, toolchain patch, Python patch and host image: **TBD**, not assumed pinned by a mutable tag.
- First build: run `idf.py build` in the CI container; assert effective `sdkconfig` and retain app, bootloader, partition, flash arguments and per-file hashes.
- Second build: `idf.py fullclean`, delay, rebuild from the **same checkout in the same container**, retain the same four members, verify hashes, compare each member byte-for-byte.
- Report: preserve both builds and a `comparison_status.txt` (MATCH/MISMATCH). The job must fail if the members differ, but retain the negative artifact when possible.
- Reproduction: the workflow's source and commands are public; an independent rerun from the same commit and fixed container digest is still **TBD**.

## Predeclared decision

**PASS** only if both app, bootloader, partition and flash arguments match byte-for-byte with successful completed CI logs, effective config and member checksums. A PASS is **same-run, same-container clean-build repeatability only**; it does not establish reproducibility across days, independently provisioned runners, container versions or toolchains.

**FAIL** if any member differs or any build/config/hash step fails. Preserve logs and differences; do not weaken comparisons or reinterpret the v1.6 negative control. A later run with a pinned immutable image digest and separately provisioned environment is needed for stronger reproducibility.

**Unknown:** Actual result **TBD**; run/job/artifact IDs **TBD**; resolved container digest **TBD**; measured binary hashes **TBD**; physical flashed firmware identity **TBD**.

## Limitations and next physical gate

The old [same-checkout failure](SAME_CHECKOUT_REBUILD_V16_2026_10_28.md) and new config are **not** a randomized one-variable causal experiment: version is frozen as well as timestamps and build-path normalization. A match cannot attribute all historical mismatches uniquely to timestamps. Neither test establishes that a board is an 8 MB variant or that a physical sensor was connected. Never flash based on CI defaults alone; independently inspect actual flash ID and run a genuine private >=600-second BH1750/SCD40 capture with wiring and provenance review under [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8).

**Four lenses:** hiring manager—reproducible failure-to-control engineering; technical reviewer—explicit configuration, provenance and byte comparisons; innovation leader—reproducibility is engineering discipline, not novelty; founder—no device, customer or product performance evidence. No employer data, outreach, IP claim, release or maturity advancement.
