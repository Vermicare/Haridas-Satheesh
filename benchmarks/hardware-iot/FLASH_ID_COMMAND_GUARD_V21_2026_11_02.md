# Hardware/IoT v2.1 — declared read-only flash-ID command guard

**Date:** 2026-11-02 (Asia/Kolkata). **Stage:** Prototype / Hardware Architecture, unchanged. **Evidence class:** synthetic software contract only; **no physical probe, flash, PSRAM detection or sensor capture**.

## Decision-changing gap

The existing [v1.5 transcript parser](read_only_flash_probe_v15.py) checks claimed chip family and flash capacity, but cannot distinguish whether a pasted transcript came from a read-only `flash-id` invocation or a command that writes or erases flash. This new **offline, non-executing** guard rejects operator-declared commands outside a narrow read-only grammar, rejects output containing common write/erase signatures, and fails closed if the declared candidate image size disagrees with the transcript. This is **not** evidence of the command actually executed; a malicious or mistaken operator can still supply edited text.

Espressif documents `flash_id` in esptool v4 and `flash-id` in current versions, separately from `write_flash`/`write-flash` and erase commands. See [v4 ESP32-S3 basic commands](https://docs.espressif.com/projects/esptool/en/release-v4/esp32s3/esptool/basic-commands.html) and [current ESP32-S3 esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/).

## Reproduce without hardware

From `benchmarks/hardware-iot`:

```sh
python -B -m unittest -v test_flash_id_command_guard_v21.py
python -B -m unittest discover -v
```

The command-line interface accepts three positional arguments: a **private** UTF-8 text file containing the exact operator-declared command, a **private** UTF-8 esptool output transcript, and the **explicit** nominal candidate-image flash size in megabytes:

```sh
python flash_id_command_guard_v21.py PRIVATE_DECLARED_COMMAND.txt PRIVATE_TRANSCRIPT.txt 8
```

It does **not** run the command, open a port, or modify hardware. Accepted examples of **declared command syntax only** include `python -m esptool --chip esp32s3 -p COM7 flash-id` (v5) and `esptool.py --chip esp32s3 -p COM7 flash_id` (v4). These examples are **not records of a physical execution**. The command parser deliberately rejects shell metacharacters, remote ports, response files, unknown options, missing or duplicate chip/port declarations, other subcommands, and inconsistent image sizes. It does not emit the private port, transcript, or device MAC. A successful parse still sets `flash_authorized=false`, `physical_device_attested=false`, `actual_command_proven=false` and physical PSRAM/sensor status `TBD`.

## Test provenance

- Source: `flash_id_command_guard_v21.py`, Git blob `1bd5cd5507fca4d710473847d8a598d1b99ab837`.
- Tests: `test_flash_id_command_guard_v21.py`, Git blob `09353f6843d09dc0b350414fc084a0b387df228f`.
- Original transcript parser: `read_only_flash_probe_v15.py`, Git blob `5b49859032727fb211fa82a65f6461f95886b209` (unchanged).
- Local pre-integration run: 6/6 tests passed on the development Python runtime with the v1.5 parser mocked; the final seventh test requires the actual repository v1.5 parser and is exercised by hosted repository discovery.
- Hosted cross-platform regression: [GitHub Actions #41348128909](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41348128909), tested source head `7bb7a0f97e12e830598ff39bb53b68e9816c5ac7`, completed **SUCCESS**. Both original logs independently inspected: **137/137 repository tests passed on Ubuntu/Python 3.13 and 137/137 on Windows/Python 3.13**, including **7/7 new tests per operating system** and the real v1.5 integration. These are fictional contract tests, not physical measurements.
- Synthetic controls: 4 accepted v4/v5 command declarations; 19 unsafe/ambiguous command declarations rejected; 6 mutation-output signatures rejected; explicit candidate-size mismatch rejected; real v1.5 parser integration tested in hosted CI; private input non-disclosure checked.

## Largest gap and next experiment

The existing [v2.0 effective-config report](EFFECTIVE_CONFIG_V20_2026_11_01.md) observes `CONFIG_SPIRAM` **not set** in the reproducible **unflashed** ESP32-S3 software build. Physical flash capacity, PSRAM identity/mode, actual command execution, exact flashed firmware and ≥600-second BH1750/SCD40 capture remain **TBD**. The next evidence-producing action is a genuine, privately preserved, independently reviewed **read-only** flash-ID transcript with the actual command, tool version and board/port provenance. Then compare with the existing backed-up firmware, and only after separate hardware review consider a sensor logger session. Do **not** flash based on this parser or the nominal N8R8 ordering label.

**Stop/reframe:** any transcript suggesting a write/erase operation, missing provenance, mismatch with candidate image, or unverified PSRAM requirement blocks physical integration. A syntactically accepted operator declaration is never a device attestation. No maturity advancement, external validation, merge, release, deployment, novelty, performance or commercial claim.

**Four lenses:** hiring manager—defensible fail-closed software evidence; technical reviewer—explicit threat model and adversarial tests; innovation leader—no novelty asserted; founder—physical validation and field reliability remain absent.
