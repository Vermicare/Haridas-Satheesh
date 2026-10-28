# Hardware/IoT v1.7 — controlled ESP32-S3 reproducible-build experiment

**Status (2026-10-28):** **Controlled same-container and two separate hosted-run byte equality VERIFIED** by independently downloaded artifacts and logs; cross-host/toolchain reproduction **TBD**. **Stage:** Prototype / Hardware Architecture (unchanged). **No physical hardware, flashing, sensor readings, calibration or deployment.**

## Why this experiment exists

The retained v1.6 same-checkout comparison in [SAME_CHECKOUT_REBUILD_V16_2026_10_28.md](SAME_CHECKOUT_REBUILD_V16_2026_10_28.md) found **70 changed application bytes and 39 changed bootloader bytes** between two successful builds of the same checkout; compile timestamps and dependent digests were among the differences. It did **not** prove that timestamps caused every changed byte. Keep its original hashes and negative decision intact.

Espressif documents [CONFIG_APP_REPRODUCIBLE_BUILD](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/reproducible-builds.html) as suppressing build date/time and path dependencies. [ESP32-S3 v6.1 Kconfig](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/kconfig-reference.html) documents the reproducibility and project-version settings. This experiment changes those **declared configuration variables** on a separate research branch; it does not edit the historical v1.6 build artifacts.

## Frozen procedure (before execution)

- Source: research/iot-reproducible-build-v17-20261028, stacked on draft PR #7. Tested PR head **`5a9009d7d9ef2d2d2d500aad4a50c5c596e780c5`**, checked-out PR merge SHA **`8d440e64331a03788379d30b8270ad964933dfa3`**.
- Firmware: the existing ESP32-S3 BH1750/SCD40 candidate, **unflashed**.
- Configuration: project-local `sdkconfig.defaults` sets `CONFIG_APP_REPRODUCIBLE_BUILD=y`, `CONFIG_APP_PROJECT_VER_FROM_CONFIG=y`, `CONFIG_APP_PROJECT_VER="iot-repro-v17"`.
- CI: [iot-reproducible-build-v17.yml](../../.github/workflows/iot-reproducible-build-v17.yml) uses the official Espressif ESP-IDF action requesting v6.1 and ESP32-S3. Resolved container digest **`sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`** (observed in hosted log); compiler **xtensa-esp-elf-gcc 15.2.0**; ESP-IDF **v6.1**. Python in container log **3.12.3**. The workflow still requests a **mutable v6.1 tag**, not an immutable digest; independently provisioned host/runner pinning **TBD**.
- First build: run `idf.py build` in the CI container; assert effective `sdkconfig` and retain app, bootloader, partition, flash arguments and per-file hashes.
- Second build: `idf.py fullclean`, delay, rebuild from the **same checkout in the same container**, retain the same four members, verify hashes, compare each member byte-for-byte.
- Report: preserve both builds and a `comparison_status.txt` (MATCH/MISMATCH). The job must fail if the members differ, but retain the negative artifact when possible.
- Reproduction: the workflow's source and commands are public; a second hosted run with unchanged firmware/config/workflow files and the same resolved container digest is verified below; a genuinely independent toolchain/host reproduction remains **TBD**.

## Predeclared decision

**PASS** only if both app, bootloader, partition and flash arguments match byte-for-byte with successful completed CI logs, effective config and member checksums. A PASS is **same-run, same-container clean-build repeatability only**; it does not establish reproducibility across days, independently provisioned runners, container versions or toolchains.

**FAIL** if any member differs or any build/config/hash step fails. Preserve logs and differences; do not weaken comparisons or reinterpret the v1.6 negative control. A later run with a pinned immutable image digest and separately provisioned environment is needed for stronger reproducibility.

**Verified in-scope result:** PASS for four retained member pairs under one container/run. **Unknown:** cross-host/toolchain reproduction, causal timestamp isolation, physical flashed firmware identity and physical sensor measurements **TBD**.

## Limitations and next physical gate

The old [same-checkout failure](SAME_CHECKOUT_REBUILD_V16_2026_10_28.md) and new config are **not** a randomized one-variable causal experiment: version is frozen as well as timestamps and build-path normalization. A match cannot attribute all historical mismatches uniquely to timestamps. Neither test establishes that a board is an 8 MB variant or that a physical sensor was connected. Never flash based on CI defaults alone; independently inspect actual flash ID and run a genuine private >=600-second BH1750/SCD40 capture with wiring and provenance review under [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8).

**Four lenses:** hiring manager—reproducible failure-to-control engineering; technical reviewer—explicit configuration, provenance and byte comparisons; innovation leader—reproducibility is engineering discipline, not novelty; founder—no device, customer or product performance evidence. No employer data, outreach, IP claim, release or maturity advancement.

## Verified hosted result — 2026-10-28 (same-container only)

[Final code-head GitHub Actions #40659292470](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659292470) **completed successfully**, job `122717976330`: both clean builds, effective config assertions, checksum verification, four `cmp` gates, artifact upload and final gate passed. The workflow was triggered from PR head `5a9009d7d9ef2d2d2d500aad4a50c5c596e780c5` and checked out merge SHA `8d440e64331a03788379d30b8270ad964933dfa3`. The two builds ran in the same official ESP-IDF v6.1 image resolved to digest `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`, with compiler `xtensa-esp-elf-gcc 15.2.0` (`esp-15.2.0_20251204`). Effective `sdkconfig` SHA-256: `45c2865ae1ae348a2ad1696136f783aa94afc11264152981056519ceeaf75816`.

The [retained artifact #12802833314](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659292470/artifacts/12802833314) was **independently downloaded and opened**. ZIP SHA-256 `f658976e6a846f1fdc73888ad3872f70e53fdf395d7ae1bee283308a4549c6d0` matched the GitHub-reported artifact digest. All **eight retained binary/config members** independently passed the embedded SHA256SUMS manifest; each of four first/second pairs was compared byte-for-byte outside CI:

| Unflashed member | Size each | Both-build SHA-256 | Independent pair equality |
|---|---:|---|---|
| Application | 196000 B | `3acc2c98ea480f15dbeaffa8d49c8812427dba73c69511e7bcc5a928e10d73f1` | MATCH |
| Bootloader | 21072 B | `da59a63758341ef54ff0083f178ea1f29ed7bc9cf89a8c7f64e9b0d2d9a9184b` | MATCH |
| Partition | 3072 B | `7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820` | MATCH |
| Flash arguments | 937 B | `43c1bb75a3e03982c9732cc7b2f3ff68e3dc5addef324eb1df34e1d293863aa2` | MATCH |

[Preflight regression #40659292677](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659292677) passed **124/124 tests on Ubuntu and 124/124 on Windows**; [ordinary unflashed compile #40659292450](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659292450) also succeeded at the tested head. These do not constitute real sensor measurements.

**Failure/learning:** earlier experimental CI runs [#40659014849](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659014849) and [#40659124132](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659124132) failed before compilation because a nested `sh -ec` invocation was incompatible with the action's command wrapper (`sh: 0: -c requires an argument`). The corrected direct command chain passed. These two failures are **CI invocation errors**, not firmware mismatches.

**Prior art / external limitation:** [Espressif Issue #13680](https://github.com/espressif/esp-idf/issues/13680) documents an earlier reproducible-build limitation in which toolchain paths could affect ELF SHA across machines. Thus even a local MATCH does not establish cross-machine byte identity. The next independent experiment should pin the immutable container digest, use a separate runner/time, verify source and config identity, and repeat the artifact comparison. **No maturity advancement, merge, release, physical flash, user outcome or product claim.**

## Independent second hosted run — cross-run equality observed (2026-10-28)

A later **documentation/registry-only** branch commit `5fe82887ff5286c55d518b254eea6390bc45b5ff` triggered [GitHub Actions #40660083184](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40660083184), which **completed successfully** (job `122720638715`) using PR merge checkout `21236c8fe227a07f39425a0165027256d184a7c3`. [Commit comparison](https://github.com/Vermicare/Haridas-Satheesh/compare/5a9009d7d9ef2d2d2d500aad4a50c5c596e780c5...5fe82887ff5286c55d518b254eea6390bc45b5ff) confirms **only this protocol and the registry changed**; firmware source, `sdkconfig.defaults` and workflow were unchanged. The two Git checkout merge SHAs differ; do **not** call this the same-checkout rerun.

The second job again resolved the **same** `espressif/idf:v6.1` image digest `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`, reported ESP-IDF v6.1 and `xtensa-esp-elf-gcc 15.2.0`, and reproduced effective `sdkconfig` SHA-256 `45c2865ae1ae348a2ad1696136f783aa94afc11264152981056519ceeaf75816`. The independently downloaded [second artifact #12803990362](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40660083184/artifacts/12803990362) has ZIP SHA-256 `d1471fdb8de9b12c1777f73701283a9af4b68f6c6330c346cdee2c294a0aa4ce`, matching GitHub's digest. All eight member manifest entries verified independently; all four within-run pairs matched, and **all eight first/second binary/config members matched the corresponding bytes from the first run #40659292470**. The exact application/bootloader/partition/flash-arguments SHA-256 values in the table above therefore hold across **both** separate hosted runs (four clean builds total).

**Evidence upgrade (narrow):** observed **cross-run byte repeatability under the same resolved image digest, compiler version, effective configuration and unchanged firmware source**, despite different documentation-only PR merge commits. This does **not** establish reproducibility across different container digests, compiler versions, machines/operating systems, or flash devices; it does **not** prove timestamps were the only cause of the earlier v1.6 mismatch. Preserve the historical negative result. Next: immutable image pin and independent environment, then real read-only flash identity and private sensor capture. **No maturity advancement, merge, release or physical measurements.**
