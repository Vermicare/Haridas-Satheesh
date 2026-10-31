# Hardware/IoT — independently downloaded ESP32-S3 CI firmware bundle v1.2

**Date:** 2026-10-27. **Stage:** Prototype / Hardware Architecture (unchanged). **Evidence:** hosted firmware compilation, immutable build artifact, independently downloaded byte verification. **Physical sensor measurements / actual flash / independent hardware review:** TBD.

## Question and baseline

Can the existing ESP-IDF v6.1 dual-sensor firmware be retained as an independently inspectable **byte-exact unflashed build package**, rather than leaving only a SHA-256 printed in a compile log? The earlier [compile-only evidence](firmware/espidf_dual_sensor_capture/ESP_IDF_COMPILE_V11_EXECUTION_2026_10_27.md) succeeded but retained no downloadable firmware bytes.

## Failure preserved and corrected

[First bundle attempt, Actions #40456945522](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40456945522): ESP-IDF compilation succeeded but the host-runner SHA file creation failed with `SHA256SUMS.txt: Permission denied`. The official container left the build directory owned by another user. **No artifact was uploaded** in that failed run. This is an actual workflow failure, not a sensor or firmware compilation failure.

[Fixed workflow commit](https://github.com/Vermicare/Haridas-Satheesh/commit/55ada26c0109171b4604dfca9f9698969ed9970f) copies the four build outputs into `RUNNER_TEMP` without changing permissions/ownership of the original container output, verifies individual SHA-256s, and uploads an immutable GitHub Actions artifact.

## Final-head independently verified result

- **Final branch head:** `fe925fe3ae6da4a303e03b064df2d8d66c0eefcc` (documentation-only change after workflow fix).
- **Hosted execution:** [Actions #40457296813](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457296813) — ESP-IDF v6.1 compile **PASS**, four-file SHA check **PASS**, upload **PASS**. Exact checked-out pull-request merge SHA: `ea86af9eb8720e2ce49e70425f9d649219cf288b`. PR head SHA and checked-out SHA are deliberately recorded separately.
- **Host regression:** [Actions #40457296794](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457296794) — **83/83 tests passed on Ubuntu and 83/83 on Windows**; both job logs inspected. All are host/synthetic tests.
- **Downloadable build artifact:** [esp32s3-unflashed-40457296813-1](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457296813/artifacts/12712637366), ID `12712637366`, ZIP size **222,776 bytes**, expires **2026-11-10 05:50:10 UTC** (14-day retention).
- **Downloaded ZIP SHA-256:** `e48e75242239539702924d3b7c430e4a652611b51e5ab7c97ab2e2774cca24a7` — **matched** GitHub's artifact digest. The ZIP was downloaded independently through the GitHub connector, opened with Python `zipfile`, and every file in its embedded `SHA256SUMS.txt` was rehashed and matched. Exactly six expected files were present; unsafe ZIP paths were absent.

| Retained output | Bytes | Independently checked SHA-256 |
|---|---:|---|
| `iot_dual_sensor_capture.bin` | 196080 | `d3eba18a7ec64b1ea46d6f3c6718df35f1d3a2f2edfb20d120661c9f1217ddd5` |
| `bootloader/bootloader.bin` | 21120 | `d45340156bbc81193fc0c4477f53a7ab90ce2d1fc247e13bfed8afb244599f7b` |
| `partition_table/partition-table.bin` | 3072 | `7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820` |
| `flasher_args.json` | 937 | `43c1bb75a3e03982c9732cc7b2f3ff68e3dc5addef324eb1df34e1d293863aa2` |

The generated `flasher_args.json` maps **0x0** to bootloader, **0x8000** to partition table and **0x10000** to application. The ESP-IDF compile log's generated command specifies **2 MB flash size**. **Actual board flash size/configuration remains independently unverified here**; do not blindly apply the CI-generated flashing parameters to an arbitrary ESP32-S3 board. The build did not target a physically verified board revision or prove PSRAM configuration. Before flashing, independently confirm the actual board's flash capacity, flash layout, electrical connections and firmware origin.

## Reproduction and decision

Protocol: [CI firmware bundle v1.2](firmware/espidf_dual_sensor_capture/CI_FIRMWARE_BUNDLE_V12.md). Download the exact artifact before expiry; inspect `BUILD_PROVENANCE.txt` and run `sha256sum --check SHA256SUMS.txt` after extraction. This checks retained bytes and recorded source/run identity, **not** reproducible binary identity across two independent builds, code safety, flashed-device identity or physical data origin.

**Strongest evidence:** an actual ESP-IDF 6.1 build and downloadable, byte-verified, unflashed application + bootloader + partition table + flash-layout package. **Largest gap:** zero genuine sensor samples, no actual flashed binary identity, no independent physical setup review, and board-specific flash configuration not confirmed. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) — confirm board flash size and wiring, locally flash a reviewed binary, preserve flash output and private >=600-second raw dual-sensor capture, verify chain and controlled light change. **Advance** only on independently reviewable physical evidence; **kill/reframe** as software instrumentation if origin/continuity cannot be established.

## Four-lens review

**Hiring manager:** a downloadable reproducibility package is inspectable work, not a simulated screenshot. **Technical reviewer:** source merge SHA, four file hashes, flash offsets, CI failure and package expiry are explicit; physical provenance is absent. **Innovation leader:** this removes a build handoff blocker but does not demonstrate environmental sensing value. **Founder:** no deployment, customer benefit, product readiness, novelty or patentability is established.

No private sensor logs, identities, credentials, employer data, collaborator records or real-world results were committed. No release, merge, stage advancement or collaborator outreach.
