# Hardware/IoT — Manifest parser ambiguity gate v0.8

**Date:** 2026-10-26 IST. **Stage:** Prototype / Hardware Architecture (unchanged). **Data:** fabricated regression fixtures only; zero physical sensor captures.

## Evidence question
Can a capture manifest with conflicting keys or nonfinite numeric values be accepted as structurally valid when the actual raw/CSV hashes match?

**Before-fix negative control:** commit `f430e3262f1d30d94500ba0715b780fccb7cac6e`, [GitHub Actions #40245700265](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40245700265), Ubuntu Python 3.13: **4 of 80 tests failed** because invalid fictional manifests returned `STRUCTURAL_PASS_PROVENANCE_UNVERIFIED`. Windows was cancelled, not counted as a failure or pass.

The four fail-open cases were: conflicting top-level `capture_origin` declarations, conflicting nested SCD40 sensor modes, nonstandard JSON `NaN` in an otherwise unused metadata field, and syntactically valid JSON number `1e400` overflowing to infinity. A fifth positive control with finite `1e3` remained accepted.

## Correction and reproducibility
- Fixed `capture_preflight.py` with recursive duplicate-key rejection (`object_pairs_hook`), nonstandard-constant rejection (`parse_constant`), and finite-number enforcement (`parse_float`).
- Preserved raw-data schema, threshold definitions, source hashing, original host-capture tests and physical provenance limitations.
- Corrected executable commit: `04d029e6b897a5ac4df53904f409294306b6863f`.
- Source Git blob: `ca1a179bdd2287aec21d55dd2b91a1144e0f959b`; regression-test blob: `a724490f0a8d96c072b8630172be514f3608967f`.
- [GitHub Actions #40245744561](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40245744561): **80/80 passed on Ubuntu and 80/80 on Windows**, Python 3.13. Both job logs inspected.
- Exact command from `benchmarks/hardware-iot`: `python -m unittest discover -v`. No external sensor, serial port, firmware flash or independent physical attestation was used.

## 60-second demonstration
1. Show before-fix CI: four invalid fictional manifests wrongly accepted.
2. Show new adversarial tests and the strict JSON parser hooks.
3. Show both OS jobs passing 80/80 after the fix.
4. End with `STRUCTURAL_PASS_PROVENANCE_UNVERIFIED`: neither a checksum nor an operator-declared origin authenticates a physical BH1750/SCD40 reading.

## Four-lens review
- **Hiring manager:** reproducible failure → regression → repair with cross-platform CI, not a shipped hardware product.
- **Technical reviewer:** verify duplicate-key rejection applies to nested objects, that overflowed JSON numerics are rejected, and that valid finite values still parse.
- **Innovation leader:** reusable evidence-boundary principle across sensor and decision systems; no novelty claim.
- **Founder:** physical instrumentation, firmware identity, data quality and independent review remain unmeasured; do not infer customer or safety value.

## Decision and next experiment
**Decision:** retain draft, no release or maturity advance. Existing [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) is still the highest-value evidence gate: independently inspectable >=600-second real ESP32-S3 BH1750/SCD40 capture, host and device timing, raw hashes, firmware/wiring review and controlled light perturbation. Preserve failed runs and protect credentials.

**Kill/reframe:** if sensor provenance or continuous physical logging cannot be established, present the tooling as a synthetic capture-integrity preflight rather than a hardware benchmark. Sensor accuracy, real-world uptime, physical-origin proof and performance: **TBD**.

## Primary standard and design consequence

[IETF RFC 8259, §4 and §6](https://datatracker.ietf.org/doc/html/rfc8259) says JSON object member names **SHOULD** be unique because duplicate handling differs across implementations; it prohibits `NaN` and `Infinity`, and allows implementations to limit numeric range. Thus the fail-closed policy is a deliberate capture-evidence interoperability rule, not a claim that every duplicate-name JSON text is universally invalid syntax. The exponent `1e400` is syntactically a JSON number, but this Python float conversion overflows and is rejected for a finite-only evidence manifest.
