# ESP32-S3 firmware internal-integrity preflight — 2026-10-27

**Scope:** static inspection of an **unflashed** ESP-IDF v6.1 GitHub Actions firmware artifact. **No physical ESP32-S3 was probed, flashed or measured.** This gate must not be interpreted as hardware authorization.

## Decision-changing gap

The previous `flash_bundle_preflight.py` verified ZIP-member SHA-256 checksums, flash offsets, partitions and only the first ESP image magic byte (`0xE9`). Recomputing the outer `SHA256SUMS.txt` after an accidental or malicious image modification could therefore leave a structurally wrong-chip image, stale embedded digest or stale partition-table MD5 undetected.

The new `firmware_internal_integrity.py` is invoked by the existing preflight and additionally checks:

- Both bootloader and application image headers against **ESP32-S3 chip ID 9**, declared DIO/2 MB/80 MHz flash settings, segment bounds, zero padding, segment XOR checksum and appended image SHA-256.
- Partition-table `0xEBEB` MD5 trailer and no non-erased bytes after the trailer.
- Rejects mismatches even when the outer ZIP-member hashes are regenerated.
- Continues returning `STATIC_PACKAGE_PASS_FLASH_NOT_AUTHORIZED`; physical chip identity, observed flash size, flashed bytes, wiring and sensor capture remain **TBD**.

The 2 MB declared flash size differs from the stated 8 MB specification of the proposed N8R8 board, but the *actual connected board* has not been independently observed. The correct decision is **HOLD**, not an assertion that the package is incompatible.

## Independent local inspection of retained artifact

Artifact: `esp32s3-unflashed-40457717468-1.zip` from [GitHub Actions run 40457717468](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457717468); this is a retained unflashed build, not an attested device image.

- ZIP SHA-256: `0a7b0fa13fb80ea7d63f85d756c1729636ffbfe8bd1cda6ff5fdb0985afdd7f3`
- Bootloader: 3 segments, chip ID 9, 2 MB/DIO/80 MHz; XOR `0x06`; embedded SHA-256 `6cc1a19dbe01ee53021a6dcea15cb994f7441fc0a9d16c345b4d2832362ea898` **matches recomputation**.
- Application: 6 segments, chip ID 9, 2 MB/DIO/80 MHz; XOR `0x28`; embedded SHA-256 `46c80710e86fec257eaf98ba64cda8be1d78eac1ab9e6f36b2085a21956c7800` **matches recomputation**.
- Partition-table MD5 trailer: `f4ad4f4538564b5d7435b62c75b69524` **matches recomputation** over the three 32-byte partition entries.
- Host inspection runtime: CPython 3.13.5, Linux; inspection time 2026-10-27 UTC. These are **local static computations**; the regression suite is a separate evidence claim.

## Independently executed regression evidence

[GitHub Actions run 40483035863](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40483035863) **passed at code commit `e490b42c0ad8bfac14b3f67c023e9d2b3987fe23`**. Both job logs were inspected: **104/104 Ubuntu tests and 104/104 Windows tests passed**, including all seven new internal-image integrity regression tests. This is software-contract verification on synthetic fixtures, **not a physical flash or sensor test**.

## Reproduce

Run the existing command on the **exact retained ZIP**, with the PR head recorded in its `BUILD_PROVENANCE.txt`:

```sh
python benchmarks/hardware-iot/flash_bundle_preflight.py esp32s3-unflashed-40457717468-1.zip --expected-pr-head 9061ed016a359d6ddf2d6b2fc38412f2dc396140
```

The auditor must report `STATIC_PACKAGE_PASS_FLASH_NOT_AUTHORIZED` and an `internal_image_integrity` section. Do not pass a guessed `--observed-flash-mb`; only a read-only physical-device probe can populate it.

Adversarial regression cases mutate the chip ID, flash-size nibble, embedded SHA-256, partition entry, segment data and hash-appended flag, then recompute outer member hashes. The original synthetic tests are preserved. No test fixture is executable firmware.

## Primary specifications

- [Espressif esptool ESP32-S3 firmware image format](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/firmware-image-format.html) — header, extended chip ID, segments, XOR and appended SHA-256.
- [Espressif ESP-IDF partition tables](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/partition-tables.html) — partition MD5 integrity trailer.
- [Espressif esptool basic commands](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/basic-commands.html) — chip compatibility checks and read-only `flash_id` command.

## Evidence and stop/advance rule

**Static validation is not cryptographic provenance attestation:** an attacker controlling the entire artifact and manifest can replace both data and hashes. The retained ZIP digest must be compared with the trusted GitHub artifact digest separately. This checker does not verify secure boot, physical flash, power stability, board revision, sensor timing or calibration.

**Next:** independently identify the actual ESP32-S3 and flash capacity using read-only commands, then review configuration before any write. After operator approval and safe wiring review, capture >=600 seconds of raw BH1750/SCD40 telemetry with an external reviewer. Do not advance maturity or release firmware on static checks alone.
