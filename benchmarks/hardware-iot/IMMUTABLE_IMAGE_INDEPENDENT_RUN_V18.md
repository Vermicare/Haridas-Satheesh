# Hardware/IoT v1.8 — immutable-image independent-runner firmware test

**Pre-execution protocol, 2026-10-31. Status: NOT YET EXECUTED when committed.**
**Maturity:** Prototype / Hardware Architecture (unchanged). **Physical measurements:** none.
This is a strictly **unflashed software-build experiment**; no board, sensor, device identity, energy, thermal, accuracy, novelty or product claim.

## Why this test

[Issue #21](https://github.com/Vermicare/Haridas-Satheesh/issues/21) retains a real v1.6 negative result: the same checkout produced 70 differing application bytes and 39 differing bootloader bytes, including embedded timestamps. The v1.7 controlled reproducible-build configuration later produced byte-identical application, bootloader, partition and flasher arguments within one container and across two hosted runs, but the official ESP-IDF action requested the mutable `v6.1` image tag. Its Docker image argument cannot safely be replaced with a bare digest in the version input. The earlier negative evidence must remain intact.

## Frozen intervention and independent variables

- **Source/config:** stacked on [draft PR #22](https://github.com/Vermicare/Haridas-Satheesh/pull/22), retaining its `CONFIG_APP_REPRODUCIBLE_BUILD=y`, fixed `CONFIG_APP_PROJECT_VER` and ESP32-S3 target. Do not edit historical v1.6/v1.7 results.
- **Container reference:** `espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`, the **historically observed** v1.7 resolved digest. The workflow must fail rather than silently use `v6.1` if this digest is unavailable. Platform availability is **TBD** until logs are checked.
- **Independent runner images:** `ubuntu-22.04` and `ubuntu-24.04`, each independently checking out the **same exact pull-request event SHA**. The jobs share the requested image digest but have different host images. This is not a cross-toolchain test.
- **Builds:** one clean `idf.py build` per runner; record checkout SHA, requested and resolved image digests, Docker server version, compiler and ESP-IDF versions, effective `sdkconfig` hash, build log, runner OS and the four binary/layout members.
- **Member comparison:** verify per-artifact `SHA256SUMS.txt` before comparing application, bootloader, partition and flasher-arguments **bytes** across jobs. A ZIP digest alone is not acceptable. Retain failed-build logs and failed comparison logs when available.
- **Actions provenance:** `actions/checkout`, `upload-artifact`, and `download-artifact` are pinned to the full commits returned by their official GitHub `refs/tags/v4` endpoints on 2026-10-31. This pinning is independent of the ESP-IDF image digest.

## Preregistered decision

**PASS (bounded):** both independently provisioned runners report the same source SHA, effective configuration, exact image reference and image config digest, and independently verified hashes and byte equality for all four retained members; the workflow completes successfully and logs/artifacts are independently inspected.

**FAIL / blocker:** a digest pull failure, missing artifact, config mismatch, missing or invalid checksum, different source SHA, different container config digest, differing bytes, or incomplete CI execution. Report the exact failure and preserve any available logs. Do not treat a green build step alone as a verified cross-run result.

**Still unknown after PASS:** original v1.6 timestamp causality; cross-toolchain or cross-architecture reproducibility; physical flash-ID, sensor identity and calibration; genuine >=600-second BH1750/SCD40 recording under [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8). The workflow does not flash a board.

## Verification and expiry

Execution results, job IDs, exact event SHA, SHA-256 manifests, per-file comparisons and failures must be added **only after hosted execution and independent reread**. GitHub artifact retention is 14 days, so durable public summaries should contain hashes and non-sensitive provenance while original artifacts are retained privately as appropriate. Never publish private device identifiers, credentials, personal telemetry or employer information.

**Four-lens check:** hiring manager—visible negative-to-control engineering; technical reviewer—identical checkout and immutable-image evidence; innovation leader—no claim of invention; founder—no device, customer, deployment or revenue evidence. No maturity advancement, merge or release is authorized by this protocol.


## Post-execution result — 2026-10-31 (independently inspected)

**Bounded software reproducibility: PASS. Intended ESP32-S3 target validation: FAIL / not established.** This distinction is essential.

[GitHub Actions #41169523114](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41169523114) at event checkout SHA `3ae02b3837782a660d9b218f7ccdfdf15534bed5` completed three jobs successfully: Ubuntu 22.04 job `124444249509`, Ubuntu 24.04 job `124444249307`, and comparison job `124444826092`. Their full hosted logs were inspected. All three [retained artifacts](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41169523114) were independently downloaded on October 31; each downloaded ZIP SHA-256 matched the GitHub-reported artifact digest. All eight per-member SHA-256 entries were recomputed from the two independent ZIPs and verified; every corresponding member was byte-identical, not merely ZIP-equal.

| Unflashed member | SHA-256 (identical on both runners) |
| --- | --- |
| `app.bin` (169104 bytes) | `88f29fb21d352627f915071344afd35f237e358e95543b374fabcbb65e031170` |
| `bootloader.bin` (26112 bytes) | `1c585fb2d829d4f9c5a2227b5a94f984f0f3a19529e06dc806fd1ef17704047b` |
| `partition.bin` (3072 bytes) | `7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820` |
| `flasher_args.json` (941 bytes) | `d7c343f169170dbcdfc6dbe7a214ac950f7143ead2bacaebe9d58bff000415ac` |

- Ubuntu 22.04 artifact `13030572160`: ZIP SHA-256 `91fbbceb8c4663d5ab49318398993bba5aa58dc76b82d49beb94b68b49373bb6`.
- Ubuntu 24.04 artifact `13030910333`: ZIP SHA-256 `bb5cde90b74be7a28dfe00db6e8c7a1eb0c133873d867cb2401468bef1838415`.
- Comparison artifact `13030402286`: ZIP SHA-256 `c89366565d5cc920fe23882f7136f4ecf1c3eea2d303ab10aa4fea3e5486411a`.
- Both runners: ESP-IDF v6.1, GCC 15.2.0, image reference `espressif/idf@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`, image config digest `sha256:1001c0c42918725dcdacfbcfdaa17cbf95370f2d15359e402b99d0a6237cb99c`, effective `sdkconfig` SHA-256 `9679481a5889ab0d44fccb1d482cb7e14aa30192701f247e36e7772d2cc6497a`. The two ZIPs differ as archives, which is not a firmware mismatch. Artifact expiry: 2026-11-14.

**Critical newly detected target mismatch:** The actual hosted build logs explicitly state `IDF_TARGET not set, using default target: esp32` and `Building ESP-IDF components for target esp32`; generated flasher commands specify `--chip esp32 --flash-size 2MB`. The versioned `sdkconfig.defaults` does not set `CONFIG_IDF_TARGET`, and no checked-in effective `sdkconfig` was present. Therefore these are reproducible **ESP32-targeted**, unflashed software outputs, **not** verified ESP32-S3-compatible firmware. This invalidates any inference that the run has produced a board-matched image for the stated ESP32-S3 DevKitC-1 N8R8. Do not flash these binaries or promote physical-hardware maturity.

**Next bounded corrective experiment:** On a separate research revision, explicitly select `esp32s3` with `idf.py set-target esp32s3` before building; assert effective `CONFIG_IDF_TARGET=\"esp32s3\"`, target-specific flasher arguments and the expected memory/partition configuration; rerun two independent immutable-image builds, retain per-member hashes and failures, and independently verify. Physical flash capacity/PSRAM/board identity must still be read-only verified before any later flash. Preserve the original v1.6 mismatch and this v1.8 bounded positive result without overwriting either.

**Decision:** Hardware/IoT stays Prototype / Hardware Architecture. This result establishes cross-host byte agreement for one pinned **ESP32** build configuration only; no device, sensor, calibration, reliability, novelty, safety or product evidence. No merge, release or flash.
