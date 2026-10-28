# Hardware/IoT v1.6 — same-checkout ESP32-S3 firmware rebuild falsification (2026-10-28)

**Stage:** Prototype / Hardware Architecture, unchanged. **Physical flash or sensor measurements:** none. **Question:** do two independent hosted compilations of the exact same checkout produce byte-identical *unflashed* firmware?

## Preregistered comparison / provenance

A completed [GitHub Actions firmware build #40457717468](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457717468) was deliberately rerun as **attempt 2** without changing source or workflow. Both attempts succeeded, passed their embedded SHA256SUMS checks and uploaded downloadable ZIPs. The two ZIPs were independently downloaded and rehashed using Python's standard library, and each internal four-file manifest was independently checked. The source identity was not inferred from the branch name:

- Both retained BUILD_PROVENANCE files: **checked-out pull-request merge SHA** `b26cc0cc12eba8317bb7f97fa202b7356f221349`; **PR head SHA** `9061ed016a359d6ddf2d6b2fc38412f2dc396140`; same run ID `40457717468`.
- [Attempt 1 artifact #12713162757](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457717468/artifacts/12713162757), 2026-10-27 05:54 UTC, ZIP SHA-256 `0a7b0fa13fb80ea7d63f85d756c1729636ffbfe8bd1cda6ff5fdb0985afdd7f3`, expires 2026-11-10.
- [Attempt 2 artifact #12800162656](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457717468/artifacts/12800162656), 2026-10-28 07:47 UTC, ZIP SHA-256 `e99e7eee7bf2a3c7dac2b4f0e5914f6eee687538b7d82b93fa954534b16bddb2`, expires 2026-11-11.
- ESP-IDF requested **v6.1** in the workflow; ESP32-S3 target; official CI container; both attempts show embedded application version `b26cc0c`. Actual container image digest/compiler toolchain pinning **TBD**. No hardware connected.

## Observed binary comparison (same source checkout)

| Retained member | Attempt 1 SHA-256 | Attempt 2 SHA-256 | Byte comparison |
|---|---|---|---|
| Application, 196080 bytes | `a1b031bc4413f320f0e33113868e4ee03e102df2298a141509f08c30c26b6046` | `80cb6e803154525e26a79b0acaf5bcf6fdefb8c5cf3c55de08d5d380e2129454` | **70 bytes differ**, six disjoint ranges |
| Bootloader, 21120 bytes | `05e50692dd1dcb14f402eb2f080981bcc812d51f3da235fe87bf97a3662e02d9` | `df6a233f7960762afb5b19b8620f6981dbcd637dd2bb7230351197943c5f0ea1` | **39 bytes differ**, five disjoint ranges |
| Partition table, 3072 bytes | `7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820` | same | **Identical** |
| Flash arguments, 937 bytes | `43c1bb75a3e03982c9732cc7b2f3ff68e3dc5addef324eb1df34e1d293863aa2` | same | **Identical** |

**Negative result:** even under identical checked-out source and workflow run ID, **application and bootloader images are not byte reproducible**. The differing binary regions include directly observable ASCII build timestamps: application `05:53:56 / Oct 27 2026` versus `07:46:55 / Oct 28 2026`; bootloader `Oct 27 2026 05:53:28` versus `Oct 28 2026 07:46:10`. Additional changed regions include 32-byte application descriptor digest and end-of-image digest/checksum regions. These observations strongly implicate embedded compile timestamps; a complete causal proof requires a controlled configuration experiment.

**Important correction to earlier uncertainty:** the two *different-checkout* build hashes were previously not comparable as a same-revision reproducibility test. This new controlled rerun resolves that ambiguity: actual **same-checkout binary mismatch** is demonstrated. The version field from the earlier different-checkout runs also changed with the pull-request merge SHA, so differing source refs remain a separate confounder.

## Reproduce and falsify

Download both named ZIP artifacts **before expiry**; keep them outside the repository. From this directory run:

```bash
python compare_firmware_rebuild_v16.py /private/attempt1.zip /private/attempt2.zip > comparison.json
python -m unittest -v test_compare_firmware_rebuild_v16.py
```

The comparison script rejects altered SHA256SUMS, duplicate/unexpected ZIP members, different checkout/run provenance, and identical attempt IDs. It emits only SHA-256, byte-count, differing-offset ranges and non-identifying run metadata. **Five synthetic negative/positive contract tests passed locally on CPython 3.13/Linux**; hosted CI for this newly published script is **TBD** until executed. Original downloaded ZIPs remain outside Git.

## Decision / next experiment

**Do not claim reproducible firmware bytes** or substitute one attempt's hashes for the other. Preserve run-specific build provenance. The next experiment is a separate, versioned **same-checkout** two-build control that disables embedded compile timestamps (and explicitly freezes project version), records exact toolchain/container image digest, then compares application, bootloader and partition bytes again. A byte match would establish only this controlled build environment, **not physical device identity or sensor authenticity**. If mismatch persists, localize further differing bytes and preserve failure. The physical gate remains [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8): read-only board flash ID and genuine ≥600-second BH1750/SCD40 capture after independent wiring/firmware review. CI's 2 MB flash declaration must not be blindly flashed onto the nominal 8 MB board.

**Primary source:** [Espressif ESP-IDF v6.1 application image format](https://documentation.espressif.com/projects/esp-idf/en/v6.1/esp32/api-reference/system/app_image_format.html) describes the embedded application description including compile time/date and ELF digest. No novelty, patentability, deployment, safety, accuracy, power or efficacy claim.

**Four-lens review:** hiring manager — independently inspectable failure record; technical reviewer — same-checkout comparison with exact hashes and timestamp offsets; innovation leader — reproducible-build control is a prerequisite, not novel sensor technology; founder — zero validated physical value, users or deployment.
