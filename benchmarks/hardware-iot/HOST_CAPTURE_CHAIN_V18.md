# Hardware/IoT v1.8 — host capture-to-bundle chain integrity (2026-10-29)

**Stage:** Prototype / Hardware Architecture (unchanged). **Physical runs:** 0 in this experiment. **All tests fictional.** This is a stacked, unmerged research contribution to draft PR #7, not a firmware release.

## Why

The existing `serial_acquire.py` records raw bytes, completion status and host monotonic duration; `serial_bundle.py` independently packages supplied raw bytes. The existing bundle verifier checks extraction and structural device timestamps but does not bind a derived bundle to the original **host capture completion receipt**. A caller could supply bytes from an interrupted or otherwise unverified host capture without the bundle builder knowing its status. This is an inspection-derived integration gap, not a claim of a proven real-world failure.

## Executable preflight

From `benchmarks/hardware-iot`:

```bash
python -B -m unittest -v test_capture_chain_v18.py
python capture_chain_v18.py /private/host_capture_dir /private/bundle_dir
python serial_bundle.py verify /private/bundle_dir
```

The new **read-only** chain checker requires:
- exact host `HOST_CAPTURE_COMPLETE_PROVENANCE_UNVERIFIED` status, no leftover `raw_serial.partial`, 600+ seconds requested and actually elapsed on the host monotonic clock;
- host raw bytes and count bound to the host SHA-256; byte-identical retained raw bytes and SHA-256 in the derived bundle;
- internally consistent first/last host byte offsets, UTC host timestamp ordering, finite nonboolean numeric fields, duplicate-key-free JSON, declared port/baud;
- a present derived CSV bound to the bundle's SHA-256 and the expected schema.

**Important:** it deliberately does **not** parse telemetry, verify device-monotonic span, check sensor cadence, verify host clock integrity, authenticate a physical sensor, or prove that the supplied firmware was flashed. The separate `serial_bundle.py verify` step remains mandatory, followed by independent human review of raw serial, wiring, flashed firmware and a controlled perturbation. A deliberately false `capture_origin=physical` in the fictional positive test **passes this chain-integrity gate**, demonstrating the non-attestation boundary.

## Reproducibility / outcome

Two isolated local executions of **14/14 fictional adversarial tests** passed on Linux CPython (exact runtime version TBD); checks include interrupted status, missing continuity, raw/bundle/CSV tampering, duration, offsets, malformed JSON, nonfinite and boolean counters, and UTC order. Source Git blob `e94bc84f75afc2942ab30f480eb82e42577db472`; test Git blob `7063789ed300f35c71efd2303094695b0b367c1e`. Cross-platform GitHub Actions: **TBD until completed final-head logs are inspected**.

**Decision:** no maturity advancement. This closes a *software evidence-chain consistency* gap, not the physical capture gap. Highest-value next experiment remains a genuine private >=600-second BH1750/SCD40 capture with independently inspected sensor wiring, read-only flash identity, a controlled light perturbation and full provenance. If that cannot be produced, retain Prototype / Hardware Architecture and do not claim bench validation.

**Four lenses:** hiring manager—defensive instrumentation integration; technical reviewer—reproducible rejection controls; innovation leader—evidence discipline, not novelty; founder—zero measured device performance or market validation. No personal telemetry, device IDs, secrets, employer information, outreach or patentability claims are published.
