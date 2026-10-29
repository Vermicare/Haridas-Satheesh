# Hardware/IoT v1.9 — host byte-exposure regression against v1.8 (2026-10-30)

**Stage:** Prototype / Hardware Architecture; unchanged. **Hardware captures:** 0 in this experiment. **All test data fictional.** Research-branch contribution; no flash, deployment, release or claim of real sensor performance.

## Decision-changing negative control

The original [v0.7 host-to-bundle chain](https://github.com/Vermicare/Haridas-Satheesh/blob/research/iot-capture-preflight-20261023/benchmarks/hardware-iot/host_bundle_chain.py) requires both host elapsed time **and first-to-last byte arrival** to span at least 600 seconds, as well as a separate 600,000-ms device-monotonic telemetry span. The newer [v1.8 host capture checker](capture_chain_v18.py) checks 600-second *host elapsed* and offset ordering, but **does not require first-to-last host byte arrival to span 600 seconds**. Its documented follow-up, `serial_bundle.py verify`, checks device telemetry but cannot reconstruct host byte arrival timing.

An independently executed **fictional** fixture with a declared 610.1-second host session and host byte offsets **0.2 to 0.3 seconds** passed the exact unchanged v1.8 code (`HOST_CHAIN_INTEGRITY_PASS_SENSOR_VALIDITY_TBD`). A second fictional late burst (609.7–609.9 seconds) also passed v1.8. Thus **v1.8 + bundle verification is not a safe replacement for the stronger v0.7 chain**. This does not invalidate v0.7 or establish an actual sensor failure; it is an integration/documentation regression risk.

## Supplemental, read-only safeguard

[host_byte_exposure_gate_v19.py](host_byte_exposure_gate_v19.py) preserves v1.8 and adds a provisional/reused **600-second first-to-last host byte-exposure check**, returning `REVIEW_REQUIRED` on a short burst. [Six fictional regression tests](test_host_byte_exposure_gate_v19.py) cover early/late bursts, the exact threshold, just-below threshold, hash tampering and a structurally valid but unauthenticated fixture. The original 14 v1.8 tests remain unchanged.

**Local verification:** CPython 3.13.5/Linux; two independent process invocations each passed **20/20** tests (14 original + 6 new). Exact Git blob identities: v1.8 source `e94bc84f75afc2942ab30f480eb82e42577db472`; original tests `7063789ed300f35c71efd2303094695b0b367c1e`; new gate `2087b3fd70edfc6bb0cfd67bd8bb981eacdd7340`; new tests `0de623871a03833785a9b3fe778be86d09deb429`. Hosted verification: **TBD until final-head job logs are inspected**.

Reproduce from `benchmarks/hardware-iot`:

```bash
python -B -m unittest -v test_capture_chain_v18 test_host_byte_exposure_gate_v19
python host_byte_exposure_gate_v19.py PRIVATE_HOST_CAPTURE_DIR PRIVATE_BUNDLE_DIR
python host_bundle_chain.py PRIVATE_HOST_CAPTURE_DIR PRIVATE_BUNDLE_DIR
python serial_bundle.py verify PRIVATE_BUNDLE_DIR
```

A v1.9 PASS is only host byte-span consistency. **Always run v0.7 and v1.8 separately** and independently review physical setup, actual flashed firmware, source timestamps and private raw capture. None of these software checks attest real sensors or trustworthy clocks; a carefully fabricated or replayed stream can pass.

## Stage / stop / next experiment

**Strongest evidence:** existing v0.7 cross-check and new fictional v1.8 short-burst counterexample. **Largest gap:** zero independently inspected genuine 600-second BH1750/SCD40 capture and no verified flash ID. **Next experiment:** real private capture with raw SHA-256, independently verified firmware identity and wiring, controlled BH1750 light perturbation, and all three structural gates. **Stop/reframe:** if host byte exposure or device span is short, retain failure and do not describe continuous measurement. If physical provenance cannot be independently inspected, describe software instrumentation only.

**Four lenses:** hiring manager—tests detect regressions between tools; technical reviewer—exact source identities, adversarial boundary and no hidden physical assumption; innovation leader—no novelty or patentability claim; founder—no measured product, reliability, energy or customer outcome. No personal raw telemetry or employer data published.
