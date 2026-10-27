# Portfolio R&D Roadmap

This roadmap is an evidence-gated control document for the public portfolio. It does **not** upgrade a project's maturity by itself. Advancement requires reproducible or independently inspectable evidence.

## Stage gates

**Idea → Research → Simulation → Prototype → Bench Validation → External Review → Real-world Pilot → Product Candidate**

A project may skip a gate only when existing evidence genuinely satisfies that gate's intent. A project can also move backward, merge, or be archived when evidence weakens the thesis.

## Flagship evidence queue

| Project | Current public maturity | Strongest public evidence | Biggest evidence gap | Highest-value next action | Advance only when | Kill / reframe trigger |
|---|---|---|---|---|---|---|
| Wireless Brain Interface | Research / Simulation | [Committed synthetic execution record](benchmarks/wireless-brain-interface/EXECUTION_RECORD.md): two same-runtime deterministic reruns with byte-identical risk–coverage CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`; no EEG | Independent second-environment reproduction and held-out public EEG policy comparison are not yet established on main; matched-coverage drift-gate benefit remains unproven | Reproduce the frozen evaluator independently, then freeze a subject-disjoint public EEG pipeline and compare ungated, confidence abstention and drift gate at matched coverage | Reproducible public-data results show a defensible risk–coverage tradeoff with subject/session provenance and uncertainty; synthetic reruns alone do not advance maturity | Reframe if gate fails to improve false-action risk at comparable useful-action coverage or adds no signal beyond simple abstention |
| Retail Demand Intelligence | Research / Architecture | Explicit probabilistic, stockout-aware decision loop and intervention framing | No public-data benchmark demonstrating decision value | Create a one-category public-data experiment comparing naive/baseline forecast, probabilistic forecast, stockout censoring/correction and opportunity ranking | A reproducible benchmark shows measurable improvement on predeclared forecasting and decision metrics | Reframe if added external/derived signals fail to beat simpler baselines consistently or cannot support an actionable intervention |
| CORTEX | Architecture / R&D | Bounded governance-memory architecture plus committed synthetic fixture, deterministic baseline and evaluator | The committed benchmark has not yet produced a verified preserved end-to-end regression result; distribution-shift/public-workflow evidence is also absent | Execute the committed fixture → baseline → evaluator pipeline in a clean environment, preserve the scored output and run metadata, then add a genuinely different distribution-shift fixture | Reproducible end-to-end runs produce auditable outputs under predefined extraction, false-positive, traceability and review-burden criteria, with evidence beyond the frozen fixture | Reframe if structured memory adds more review/noise than useful governance signal, reliable lineage cannot be maintained, or performance collapses under realistic distribution shift |
| Adaptive Personal Cooling | Prototype / Documented R&D | Committed raw/instrument templates plus draft-branch fictional-only [origin marker coverage v0.2](benchmarks/adaptive-cooling/ORIGIN_GATE.md) and [dry-run integrity v0.4](benchmarks/adaptive-cooling/DRY_RUN_INTEGRITY.md), including finite-input overflow rejection and a **new negative control** where whole-run energy totals conceal 10 interval discrepancies; synthetic-only [CI 40/40 on Ubuntu and Windows](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40231888178); plus draft-branch [capture-chain v1](benchmarks/adaptive-cooling/CAPTURE_CHAIN_V1.md) with 22/22 fictional-only local tests in two clean Linux directories ([CI 62/62 on Ubuntu and Windows](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40295332717)); plus draft-branch [cross-artifact alignment v1](benchmarks/adaptive-cooling/CAPTURE_ALIGNMENT_V1.md) with 13 new fictional-only negative/control tests ([CI 75/75 on Ubuntu and Windows](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40388474144)); plus draft-branch [declared-cadence contradiction v1](benchmarks/adaptive-cooling/CAPTURE_CADENCE_V1.md) (fictional 5-second declaration with actual 60-second CSV gaps rejected; [CI 79/79 on Ubuntu and Windows](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40462666047)); no real sensor provenance, logger-to-CSV replay or meter-latency characterization | Instrument identities/uncertainties are not yet populated, original logger-to-CSV conversion is not independently replayed, and no real ≥10-minute logging dry run or repeated control → fan-only → prototype measurements are preserved | Populate the instrument manifest with actual equipment and uncertainty/check details; complete a logging dry run; then run repeated control → fan-only → prototype trials using the committed measurement schema | Repeatable instrumented measurements show a meaningful localized thermal benefit with defensible energy, humidity and condensation behavior under documented conditions | Reframe if humidity/heat rejection or energy requirements erase the localized-efficiency advantage, or repeated measurements cannot distinguish the prototype from simpler fan-only control |
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

The [frozen WBI synthetic evaluator execution record](benchmarks/wireless-brain-interface/EXECUTION_RECORD.md) already documents **two same-runtime deterministic executions** and a preserved byte-identical risk–coverage CSV. Do not repeat this as an unverified milestone. The next unresolved gates are **independent second-environment reproduction** and a **subject-disjoint public EEG benchmark** with frozen calibration, common action opportunities, matched useful-action coverage and uncertainty. Draft PR #5 contains additional synthetic policy diagnostics, but is unmerged and cannot be treated as main-branch EEG validation.

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
