# Hardware/IoT v2.0 — path-alias regression in host-capture review (2026-10-30)

**Maturity:** Prototype / Hardware Architecture, unchanged. **Physical captures:** zero. **Inputs:** entirely fictional fixture. **No flash, sensor, calibration, physical-time, reliability, product, or novelty evidence.**

## Reproduced negative control

The unchanged [v1.8 capture-chain checker](capture_chain_v18.py) reads host and bundle raw files using `Path.read_bytes()` without rejecting symlink aliases. The [v1.9 byte-exposure review](host_byte_exposure_gate_v19.py) delegates to v1.8 and also does not check file aliases. In a fictional complete 610.1-second fixture, replacing the bundle's `raw_serial.log` with a symlink pointing to the host's `raw_serial.log` produces:

- **Original v1.8:** `HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD`.
- **Original v1.9:** `HOST_BYTE_SPAN_CONSISTENT_ORIGIN_UNVERIFIED`.
- **Additive v2.0:** `REVIEW_REQUIRED` for a symlink input.

The result demonstrates an **integration evidence-chain alias gap**, not an actual tampering incident. Hash equality does not establish two independently retained files when both names can resolve to the same mutable target. A pre-read size check is also missing from v1.8; its maximum is applied only after reading raw bytes. This experiment does **not** claim exploitation, malicious access, or a real-world device defect.

**Important preexisting protection:** [v0.7 host_bundle_chain.py](https://github.com/Vermicare/Haridas-Satheesh/blob/research/iot-capture-preflight-20261023/benchmarks/hardware-iot/host_bundle_chain.py) already rejects symlinked raw inputs and directory aliases and separately requires >=600 seconds of host byte exposure and >=600,000 ms of device telemetry. The v2.0 supplemental gate is **not a replacement for v0.7**.

## Additive review gate and scope

[host_path_alias_gate_v20.py](host_path_alias_gate_v20.py) checks that capture/bundle directories are distinct, existing, nonsymlink directories; that five required inputs are regular nonsymlink files; and that their declared size ceilings are met **before** calling the unchanged v1.9 reviewer. [Nine fictional tests](test_host_path_alias_gate_v20.py) cover a positive structural case, original-v1.8/v1.9 symlink acceptance, symlinked manifest/directory, oversized manifest, same-directory alias, missing CSV, inherited v1.9 burst rejection and raw tampering.

This is a **best-effort preflight**, not race-free path or inode attestation. A malicious local actor could swap paths between preflight and read (time-of-check/time-of-use). Parent-directory symlinks, special mounts, coordinated forgery and trustworthy clocks are not authenticated. Do not use it as a security boundary for untrusted filesystem actors. Retain private raw logs outside Git and review source permissions.

## Reproducibility and provenance

- Repository: `Vermicare/Haridas-Satheesh`, branch `research/iot-host-chain-v18-20261029`.
- Code-bearing head: `28e75049ce27beb455b664737c84625df70bea97`.
- Original v1.8 source blob: `e94bc84f75afc2942ab30f480eb82e42577db472` (**unchanged**).
- Original v1.9 source blob: `2087b3fd70edfc6bb0cfd67bd8bb981eacdd7340` (**unchanged**).
- Additive v2.0 source blob: `549be15d9c66e0630feefa52d36722e7cbcb638a`.
- Additive v2.0 test blob: `c7c96170c4350bb06ae7b92d8dcf21e7ffcf78c0`.
- [Hosted full IoT preflight #41042153165](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41042153165): **153/153 tests passed on Ubuntu and 153/153 on Windows**, including all nine v2.0 tests on each, with job logs inspected. Neither operating system skipped symlink tests.
- [Original host-chain workflow #41042153219](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41042153219): **14/14 tests passed on Ubuntu and 14/14 on Windows**.
- Python matrix: `3.13`; exact patch, runner image digest and physical provenance: **TBD**.

From `benchmarks/hardware-iot` on the stated branch:

```bash
python -B -m unittest -v test_capture_chain_v18 test_host_byte_exposure_gate_v19 test_host_path_alias_gate_v20
python host_path_alias_gate_v20.py PRIVATE_HOST_CAPTURE_DIR PRIVATE_BUNDLE_DIR
python host_bundle_chain.py PRIVATE_HOST_CAPTURE_DIR PRIVATE_BUNDLE_DIR
python serial_bundle.py verify PRIVATE_BUNDLE_DIR
```

## Decision and four-lens review

**Decision:** No maturity advancement. **Strongest evidence:** reproducible cross-platform fictional alias negative control and retained v0.7 stronger chain. **Largest gap:** no genuine independently inspected >=600-second BH1750/SCD40 raw capture or verified flashed-firmware identity. **Next decisive experiment:** capture private physical telemetry with actual board flash-ID, fixed wiring, independent raw/firmware review and a controlled BH1750 light perturbation; run v0.7, v1.8, v1.9, v2.0 and serial bundle verification on the same raw bytes. **Stop/reframe:** any alias, insufficient exposure, device span or provenance gap prevents physical validation claims.

**Hiring manager:** regression tests defend integration assumptions. **Technical reviewer:** exact unchanged baseline blobs, adversarial fixtures and limitations. **Innovation leader:** no novelty/patentability assertion. **Founder:** no product performance, reliability, customer or commercial evidence. No employer or personal telemetry is published.
