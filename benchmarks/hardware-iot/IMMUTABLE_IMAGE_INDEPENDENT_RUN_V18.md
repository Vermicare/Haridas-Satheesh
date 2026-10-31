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
