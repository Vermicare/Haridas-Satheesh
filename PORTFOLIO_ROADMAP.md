# Portfolio R&D Roadmap

This roadmap is an evidence-gated control document for the public portfolio. It does **not** upgrade a project's maturity by itself. Advancement requires reproducible or independently inspectable evidence.

## Stage gates

**Idea → Research → Simulation → Prototype → Bench Validation → External Review → Real-world Pilot → Product Candidate**

A project may skip a gate only when existing evidence genuinely satisfies that gate's intent. A project can also move backward, merge, or be archived when evidence weakens the thesis.

## Flagship evidence queue

| Project | Current public maturity | Strongest public evidence | Biggest evidence gap | Highest-value next action | Advance only when | Kill / reframe trigger |
|---|---|---|---|---|---|---|
| Wireless Brain Interface | Research / Simulation | Frozen synthetic evaluator independently reproduced on Linux/Windows in [draft PR #5](https://github.com/Vermicare/Haridas-Satheesh/pull/5); one real S001R04 training EDF checksum/header verification passed [CI #40122474197](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40122474197) | Real EDF+ annotation extraction remains blocked by bounded download timeouts; no EEG decoding, matched-coverage public-data results, longitudinal drift validation or independent review | Resolve bounded publisher-source acquisition, cross-check real T0/T1/T2 task annotations with an independent reader, then freeze subject-disjoint decoder and matched-coverage gate comparisons; select separate multi-session data for drift | Independently reproduced held-out public EEG evaluation reduces incorrect actions at comparable coverage without unacceptable useful-action loss | Reframe drift gate if dominated by simple abstention; no clinical/device claims |
| Retail Demand Intelligence | Research / Architecture | Explicit probabilistic, stockout-aware decision loop and intervention framing | No public-data benchmark demonstrating decision value | Create a one-category public-data experiment comparing naive/baseline forecast, probabilistic forecast, stockout censoring/correction and opportunity ranking | A reproducible benchmark shows measurable improvement on predeclared forecasting and decision metrics | Reframe if added external/derived signals fail to beat simpler baselines consistently or cannot support an actionable intervention |
| CORTEX | Architecture / R&D | Frozen fictional fixture/shift negative control, hash-pinned 12-utterance blinded-review packet and [60/60 prior cross-platform structural tests](benchmarks/cortex/BLINDED_REVIEW_FAIL_CLOSED_V02.md); [earlier seven malformed-input exceptions per OS](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40155101712) corrected in [CI #40155139147](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40155139147); new [JSON/manifest fail-closed v0.3](benchmarks/cortex/CORTEX_JSON_INTAKE_INTEGRITY_V03.md) reproduced **4 assertion failures + 5 uncaught errors per OS** before fix and passed **69/69 tests on Ubuntu and Windows** in [CI #40199139641](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40199139641) | Fixture-specific extractor fails on separately authored fictional case; no independent labels, semantic accuracy, reviewer correction time, authenticated history or real workflow | Obtain independent blinded annotations of frozen fictional case; adjudicate disagreements and evaluate a general extractor against fairly timed manual structured notes; preserve private reviewer inputs off GitHub | Reproducible unseen-case semantic extraction with traceable predecessors and acceptable false positives/reviewer burden; structural tests alone cannot advance maturity | Reframe as provenance/lineage tooling if unsupported records or correction burden exceed manual notes; reject cyclic lineage and adjudicate forks |
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

**Evidence-first priority (2026-10-24):** WBI's frozen synthetic reproducibility is supported by cross-platform evidence in draft PR #5, and one real training EDF checksum/header preflight passed in [CI #40122474197](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40122474197), but public EEG **decoding** and real annotation validation remain **TBD** after bounded acquisition timeouts. PhysioNet's single-session data can test cross-subject transfer, not longitudinal drift. Resolve real annotation acquisition and independently verify task labels before claiming any EEG decoding result. In parallel, CORTEX draft PR #4 now includes a new *unlabeled* fictional reviewer case and archive, with a preregistered independent annotation/correction-burden protocol. Neither packet preparation nor structural tests are external review or stage advancement.

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

## October 25, 2026 — CORTEX malformed intake evidence gate

[Eight fictional malformed-packet controls](benchmarks/cortex/BLINDED_REVIEW_FAIL_CLOSED_V02.md) reproduced **seven uncaught exceptions per OS before correction** in [CI #40155101712](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40155101712). After fail-closed input guards, [CI #40155139147](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40155139147) passed **60/60 structural tests on Ubuntu and Windows** and preserved existing fictional input/output hash assertions. The [versioned registry](benchmarks/cortex/BLINDED_REVIEW_FAIL_CLOSED_V02_REGISTRY.json) pins source/test Git blobs and run conditions. This is validator correctness only, **not** independent annotation, extraction performance, human timing or external review. Stage unchanged; next evidence gate is the independently adjudicated unseen-case study.

## October 26, 2026 — CORTEX archival citation evidence gate v0.4

**Stage unchanged: Architecture / R&D.** The frozen fictional reviewer intake checks that a superseded decision ID exists, but an otherwise valid submission can omit the **specific archived record** supporting that predecessor. The additive [v0.4 citation gate](benchmarks/cortex/ARCHIVE_CITATION_GATE_V04.md) requires an exact predecessor-to-archive-record reference, with [source and tests](benchmarks/cortex/archive_citation_gate_v04.py) and [machine-readable registry](benchmarks/cortex/ARCHIVE_CITATION_GATE_V04_REGISTRY.json). This fixes a structural evidence-link gap, **not** semantic extraction, reviewer independence, actual historical authenticity, or correction burden. No stage advancement.

**Strongest evidence:** reproducible fictional structural negative control, with original v0.1 intake retained. **Largest gap:** independently annotated unseen fictional case, blinded adjudication and measured correction time versus manual notes. **Next experiment:** voluntary private reviewer annotations, freeze gold labels before general extractor runs, and report real measured review burden. **Kill/reframe:** if unsupported lineage persists or structured-memory correction burden exceeds manual notes, narrow CORTEX to provenance/lineage tooling. GitHub CI: **TBD pending final-head review**.
