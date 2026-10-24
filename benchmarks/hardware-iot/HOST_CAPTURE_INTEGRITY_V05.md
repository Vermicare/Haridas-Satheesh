# Hardware/IoT host serial capture integrity v0.5 — 2026-10-25

**Boundary:** synthetic/injected-port software verification only. **No physical BH1750 or SCD40 capture, no firmware attestation, no real sensor measurements.** Maturity stays **Prototype / Hardware Architecture**. Draft PR #7 remains unmerged.

## Question and identified gap
The v0.4 host acquisition utility writes `raw_serial.log` and `capture_manifest.json`, but its own successful return does not independently check the bytes later handed to a reviewer. A post-capture edit, truncation, status swap, or malformed manifest could be overlooked. This is an evidence-package integrity gap, not a demonstrated attack on physical hardware.

## Added executable contract
- `verify_host_capture.py` independently rereads raw bytes and manifest, checks byte count and SHA-256, and rejects mismatched file/status pairings, duplicate JSON keys, symlinked evidence files, false complete/empty captures, insufficient host duration, and inconsistent first/last byte offsets.
- A correctly preserved **failed** acquisition is reported as `INCOMPLETE_CAPTURE_PRESERVED`, not success.
- A complete capture is labeled `INTEGRITY_PASS_PROVENANCE_UNVERIFIED`. This label explicitly does **not** authenticate the ESP32, sensors, firmware, timestamps, origin, or a >=600-second device-monotonic span.
- The validator can be fooled if an adversary modifies **both** the raw bytes and all matching manifest fields. It does not use signatures, trusted time, secure boot, or external witnesses.

## Reproduce from `benchmarks/hardware-iot`
```bash
python -B -m unittest -v test_serial_acquire.py test_verify_host_capture.py
python verify_host_capture.py /path/to/actual_private_capture_directory
```
The second command is **not** executed here; no actual physical capture directory was available. It exits 2 on integrity failure. Do not publish raw serial data without checking for credentials, identifiers and private information.

## Recorded evidence
- Baseline v0.4 Git blob SHAs (read from PR #7 and checked against local package): `serial_acquire.py` = `3088ea54c4dda40ee7e8849bf688b846dce8c2b2`; `test_serial_acquire.py` = `42606fb3863dacaf13cf3da31b38d2b04a25a321`.
- New Git blob SHAs: `verify_host_capture.py` = `c8b1b2a94f5c834a7941d8b0952b9a5619acbcd0`; `test_verify_host_capture.py` = `11fb995eee14985b85ccc6f7eb17ceaed37f1e0e`.
- Local environment: CPython 3.13.5, Linux, GCC 14.2.0; standard library only; no serial device.
- Two separate local process executions: **21/21 passed each** (11 existing v0.4 tests + 10 new adversarial/positive tests).
- Cross-platform CI: **TBD until the exact final commit is verified in GitHub Actions**.
- Actual physical capture: **TBD**; measurement accuracy: **TBD**; device-monotonic continuity: **TBD**.
- No claim of before-fix acceptance by a prior independent verifier: **no prior verifier existed**.

## Failure/learning
Hashing during acquisition is not the same as independently checking a later evidence package. An internally consistent, operator-controlled manifest is not cryptographic device attestation. Host-monotonic capture duration is not device-monotonic sensor coverage.

## Next evidence gate
Follow [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8): capture a genuine >=600-second ESP32-S3/BH1750/SCD40 session with raw serial, firmware binary SHA-256, actual wiring/sensor mode and operator-observed light perturbation. Independently check both the host bundle and the separately extracted device-monotonic sensor CSV, and retain all failures/gaps. **Do not advance maturity until physical evidence and independent review exist.**

## Four-lens decision
Hiring: reproducible engineering guard, not field deployment. Technical: independent bytes/manifest check, not authenticity or TOCTOU protection. Innovation: reusable provenance boundary, not novelty/patentability. Founder: physical instrumentation and operator/reviewer costs remain unmeasured.
