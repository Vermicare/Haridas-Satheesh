# Hardware/IoT — Host-to-Bundle Chain v0.7 (fictional contract)

**Date:** 2026-10-25 UTC. **Branch:** `research/iot-capture-preflight-20261023` (draft PR #7). **Stage:** Prototype / Hardware Architecture, unchanged. **Physical measurements:** zero.

## Question and prior evidence gap

The host serial logger and telemetry bundle builder were independently tested, but nothing checked that the **same raw serial bytes** flowed from a completed host acquisition into the later CSV/firmware-manifest bundle. Moreover, a 630-second host session with all bytes arriving in its first second could satisfy the earlier host-completion check. Neither case authenticates sensor origin, but both matter for a reviewable capture chain.

## Reproduce (Python 3.13, standard library; no hardware)

From `benchmarks/hardware-iot`:

```sh
python -m unittest -v test_host_bundle_chain_v07.py
python -m unittest discover -v
# After a genuine private acquisition and bundle build:
python host_bundle_chain.py PATH_TO_PRIVATE_HOST_CAPTURE PATH_TO_PRIVATE_DERIVED_BUNDLE
```

For a 30–90-second technical walkthrough, show the two full-integration tests, the short-burst replay rejection, the changed-bundle rejection and the explicit `PROVENANCE_UNVERIFIED` result. All automated examples are fictional, including a fixture whose operator-controlled manifest says `physical`.

## Method / predeclared contract

1. Require a successful independent host integrity check and a successful independent raw→CSV bundle preflight.
2. Require byte-identical nonsymlink raw files in separate host/bundle directories, matching host and bundle SHA-256 declarations.
3. Require **host elapsed >=600 seconds**, **first-to-last byte arrival >=600 seconds**, and **device-monotonic telemetry span >=600,000 ms**. All three are necessary, none sufficient for authentic physical origin.
4. Fail closed for incomplete host capture, failed bundle preflight, altered/rehashed derived bytes, hash mismatch, too-short spans and symlinked raw inputs.
5. Emit `CHAIN_PASS_PROVENANCE_UNVERIFIED`, never physical attestation, firmware-flash attestation or sensor accuracy.

## Execution / results

- Source Git blob: `1f9e95fe49ca94164cf570f74dad1ebf6688ffc2`; test Git blob: `5e3f2a20e6b59b85ace780463278180611b0fc54`.
- Local isolated CPython 3.13.5: **10/10 mocked-chain tests passed**, 2 real-upstream integration tests **skipped** because those repository modules were not installed in the isolated local copy. No claim of local full integration.
- [GitHub Actions #40217485476](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40217485476), test head `1e758c8ea8eed19c3c1f0578fb350241ee2487e4`: **75/75 tests passed on Ubuntu and 75/75 on Windows**, Python 3.13; both job logs inspected. The two new full-integration fictional tests executed successfully on each OS (not skipped).
- Negative control: a fabricated 630-second host manifest with first-to-last byte arrival of **0.5 seconds** is rejected, even with a fictional 600,000-ms device telemetry span. The prior host-only check did not impose this combined condition.
- No actual COM/tty port opened, no BH1750/SCD40 readings captured, no firmware flashed or authenticated.

## Limitations and decision

All timestamps, counters, hashes, serial streams and firmware-file identities remain operator controlled. A coordinated forgery can satisfy the chain. Host byte-arrival duration does not prove physical sampling or timing accuracy. A `physical` declaration in a fictional bundle is not evidence of physical provenance. No security, sensor-performance, novelty, deployment, energy or reliability claim.

**Decision:** Retain Prototype / Hardware Architecture; no release or merge requested. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) — run a genuine ~630-second private ESP32-S3 BH1750/SCD40 capture with device monotonic span >=600 seconds, raw byte hashes, actual flashed-binary provenance, controlled light perturbation, and independent wiring/source review. Preserve any failed session. **Reframe** as capture tooling if authentic provenance and continuous sensor coverage cannot be established.

**Privacy:** Never commit private raw serial logs, network credentials, sensitive device identifiers or location traces. Review before publishing any sanitized physical sample.
