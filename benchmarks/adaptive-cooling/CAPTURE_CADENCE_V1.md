# Adaptive Cooling — declared capture cadence consistency v1 (2026-10-27)

**Evidence class:** fictional-only software integrity regression. **Physical instrument data: TBD.** This is not proof of logger authenticity, sensor sampling frequency, cooling effect, energy savings, thermal comfort, or safety. **Stage remains Prototype / Documented R&D.**

## Specific negative control

The existing CSV integrity gate allows any gap up to 60 seconds. The capture manifest separately declares `sample_interval_s`, but the previous cross-artifact alignment check never compared this declared cadence with consecutive CSV timestamps. Thus an internally coherent 11-row fictional 10-minute CSV with **60-second actual intervals** could pass while the manifest falsely declares **5-second nominal intervals**. Both CSV and manifest can be correctly hashed; hashes do not establish truthful cadence.

## Candidate correction

`capture_alignment.py` now rejects `DECLARED_CADENCE_MISMATCH` if any consecutive observed timestamp gap is outside **0.5–1.5 times the manifest's declared nominal interval**, with a 1-microsecond arithmetic slack. The tolerance is a deliberately provisional, wide *review threshold*, not a measurement of instrument jitter, clock drift, sensor timing, or compliance with any standard. It is not a replacement for the independent maximum-gap and energy-integrity gates.

Four new **fictional** regression cases in `test_capture_alignment.py` cover a correctly declared 5-second series, sparse 60-second rows misdeclared as 5-second samples, oversampled 20-second rows misdeclared as 60-second samples, and one omitted 5-second sample producing a 10-second gap. All fixture energy counters are calculated consistently with the fictional 60 W signal to isolate the cadence discrepancy.

## Reproduce

From `benchmarks/adaptive-cooling` on the research branch:

```bash
python -B -m unittest -v test_fixture_origin_gate.py test_dry_run_integrity.py test_capture_chain.py test_capture_alignment.py
```

For a private physical bundle after independent capture and preservation:

```bash
python capture_alignment.py --bundle /path/to/private/capture --expected-manifest-sha256 <independently_preserved_sha256>
```

Preserve the original logger bytes, manifest, conversion command, hashes, instrument identities and any failure. Do **not** change declared cadence after observing failures to force a passing result. A logger with legitimate event-driven sampling, variable cadence, clock corrections, batching or packet loss may fail this fixed-cadence contract; investigate and document a separate preregistered acquisition model rather than silently weakening the threshold.

## Research decision

This improves *internal consistency checking only*. It cannot establish that original logger bytes generated the CSV, that timestamps came from hardware, or that a physical prototype works. The high-value next experiment is still [Issue #15](https://github.com/Vermicare/Haridas-Satheesh/issues/15): instrument inventory and calibration/uncertainty, original >=10-minute physical logger capture, reproducible conversion and independent inspection, then preregistered repeated ambient → fan-only → prototype comparisons including external energy and heat rejection.

**Hosted verification:** [GitHub Actions #40462666047](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40462666047) completed successfully at code/test commit `2f87a09c1835af1377a66c52693545f341b152d4`. **79/79 fictional-only tests passed on Ubuntu and 79/79 on Windows**, including all four new cadence controls. Both raw job logs were inspected. Later commits only add documentation/registry; this does not establish physical sampling or performance.
