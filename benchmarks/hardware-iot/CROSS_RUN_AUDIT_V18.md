# Hardware/IoT v1.8 — independent offline cross-run artifact audit

**Date:** 2026-10-29. **Maturity:** Prototype / Hardware Architecture, unchanged. **Result:** PASS for retained *unflashed* binary equality only; no physical device, flashing, measurements or hosted v1.8 test run.

## Decision-changing question

Do the two previously reported v1.7 hosted runs actually retain byte-identical firmware/layout outputs, despite differing PR merge checkouts? This v1.8 audit independently downloads both still-available GitHub Actions ZIPs, checks the ZIP SHA-256 against GitHub artifact metadata, verifies all eight internal SHA256SUMS entries, requires both within-run builds and cross-run bytes to match, and compares declared ESP-IDF/compiler/effective-config metadata. It never treats a matching binary as proof of source equivalence or hardware provenance.

## Inputs and verified local execution

- [First run #40659292470](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659292470), [artifact #12802833314](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40659292470/artifacts/12802833314): ZIP SHA-256 `f658976e6a846f1fdc73888ad3872f70e53fdf395d7ae1bee283308a4549c6d0`; checkout merge `8d440e64331a03788379d30b8270ad964933dfa3`.
- [Second run #40660083184](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40660083184), [artifact #12803990362](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40660083184/artifacts/12803990362): ZIP SHA-256 `d1471fdb8de9b12c1777f73701283a9af4b68f6c6330c346cdee2c294a0aa4ce`; checkout merge `21236c8fe227a07f39425a0165027256d184a7c3`.
- Downloaded both ZIPs again through the connected GitHub artifact endpoint on 2026-10-29. Independently computed both ZIP SHA-256 values, inspected all 14 members per ZIP, verified every SHA256SUMS entry and independently compared all four first/second pairs **within each ZIP** and **across both ZIPs**.
- Executed `python -B -m unittest -v test_audit_cross_run_v18.py` on local CPython **3.13.5 / Linux**: **11/11 fictional tests passed (one positive control, ten negative controls)** after correcting two test assertion-message expectations. This initial test-harness failure was not a binary mismatch. **Hosted Windows/Ubuntu v1.8 tests: TBD.**
- Executed `python -B audit_cross_run_v18.py first.zip second.zip --output result.json` locally: **PASS_STATIC_UNFLASHED_BINARY_EQUALITY_SOURCE_REVIEW_REQUIRED**. Aggregate-only hashes and run conditions are in [registry](CROSS_RUN_AUDIT_V18_REGISTRY.json); no ZIPs or device identifiers are committed.

| Retained member | Bytes per build | Verified SHA-256 (all four copies) |
|---|---:|---|
| Application | 196000 | `3acc2c98ea480f15dbeaffa8d49c8812427dba73c69511e7bcc5a928e10d73f1` |
| Bootloader | 21072 | `da59a63758341ef54ff0083f178ea1f29ed7bc9cf89a8c7f64e9b0d2d9a9184b` |
| Partition table | 3072 | `7f00b6c042a89b15b0cac534f82ed988caf29278ff5700b0c511eb1b5bb7c820` |
| Flash arguments | 937 | `43c1bb75a3e03982c9732cc7b2f3ff68e3dc5addef324eb1df34e1d293863aa2` |

Both ZIPs declare ESP-IDF v6.1, xtensa-esp-elf-gcc 15.2.0, and effective sdkconfig SHA-256 `45c2865ae1ae348a2ad1696136f783aa94afc11264152981056519ceeaf75816`.

The GitHub [source-head comparison](https://github.com/Vermicare/Haridas-Satheesh/compare/5a9009d7d9ef2d2d2d500aad4a50c5c596e780c5...5fe82887ff5286c55d518b254eea6390bc45b5ff) was independently checked this run and shows only **two documentation/registry files** changed between the source heads. The ZIPs alone do **not** establish that; the PR merge checkouts differ. The container digest is also **not embedded in the ZIPs**: previous log evidence recorded a shared digest, but this offline experiment does not reattest it.

## Reproduce / negative controls

Download the two ZIPs from the linked GitHub Actions artifacts while available, verify their archive digests, then from this directory run:

```sh
python -B -m unittest -v test_audit_cross_run_v18.py
python -B audit_cross_run_v18.py /path/to/first.zip /path/to/second.zip --output /path/to/private-or-aggregate-result.json
```

The executable rejects malformed or duplicate members, mismatched checksums, same-checkout-as-independent-run substitution, rehashed changed binaries, changed compiler/config, mismatched within-run pairs, reported build failures and corrupted ZIPs. All test fixtures are fictional. Output includes only hashes, sizes and declared build metadata.

**Retention warning:** GitHub reports first artifact expiry **2026-11-11 08:51:38 UTC** and second expiry **2026-11-11 08:58:06 UTC**. Durable independent archival or re-execution is needed before links expire; do not confuse retained hashes with retained bytes.

## Four-lens decision and next gate

Hiring manager: a verifiable, bounded reproducibility check. Technical reviewer: bytes are independently compared; source equivalence, image pinning and physical identity are separate evidence layers. Innovation leader: no novelty claim. Founder: no user, device or commercial outcome.

**No stage advancement.** Strongest evidence is two hosted runs with four identical retained unflashed member pairs, now independently rechecked by executable code. **Largest gap:** independently pinned toolchain/host plus physical flash identity and real dual-sensor capture. **Next decisive experiment:** preserve expiring artifacts, pin immutable image digest, repeat on a separately provisioned runner, then inspect physical board flash configuration and record genuine >=600-second BH1750/SCD40 raw serial with independent review. **Reframe/stop:** if cross-environment binaries diverge, require run-specific artifact identity; if physical provenance cannot be established, retain only software tooling claims. No flash authorized.
