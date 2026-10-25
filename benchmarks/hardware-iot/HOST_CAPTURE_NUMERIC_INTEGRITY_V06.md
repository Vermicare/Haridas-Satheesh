# Hardware/IoT host-capture numeric evidence integrity v0.6 — 2026-10-25

**Evidence boundary:** synthetic, injected-port and malformed-manifest tests only. No actual BH1750/SCD40 data, physical sensor attestation, firmware attestation, device-monotonic coverage or measured performance. Maturity remains **Prototype / Hardware Architecture**; PR #7 is draft/unmerged.

## Hypothesis and reproduced negative result

The v0.5 verifier checks raw byte counts, SHA-256 and declared host capture duration, but Python's default JSON parser accepts `NaN`, `Infinity`, and `-Infinity` as non-standard constants. It also silently converts syntactically valid JSON `1e400` to floating-point infinity. Non-finite values can defeat ordered comparisons, so an internally consistent synthetic raw/manifest bundle may be incorrectly accepted as complete.

A new six-method synthetic regression suite was first committed **without modifying the verifier** at `90e71de073fe7470665d309f5ec8503b0b272780`. [Before-fix GitHub Actions #40169706985](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40169706985) reproduced **six failing assertions/subtests on Ubuntu** (NaN first/last byte offsets, NaN/+Infinity elapsed, NaN in unchecked metadata, and an overflowed JSON exponent). The Windows job was cancelled after the Ubuntu failure; **do not claim a before-fix Windows result**.

## Corrective change and controls

The v0.6 verifier rejects all non-standard JSON numeric constants through `parse_constant`, and rejects JSON floating-point exponent overflow through a finite-only `parse_float`. This applies to the **whole manifest**, including optional metadata, not just required elapsed/offset fields. It leaves byte/hash/status checks and synthetic/physical provenance disclaimers intact.

The six new regression methods include a valid finite synthetic complete capture and a correctly preserved incomplete capture, guarding against over-rejection. [Corrected GitHub Actions #40169745261](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40169745261) passed **63/63 tests on Ubuntu and 63/63 on Windows**, Python 3.13, at code/test commit `878f5e0bc5db417a71d36a13dd3aba5ced1eba49`. The original 57-test suite remains included. No physical hardware was connected.

## Reproduction

From `benchmarks/hardware-iot`:

```bash
python -B -m unittest -v test_host_capture_nonfinite_v06.py
python -B -m unittest discover -p 'test_*.py' -v
```

Source blob SHAs at corrected head: `verify_host_capture.py` = `cc6eeae8c7998893340c3ee43ef4d29ec4955a1d`; `test_host_capture_nonfinite_v06.py` = `87b655f46e643a87e6d8b9dc30697d3bda03e046`. Standard-library-only validator/test. Exact runner images and transitive OS packages: **TBD**. No benchmark latency/energy numbers were measured.

## Decision, limitations and next gate

**Decision: retain Prototype / Hardware Architecture.** This closes a malformed numeric-evidence acceptance gap; it does not authenticate an operator-controlled bundle or protect against a jointly forged raw log and manifest. A Python numeric parser can reject malformed metadata without proving any physical sensor's identity or accuracy. Neither field performance nor device-monotonic coverage is established.

**Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8): acquire a genuine >=600-second BH1750/SCD40 capture with operator-observed light perturbation, real wiring/modes, firmware binary hash, raw serial bytes, separately parsed CSV, and independent gap accounting. **Advance only** with reviewable physical evidence; **reframe** as capture tooling if genuine sensor provenance or continuity cannot be demonstrated.

**Four lenses:** Hiring—visible before/after reproducible failure; Technical—finite-only JSON parsing, still no authenticity; Innovation—reusable evidence-integrity discipline, no novelty claim; Founder—physical validation and instrumentation costs remain TBD.

**Release:** none. No public raw sensor log, employer data, collaborator contact or deployment.
