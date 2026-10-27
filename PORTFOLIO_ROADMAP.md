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

## October 26, 2026 — Hardware/IoT manifest ambiguity gate v0.8 (draft PR #7 only)

**Stage unchanged: Prototype / Hardware Architecture.** The raw→CSV capture preflight accepted ambiguous duplicate manifest keys and nonfinite JSON metadata. [Before-fix CI #40245700265](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40245700265) reproduced **4/80 failed Ubuntu regression tests**; Windows was cancelled. Strict recursive duplicate-key and finite-number parsing passed [80/80 tests on Ubuntu and 80/80 on Windows in CI #40245744561](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40245744561). See [failure/repair record](benchmarks/hardware-iot/MANIFEST_PARSER_INTEGRITY_V08.md) and [registry](benchmarks/hardware-iot/MANIFEST_PARSER_INTEGRITY_V08_REGISTRY.json).

**Strongest evidence:** cross-platform fictional negative controls with before/after CI. **Largest gap:** zero independently verified physical BH1750/SCD40 captures; hashes and operator declarations do not authenticate hardware. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8), an independently inspectable >=600-second real dual-sensor capture with raw bytes, firmware/wiring provenance and controlled light perturbation. **Advance only** after reproducible physical observation and review; **reframe** as capture-integrity tooling if physical provenance remains unavailable. No release, merge, sensor-performance claim or maturity upgrade. This note is on the draft branch, not main.

## October 26, 2026 — Hardware/IoT private-bundle publication safeguard v0.9 (draft PR #7 only)

**Stage unchanged: Prototype / Hardware Architecture.** The downstream raw-serial bundle builder previously allowed output inside a Git checkout even though the acquisition tool forbade it. Two fictional negative controls reproduced this fail-open privacy risk: [before-fix CI #40309376746](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40309376746), **2/82 expected failures on Ubuntu** (Windows cancelled). A shared Git-worktree guard rejects both `.git` directories and linked-worktree `.git` files before writing: [after-fix CI #40309494687](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40309494687), **82/82 passed on both Ubuntu and Windows**. [Evidence](benchmarks/hardware-iot/RAW_BUNDLE_GIT_PRIVACY_V09.md) · [Registry](benchmarks/hardware-iot/RAW_BUNDLE_GIT_PRIVACY_V09_REGISTRY.json).

**Strongest evidence:** cross-platform regression of an actual software privacy-guard gap using fictional input. **Largest gap:** no authentic independently inspected >=600-second BH1750/SCD40 capture; firmware flashed, sensor origin, accuracy and reliability remain **TBD**. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8), private >=630-second serial recording with >=600-second dual-sensor monotonic and host-byte coverage, hashes, controlled light perturbation and independent setup review. **Advance only** after repeated, reviewable physical evidence; **kill/reframe** as capture-integrity tooling if physical provenance cannot be established. This guard does not stop deliberate later Git additions or other data transfers. Draft branch only, not main; no release, merge or stage advancement.

## October 27, 2026 — Hardware/IoT device-side capture candidate (draft PR #7 only)

**Stage unchanged: Prototype / Hardware Architecture.** [ESP-IDF dual-sensor firmware candidate](benchmarks/hardware-iot/firmware/espidf_dual_sensor_capture/README.md) now emits the proposed exact raw `IOTCSV,` contract in source form. The CRC/framing helper was tested on host C compilers: [GitHub Actions #40406840604](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40406840604) passed **83/83 tests on Ubuntu and 83/83 on Windows**, including the new compiled host C check. **This is not an ESP-IDF firmware build or hardware test.** No board was flashed, no real sensor bytes were acquired, and no calibration or accuracy claim is supported.

**Strongest evidence:** reproducible dual-OS host CRC/framing checks and existing synthetic host-to-bundle integrity chain. **Largest gap:** no independently inspectable >=600-second genuine BH1750/SCD40 capture, actual ESP-IDF compile/flash log, firmware identity, controlled light perturbation or physical setup review. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) — compile candidate in ESP-IDF 6.1, capture private raw bytes for >=600 seconds, preserve hashes and failures, run chain verifier, independently inspect wiring/source and light-change response. **Advance** only with repeated independently reviewable physical evidence; **reframe** as software capture tooling if authentic continuity cannot be established. No stage upgrade, release, or employer/private data. This entry is on the draft branch, **not main**.

## October 27, 2026 — Hardware/IoT compile-only gate v1.1 (draft PR #7)

**Stage remains Prototype / Hardware Architecture.** The ESP32-S3 BH1750/SCD40 firmware candidate now has a **real ESP-IDF v6.1 compile-only result** at commit `79426a5ba1245264c386565dd5911d3a578180f8`: [Actions #40421852576](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40421852576) succeeded in the official Espressif v6.1 Docker image, produced a 196080-byte binary (SHA-256 `28637965c44fcbe86fb441fafc553b6f4f7c4a8d68505a528faeefa49e877a55`), and did **not** flash or interact with hardware. [Host-only Actions #40421852619](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40421852619) passed 83/83 synthetic/host tests on each of Ubuntu and Windows. [Execution record](benchmarks/hardware-iot/firmware/espidf_dual_sensor_capture/ESP_IDF_COMPILE_V11_EXECUTION_2026_10_27.md) and [registry](benchmarks/hardware-iot/firmware/espidf_dual_sensor_capture/EVIDENCE_REGISTRY.json) preserve provenance and unknowns. This is **draft-branch evidence, not mainline publication**.

**Largest gap:** no actual flashed binary identity, sensor transaction, calibrated physical observation, genuine >=600-second dual-sensor raw capture or independent physical review. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) — operator flash/wiring review, private raw logging, controlled BH1750 light change, host/device span verification and independent evidence review. **Advance only** on independently inspectable physical measurements; **kill/reframe** as software logging tooling if real acquisition/provenance cannot be established. No physical performance or deployment claim, release or stage upgrade.

## October 27, 2026 — Hardware/IoT retained firmware bundle v1.2

**Maturity unchanged: Prototype / Hardware Architecture.** The ESP32-S3 BH1750/SCD40 candidate now has a **retained, independently downloaded and SHA-verified ESP-IDF v6.1 build package** on draft PR #7. [Final-head CI #40457296813](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457296813) compiled the application, verified four file digests and uploaded [artifact #12712637366](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457296813/artifacts/12712637366). The downloaded ZIP SHA-256 matched GitHub's published digest, and all four embedded file hashes matched. The 222,776-byte artifact expires **November 10, 2026 UTC**; it is not a permanent release. [Independent execution record](benchmarks/hardware-iot/CI_FIRMWARE_BUNDLE_V12_EXECUTION_2026_10_27.md) preserves the exact SHA-256s, checked-out merge SHA, PR head, run conditions, flash offsets and limitations. [Final-head host CI #40457296794](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40457296794) passed **83/83 host/synthetic tests on Ubuntu and Windows**.

**Preserved failure:** [CI #40456945522](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40456945522) compiled successfully but failed to write `SHA256SUMS.txt` in the root-owned container build directory, so it uploaded **no** artifact. The fixed workflow stages the output in runner-owned temporary storage before hashing/upload. **Strongest evidence:** verified compile and retained unflashed bytes with independent SHA validation. **Largest gap:** **no physical sensor sample, actual flash, independent setup review, or confirmed board-specific flash capacity**; the CI-generated flash command currently declares **2 MB**, which must be checked against the actual board before use. **Next experiment:** [Issue #8](https://github.com/Vermicare/Haridas-Satheesh/issues/8) — independently confirm board/flash layout and wiring, flash a reviewed and hashed binary, capture genuine >=600-second private dual-sensor telemetry with a light-change control, then run host-to-bundle verification and obtain independent setup review. **Advance only** with independently reviewable physical evidence; **kill/reframe** as instrumentation software if physical origin/continuity cannot be established. No release, merge, hardware validation, product claim, collaborator outreach or stage upgrade.
