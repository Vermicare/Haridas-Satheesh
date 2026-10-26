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

The [frozen WBI synthetic evaluator execution record](benchmarks/wireless-brain-interface/EXECUTION_RECORD.md) already documents **two same-runtime deterministic executions** and a preserved byte-identical risk–coverage CSV. Do not repeat this as an unverified milestone. The second-environment and hosted cross-OS **synthetic software** reproduction gates were resolved on draft PR #16; the unresolved scientific gate is **real, different-day public EEG**, with separate within-subject cross-session and subject-disjoint protocols, frozen calibration, common action opportunities, matched useful-action coverage and subject-level uncertainty. Draft PR #5 contains additional synthetic policy diagnostics, but is unmerged and cannot be treated as main-branch EEG validation.

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

## October 26, 2026 — frozen WBI evaluator, separate-container reproduction (draft)

The unchanged mainline WBI synthetic evaluator was authenticated by Git blob and executed in a **separate Linux container** with Python 3.13.5. Two clean-directory runs matched the original September CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` and matched stdout hashes; a deliberately mutated source was rejected by the new verifier. See [reproduction record](benchmarks/wireless-brain-interface/SEPARATE_CONTAINER_REPRO_2026_10_26.md) and [executable verifier](benchmarks/wireless-brain-interface/verify_frozen_synthetic.py).

**Evidence boundary:** this is a second *execution environment*, not a new Python version, independent external reviewer, Windows CI or public EEG benchmark. No stage change. **Next:** Windows/Linux CI for the frozen checker and subject-disjoint real EEG with matched coverage; **reframe** if drift gating does not beat confidence abstention fairly.

### October 26, 2026 — WBI cross-OS software gate resolved on draft PR #16

[GitHub Actions #40301577095](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40301577095) **passed on Ubuntu and Windows**, Python 3.13.16, with matching frozen source Git blob, September CSV SHA-256 and stdout SHA-256 in both job logs. Earlier Windows failures were **preserved**: Git checkout CRLF conversion, then legacy console encoding; both were fixed in the verification infrastructure without changing the frozen evaluator. [Full reproducibility/failure record](benchmarks/wireless-brain-interface/SEPARATE_CONTAINER_REPRO_2026_10_26.md).

**Strongest WBI evidence:** deterministic fictional evaluator, independent Linux environment reproduction and now successful hosted cross-OS reproduction. **Largest gap:** no subject-disjoint real EEG, matched-coverage benefit, clinical safety or external review. **Next experiment:** freeze and execute public EEG subject/session holdout against ungated, confidence-abstention and drift-aware policies with common opportunities and uncertainty intervals. **Advance only** with independently inspectable real-data risk–coverage evidence; **reframe** if drift gating cannot beat confidence-only abstention at matched coverage. **Stage remains Research / Simulation; draft/unmerged.**

### October 27, 2026 — WBI dataset eligibility and split integrity (draft PR #16)

[Prospective BNCI2014_001 EEG protocol](benchmarks/wireless-brain-interface/BNCI2A_EEG_PREREG_2026_10_27.md) corrects a consequential dataset mismatch: PhysioNetMI offers one session and cannot establish different-day session shift; BCI Competition IV 2a has two sessions on separate days (9 subjects, six runs/session). A standard-library [metadata-only split preflight](benchmarks/wireless-brain-interface/bnci2a_split_preflight.py) now specifies 9 within-subject temporal and 9 subject-disjoint folds with nonoverlapping train/calibration/test trial identifiers; [nine fictional negative-control tests](benchmarks/wireless-brain-interface/test_bnci2a_split_preflight.py) passed locally. [Hosted cross-OS CI #40415140397](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40415140397) passed **9/9 fictional metadata tests on Ubuntu and 9/9 on Windows**; both logs inspected. Dataset download, real metadata manifest, EEG results and source file hashes remain **TBD**. **No stage change.**

**Strongest evidence:** preserved September synthetic execution and verified hosted cross-OS reproduction. **Largest gap:** no real cross-day EEG, no matched-coverage benefit or independent external review. **Next experiment:** acquire and checksum BNCI2a session T/E files, extract source-derived trial metadata, pass the split gate, freeze decoder and evaluate held-out E without peeking. **Advance only** after independently inspectable, subject-aware real-data risk–coverage and uncertainty evidence; **reframe** if drift gating fails against simple abstention at comparable coverage. Public EEG classification is not clinical or hardware validation.
