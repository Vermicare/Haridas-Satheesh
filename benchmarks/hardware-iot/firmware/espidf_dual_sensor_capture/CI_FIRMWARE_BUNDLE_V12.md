# ESP32-S3 dual-sensor CI firmware bundle — v1.2 evidence protocol

**Prepared:** 2026-10-27. **Maturity:** Prototype / Hardware Architecture, unchanged. **Physical measurements:** none. **Hardware flash:** not performed. **Artifact round-trip verification:** TBD until the new hosted workflow run and downloaded artifact have been inspected.

## Why this is needed

The prior ESP-IDF 6.1 compile-only job printed an application binary SHA-256 but did **not** retain a downloadable binary. A log hash alone cannot be independently compared against the bytes a later operator might flash. This change preserves a short-lived, **unflashed** build package; it does not establish hardware identity, sensor provenance or a successful flash.

## Build contract and source provenance

Workflow: [iot-espidf-compile.yml](../../../../.github/workflows/iot-espidf-compile.yml). The existing job uses `espressif/esp-idf-ci-action@v1`, requests `espressif/idf:v6.1`, targets `esp32s3` and runs `idf.py build` on the public source. The workflow now requires nonempty files and generates `SHA256SUMS.txt` for:

- `iot_dual_sensor_capture.bin` — application;
- `bootloader/bootloader.bin` — bootloader;
- `partition_table/partition-table.bin` — partition table;
- `flasher_args.json` — generated flash-layout metadata.

The host step copies the container-generated outputs into a runner-writable temporary staging directory, then executes `sha256sum --check SHA256SUMS.txt` **before** upload. No ownership or permission changes are applied to the original build directory. `BUILD_PROVENANCE.txt` records repository, actual checked-out Git commit, event, pull-request head commit (if any), run ID/attempt, requested toolchain, target, and explicit `UNFLASHED_CI_BUILD_ONLY` status. The checked-out commit may be GitHub's pull-request **merge commit**, not the PR head; compare both rather than silently treating them as identical.

The upload uses GitHub Actions' immutable v4 artifact mechanism with **14-day retention**. This is a short-term review artifact, not an archival release, binary reproducibility proof or signed firmware distribution. It contains no credentials by design; any unexpected private data in logs or binaries must be investigated before public distribution.

## Independent check after a successful hosted run

1. Open the exact ESP-IDF workflow run for the PR head; verify its **compile**, **SHA check** and **upload** steps all succeeded. If any fail, preserve the failure and report `artifact=TBD`.
2. Download the `esp32s3-unflashed-<run_id>-<attempt>` artifact from that run. Extract into a new empty directory.
3. In the extracted directory, run `sha256sum --check SHA256SUMS.txt`. **All four files must pass.** On Windows, use an equivalent SHA-256 verifier; do not treat a matching ZIP hash as a substitute for checking individual firmware files.
4. Inspect `BUILD_PROVENANCE.txt` against the run's repository, checked-out commit and PR head; verify `flasher_args.json` references the expected application, bootloader and partition table. Preserve the downloaded artifact's identity and observed digests in a later execution record.
5. Do not call the package flash-tested. A person must independently check the board model, serial port, electrical wiring and flash layout before flashing; preserve the actual flashed-file hashes and console output. No automatic flashing is authorized by this workflow.

**Failure handling:** missing output, wrong source commit, mismatch between declared and observed digest, incomplete artifact, unexpected flash layout, or a failed build **blocks the bundle gate**. Preserve the failed run; do not replace hashes or fabricate a passing package. The prior verified compile-only evidence remains intact.

## Next physical evidence gate

[Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8): flash a separately inspected binary on the actual ESP32-S3, record the exact binary and flash log, then privately preserve >=600 seconds of real BH1750 and SCD40 serial telemetry and a controlled light-change observation. Use the existing host-to-bundle validators and independent wiring review. No CO2 accuracy, thermal benefit, calibration, field reliability or product claim follows from CI alone.

**Decision:** retain maturity. If the artifact cannot be reproduced or matched to the flashed bytes, retain the work as software-build evidence only. No release, deployment or external review has occurred.

## Preserved negative control — root-owned build output (2026-10-27)

[CI run #40456945522](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40456945522) at commit `c8b9df37ebeb774dda791e116545dab4195eb039` **failed** the initial artifact step even though the ESP-IDF compile succeeded. The log printed the application SHA-256 `a5a6b7497ae1f994fbf158c0b3b895cdec2b1b5c43c9f59f9696a63a5ea6d732`, then `SHA256SUMS.txt: Permission denied` when the host runner attempted to write inside the container-created build directory. **No artifact was uploaded in that run.** This is a build-to-artifact handoff failure, not a sensor or firmware compilation failure.

The subsequent workflow fix at commit `55ada26c0109171b4604dfca9f9698969ed9970f` copies the four generated outputs to `RUNNER_TEMP`, a runner-writable directory, before computing/checking SHA-256 and uploading. **Fixed-run execution status: TBD until hosted CI is inspected.** Do not erase or relabel the failed run.
