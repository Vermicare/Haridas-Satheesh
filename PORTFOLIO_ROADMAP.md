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
| CORTEX | Architecture / R&D | Frozen fictional exact-match baseline; [archive/transfer negative controls](benchmarks/cortex/LINEAGE_SHIFT_EVIDENCE.md) and 13 additive supersession graph tests on draft PR #4; the original fixture scores 1.0 F1 despite unresolved D0 | The frozen-only baseline returns no objects on a separately authored fictional scenario (all five F1=0); self-loops/cycles were not checked by the earlier membership-only preflight; no blinded semantic review, correction-time study, authenticated history, or real workflow | Have two independent reviewers annotate an unseen fictional meeting and archival documents, explicitly adjudicate forks/cycles, then compare a general extractor with manual notes on source precision, false positives and measured correction time | Reproducible unseen-case extraction and defensible historical lineage, independently reviewed with predeclared false-positive and correction-burden thresholds | Reframe if source attribution cannot be substantiated or reviewer effort/noise exceeds manual notes; treat cycles as invalid and forks as requiring adjudication |
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
