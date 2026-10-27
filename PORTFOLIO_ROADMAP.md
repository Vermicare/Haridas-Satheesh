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
| CORTEX | Architecture / R&D | [Frozen synthetic fixture/shift negative controls](benchmarks/cortex/LINEAGE_SHIFT_EVIDENCE.md) and [strict source-span falsification](benchmarks/cortex/SOURCE_SPAN_COMPLETENESS_V01.md): a required citation can be omitted while legacy traceability stays 1.0; 135/135 CI tests passed on Ubuntu and Windows | No independently adjudicated semantic/source-span labels, human correction time, authenticated history or real workflow | Freeze independent blinded annotations and adjudicated required source spans for the unseen fictional case; compare a general extractor against fairly timed manual notes (Issue #12) | Reproducible unseen-case quality, complete/defensible citations and acceptable measured false-positive and correction burden | Reframe as provenance/lineage assistance if unsupported records or correction burden exceed manual notes; structural checks cannot establish human value |
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

**Strongest evidence:** reproducible fictional structural negative control, with original v0.1 intake retained. **Largest gap:** independently annotated unseen fictional case, blinded adjudication and measured correction time versus manual notes. **Next experiment:** voluntary private reviewer annotations, freeze gold labels before general extractor runs, and report real measured review burden. **Kill/reframe:** if unsupported lineage persists or structured-memory correction burden exceeds manual notes, narrow CORTEX to provenance/lineage tooling. GitHub CI: **90/90 synthetic tests passed on Ubuntu and Windows** ([run #40241271339](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40241271339), executable head `e5f95d7`); final documentation head pending review.

## October 26, 2026 — CORTEX standards-mapping decision (v0.5, draft)

**Evidence:** [Synthetic PROV-O mapping](benchmarks/cortex/PROV_O_MAPPING_V01.md) represents author-created fictional source/decision/archive nodes with `prov:wasDerivedFrom` and preserves domain-specific `cortex:supersedes` separately from `prov:wasRevisionOf`. The [registry](benchmarks/cortex/PROV_O_MAPPING_V01_REGISTRY.json) pins input/source/test Git blobs and explicitly records **hosted CI as TBD**; 19 adversarial test cases are committed; [v0.2 negative-control evidence](benchmarks/cortex/PROV_O_MAPPING_INTEGRITY_V02.md) reproduced five false accepts and one malformed-input error in the original mapper, then passed 19/19 tests in two separate local Python 3.13.5/Linux clean directories with identical graph SHA-256. A matching latest-head Ubuntu/Windows Actions run remains **TBD**. This is a synthetic interoperability/integrity example, **not** semantic extraction, RDF conformance, real history or reviewer evidence. No maturity advancement.

**Largest gap:** independently adjudicated unseen-case source/lineage annotations and measured correction burden. **Next experiment:** Issue #12, freeze independent labels and compare a general extractor with fairly timed manual structured notes. **Reframe/kill:** narrow to provenance-only assistance if unsupported records or correction effort outweigh manual notes. Existing validated v0.4 evidence is preserved.

## October 26, 2026 — CORTEX private reviewer pair readiness v0.1

**Maturity unchanged: Architecture / R&D.** [Two-reviewer structural preflight](benchmarks/cortex/REVIEWER_PAIR_PREFLIGHT_V01.md) is a synthetic-only preparation artifact. It binds both inputs to the original fictional case/archive hashes and rejects duplicate pseudonyms, missing citations, non-manual methods and unusable timing. It reports only aggregate source-signature overlap, not semantic agreement. **Strongest evidence:** previously verified fictional structural tests plus new test-only pair controls ([CI #40372166423](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40372166423): 123/123 tests passed on Ubuntu and Windows; logs inspected). **Largest gap:** independent reviewers, adjudicated source-span labels and measured correction burden. **Next experiment:** Issue #12's private blinded annotations and a fair manual comparator. **Kill/reframe:** if unsupported governance records or correction time exceed manual notes, narrow to provenance/lineage assistance. No human results or stage change.

## October 27, 2026 — CORTEX source-span metric falsification (v0.1)

**Stage unchanged: Architecture / R&D.** [Evidence and protocol](benchmarks/cortex/SOURCE_SPAN_COMPLETENESS_V01.md), [executable auditor](benchmarks/cortex/source_span_completeness_v01.py) and [provenance registry](benchmarks/cortex/SOURCE_SPAN_COMPLETENESS_V01_REGISTRY.json) demonstrate that the original frozen `source_span_traceability` awards full credit to a **nonempty subset** of required sources. In a controlled, author-created fictional seven-object negative case, removing one required decision citation leaves legacy traceability at 1.0, while strict exact-source completeness falls from 7/7 to 6/7. [GitHub Actions #40439644368](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40439644368) passed **135/135 tests on Ubuntu and 135/135 on Windows**, including 12 new adversarial controls; both logs inspected. The original evaluator and historical scores are preserved.

**Strongest evidence:** reproducible metric falsification on frozen synthetic source bytes, not real meeting performance. **Largest gap:** independently adjudicated required source spans, semantic agreement and measured correction burden. **Next experiment:** Issue #12 blinded reviewer study, then frozen general-extractor comparison against manual structured notes. **Advance only with:** defensible independently reviewed citations and acceptable measured burden. **Kill/reframe:** narrow to provenance-assisted review if unsupported governance records or correction effort outweigh manual notes. No external validation, real workflow, release or maturity advancement.

## October 27, 2026 — CORTEX annotation comparability gate

**Stage unchanged: Architecture / R&D.** A source-only object could pass the earlier fictional blinded-review intake even though it lacks a decision statement, action description, risk statement, dependency or conditional follow-up. This undermines any later claim that source-signature overlap represents semantic agreement. The additive [v0.2 annotation contract](benchmarks/cortex/SEMANTIC_ANNOTATION_CONTRACT_V02.md) requires typed per-kind semantic fields, explicit unknown owner/date/status, versioned reviewer schema and the existing frozen source/archive integrity checks. The old intake, labels, evaluator and packet hashes remain untouched.

**Strongest evidence:** reproducible fictional integrity/negative controls (not semantic extraction). **Largest gap:** no independent reviewers, adjudicated labels or measured correction time. **Next decisive experiment:** two voluntary blinded annotations of the fixed fictional packet, then a frozen general extractor versus a fairly timed manual-note comparator. **Kill/reframe:** if unsupported governance facts or correction burden exceed manual notes, narrow CORTEX to provenance/lineage assistance. No reviewer data, real employer records, deployments or external validation are claimed. Cross-platform CI for the latest v0.2 tests: **pending final-head verification**.
