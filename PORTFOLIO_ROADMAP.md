# Portfolio R&D Roadmap

This roadmap is an evidence-gated control document for the public portfolio. It does **not** upgrade a project's maturity by itself. Advancement requires reproducible or independently inspectable evidence.

## Stage gates

**Idea → Research → Simulation → Prototype → Bench Validation → External Review → Real-world Pilot → Product Candidate**

A project may skip a gate only when existing evidence genuinely satisfies that gate's intent. A project can also move backward, merge, or be archived when evidence weakens the thesis.

## Flagship evidence queue

| Project | Current public maturity | Strongest public evidence | Biggest evidence gap | Highest-value next action | Advance only when | Kill / reframe trigger |
|---|---|---|---|---|---|---|
| Wireless Brain Interface | Research / Simulation | Documented simulated EEG + ECG-style architecture; explicit separation of decoding, uncertainty, safety gating and action | A deterministic synthetic selective-action evaluator is committed, but clean-run reproducibility/results and a public real-EEG benchmark are not yet verified | Execute the committed Issue #3 evaluator in a clean environment twice; verify contract tests and byte-identical risk–coverage output; preserve the benchmark artifact; then connect the frozen evaluator unchanged to longitudinal public motor-imagery EEG | Clean deterministic reruns pass the evaluator contract and preserve reproducible synthetic outputs; then reproducible public-data runs compare the authorization gate fairly with both ungated decoding and simple abstention at comparable coverage | Reframe if safety gating provides no useful false-action reduction after accounting for lost useful actions, or if the claimed contribution collapses into established methods |
| Retail Demand Intelligence | Research / Architecture | Explicit probabilistic, stockout-aware decision loop and intervention framing | No public-data benchmark demonstrating decision value | Create a one-category public-data experiment comparing naive/baseline forecast, probabilistic forecast, stockout censoring/correction and opportunity ranking | A reproducible benchmark shows measurable improvement on predeclared forecasting and decision metrics | Reframe if added external/derived signals fail to beat simpler baselines consistently or cannot support an actionable intervention |
| CORTEX | Architecture / R&D | Bounded governance-memory architecture plus committed synthetic fixture, deterministic baseline and evaluator | The committed benchmark has not yet produced a verified preserved end-to-end regression result; distribution-shift/public-workflow evidence is also absent | Execute the committed fixture → baseline → evaluator pipeline in a clean environment, preserve the scored output and run metadata, then add a genuinely different distribution-shift fixture | Reproducible end-to-end runs produce auditable outputs under predefined extraction, false-positive, traceability and review-burden criteria, with evidence beyond the frozen fixture | Reframe if structured memory adds more review/noise than useful governance signal, reliable lineage cannot be maintained, or performance collapses under realistic distribution shift |
| Adaptive Personal Cooling | Prototype / Documented R&D | Architecture, component research and prototype plan plus committed raw-measurement and instrument-manifest schemas | Instrument identities/uncertainties are not yet populated and no logging dry run or repeated control → fan-only → prototype measurements are preserved | Populate the instrument manifest with actual equipment and uncertainty/check details; complete a logging dry run; then run repeated control → fan-only → prototype trials using the committed measurement schema | Repeatable instrumented measurements show a meaningful localized thermal benefit with defensible energy, humidity and condensation behavior under documented conditions | Reframe if humidity/heat rejection or energy requirements erase the localized-efficiency advantage, or repeated measurements cannot distinguish the prototype from simpler fan-only control |
| Companion Intelligence — Life OS | In Progress; implementation private | Active private engineering architecture with explicit evidence, consent and audit boundaries | Public evidence is necessarily limited; no sanitized end-to-end demonstration | Produce a synthetic/sanitized vertical-slice demo: trusted input → inspectable reasoning → explicit authorization → action receipt → correction/reversal | A public-safe demo demonstrates the governance properties without exposing personal/private data or private code | Reframe modules that cannot preserve explicit authorization, reversibility or inspectable provenance |
| EPMO Microsoft 365 Automation | Implemented / In Progress — Professional | Real professional delivery patterns described without confidential material | Public proof is constrained by employer confidentiality | Build a synthetic Microsoft-style governance scenario or vendor-neutral demo showing handoff reduction, approvals and traceability | A sanitized artifact demonstrates the method without implying disclosure of employer systems | Keep implementation claims high-level if stronger proof would require confidential data; never trade confidentiality for portfolio evidence |

## Benchmark discipline

For every experiment, record:

1. **Question / hypothesis**
2. **Dataset or physical setup and provenance**
3. **Baseline**
4. **Method under test**
5. **Predeclared metrics**
6. **Run conditions / seed / dependency versions**
7. **Results** — use `TBD` until actually measured
8. **Failure cases**
9. **Decision** — advance, repeat, reframe, merge or archive
10. **Limitations**

Unknown values stay **TBD**. Simulated results must remain labeled simulated. Public-data results are not clinical or production validation.

## Cross-project convergence

Several flagships share a deeper systems pattern:

> **signals → state estimation → uncertainty → decision → human/safety gate → action → outcome → adaptation**

Reusable R&D infrastructure should therefore be preferred where it improves rigor: provenance, experiment manifests, uncertainty/calibration metrics, event/decision lineage, replayable simulations, and human-authorization boundaries.

This convergence is a research/engineering pattern, not evidence that the projects are one product.

## Current priority

The next evidence gate is **Wireless Brain Interface Issue #3 reproducibility verification**. The deterministic synthetic evaluator is committed; now execute that exact revision in a clean environment twice, require its contract tests to pass, verify identical thresholds/metrics and byte-identical risk–coverage output, and preserve the resulting artifact. Only then connect the frozen evaluator unchanged to longitudinal public motor-imagery EEG, where the authorization gate must be compared with both ungated decoding and simple confidence abstention at comparable coverage.

After that: **Retail public-data benchmark → CORTEX synthetic governance pilot → Adaptive Cooling instrumented bench protocol → Companion Intelligence sanitized demo → EPMO synthetic governance demo**.


## October 22, 2026 — publication and evidence reconciliation

**Publication status:** the following are committed *evidence-boundary summaries*, not full executable package imports. Earlier independent research ZIPs remain local and are not automatically reproduced by these documents. No maturity upgrades or real-data claims are authorized.

| Family | Public evidence note | Strongest evidence boundary | Next gate |
|---|---|---|---|
| WBI | [October audit](benchmarks/wireless-brain-interface/OCTOBER_2026_EVIDENCE_AUDIT.md) | Committed same-runtime deterministic synthetic execution record; drift benefit unproven | Clean independent reproduction; longitudinal EEG at matched coverage |
| CORTEX | [CI triage](benchmarks/cortex/OCTOBER_2026_CI_TRIAGE.md) | Local synthetic forensic findings, not corrected public CI | Adjudicate contradictory labels and test new scenario |
| Cooling | [Energy gate](benchmarks/adaptive-cooling/OCTOBER_2026_ENERGY_GATE.md) | Synthetic consistency check only | Real instrument/logging dry run, then controlled trials |
| Retail | [Data gate](benchmarks/retail-demand/OCTOBER_2026_DATA_GATE.md) | Local schema/acquisition checks, not decision uplift | Pinned public-data chronological benchmark |
| Hardware/IoT | [Capture gate](projects/HARDWARE_IOT_EVIDENCE_GATE_2026_10.md) | Fictional capture sufficiency checks, no real sensor session | Ten-minute instrumented BH1750/SCD40 capture |
| Companion | [Authorization gate](benchmarks/companion-life-os/OCTOBER_2026_AUTHORIZATION_GATE.md) | Fictional consent and reversal flow only | Independent identity-bound replay/expiry adversarial tests |

**Release rule:** publish executable source, fixtures, licenses, manifests and reproducible CI only after package-level review for correctness, dependency and confidentiality risks. Do not infer that this documentation imports the research ZIPs or that local test claims were independently verified on GitHub.


## October 25, 2026 — Hardware/IoT host capture integrity v0.5 (draft PR #7 only)

**Stage remains Prototype / Hardware Architecture.** The strongest new **software-only** evidence is an independent raw-serial/manifest verifier with 10 injected-port tests, two local CPython 3.13.5/Linux runs of 21/21 relevant tests, and [57/57 tests on both Ubuntu and Windows at executable head](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40130671456). See [evidence note](benchmarks/hardware-iot/HOST_CAPTURE_INTEGRITY_V05.md) and [machine-readable registry](benchmarks/hardware-iot/HOST_CAPTURE_INTEGRITY_V05_REGISTRY.json). The verifier detects altered raw bytes, mismatched counts, status swaps, malformed duplicate-key manifests and false completion, but cannot authenticate device, firmware, sensor readings or a jointly forged manifest/raw pair.

**Largest gap:** no independently reviewed genuine >=600-second BH1750/SCD40 raw capture or device-monotonic coverage. Physical origin, sensor accuracy and field reliability remain **TBD**.

**Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) — preserve raw bytes, actual firmware binary hash, timestamp source, wiring/modes, independently inspectable controlled light perturbation, separate parsed CSV and gap accounting. **Advance only** after genuine repeated sensor evidence and independent setup review; **reframe** as logging tooling if provenance cannot be established or coverage repeatedly fails. No release or physical-performance claim. This paragraph exists on draft PR #7's branch and is **not yet merged into main**.


## October 25, 2026 — Hardware/IoT numeric capture integrity v0.6 (draft PR #7 only)

**Stage unchanged: Prototype / Hardware Architecture.** The v0.5 independent manifest verifier had a demonstrated fail-open numeric parsing gap: non-standard `NaN`/`Infinity` and JSON exponent overflow could be accepted as apparently valid host elapsed time or offsets. [Before-fix CI #40169706985](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40169706985) reproduced **six failing assertions/subtests on Ubuntu**; Windows was cancelled. The finite-only JSON parser correction passed [63/63 tests on both Ubuntu and Windows in CI #40169745261](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40169745261). See [v0.6 failure/reproduction note](benchmarks/hardware-iot/HOST_CAPTURE_NUMERIC_INTEGRITY_V06.md) and [registry](benchmarks/hardware-iot/HOST_CAPTURE_NUMERIC_INTEGRITY_V06_REGISTRY.json). These are **fictional capture tests**, not physical sensor evidence.

**Strongest evidence:** before/after independently runnable regression with raw-byte/hash consistency and fail-closed malformed-numeric checks. **Largest gap:** no authentic >=600-second BH1750/SCD40 dual-sensor recording, firmware attestation, device-monotonic continuity or sensor accuracy. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) genuine instrumented capture and independent provenance review. **Advance only** on reviewable physical measurements; **kill/reframe** as software capture tooling if physical-origin/continuity evidence cannot be established. No release, performance claim or maturity upgrade. This is draft-branch evidence, not main.

## October 25, 2026 — Hardware/IoT host-to-bundle chain v0.7 (draft PR #7 only)

**Stage remains Prototype / Hardware Architecture.** The new [chain verifier](benchmarks/hardware-iot/host_bundle_chain.py) connects the previously separate host raw-serial integrity and raw→CSV bundle preflight contracts. It rejects different host/bundle raw bytes, short host first-to-last byte exposure, incomplete capture and short device-monotonic coverage. [Cross-platform CI #40217485476](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40217485476) passed **75/75 tests on Ubuntu and 75/75 on Windows**, including fictional full-integration positive and replay-negative controls. See [evidence](benchmarks/hardware-iot/HOST_BUNDLE_CHAIN_V07.md) and [registry](benchmarks/hardware-iot/HOST_BUNDLE_CHAIN_V07_REGISTRY.json).

**Strongest evidence:** reproducible, cross-platform *fictional* end-to-end integrity contract. **Largest gap:** zero independently witnessed real BH1750/SCD40 samples; device identity, firmware flashed, sensor accuracy and clock authenticity remain **TBD**. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) genuine ~630-second private acquisition, >=600-second host-byte and device-telemetry coverage, controlled light perturbation, raw/CSV hashes and independent setup review. **Advance only** after repeatable physical observations and source review; **kill/reframe** as logging tooling if physical provenance cannot be demonstrated. No release, deployment, stage change or hardware-performance claim. This note exists on the draft branch, **not main**.
