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
| EPMO Microsoft 365 Automation | Professional case study; independent fictional demo **Research / Simulation** | [v0.1 replay](benchmarks/epmo-governance/README.md) + [v0.3 durable receipts](benchmarks/epmo-governance/DURABLE_SQLITE_V03.md) + [v0.4 reconciliation](benchmarks/epmo-governance/REPLAY_LEDGER_RECONCILIATION_V04.md) + [v0.5 atomic one-use consumption](benchmarks/epmo-governance/FICTIONAL_APPROVAL_CONSUMPTION_V05.md); **79/79** tests on Linux and Windows [CI #40151625112](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40151625112); all fictional, zero external actions | v0.5 is isolated: approval issuance/actors/clock are untrusted; not integrated with v0.4 replay, fake action, compensation or human burden; employer evidence remains confidential | Integrate sandbox identity and trusted time with v0.4 replay and v0.5 one-use transaction, add transactional outbox/fake action and correction; blind-review against manual notes | Repeatable independent fictional end-to-end gate proves no policy bypass, inspectable receipt/compensation and acceptable measured reviewer burden without employer data | Reframe if approval bypass or double-action is possible, compensation fails or reviewer burden exceeds manual notes; never disclose employer systems for proof |

## October 25, 2026 — EPMO v0.6 structural integrity gate (draft branch)

**Maturity unchanged: Research / Simulation.** The independent [v0.6 read-only ledger auditor](benchmarks/epmo-governance/APPROVAL_LEDGER_INTEGRITY_V06.md) has **22/22 local adversarial tests passed twice** (Linux/Python 3.13.5); [GitHub CI #40174154959](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40174154959) passed **101/101 tests on Ubuntu and Windows**. It detects mismatched, orphaned and missing fictional receipts but **fails intentionally** to detect a coordinated forgery of both tables. No authentication, trusted time, real actions or employer data. Largest gap: v0.4 replay and v0.5 atomic approval are not integrated with identity/time/outbox. Next: a sandbox identity + transactional fake-action end-to-end crash/replay experiment. Reframe as an offline consistency tool if authenticity cannot be independently established. Do not advance stage or release on this result.

## October 26, 2026 — EPMO v0.7 reviewer-burden preflight (draft branch)

**Maturity unchanged: Research / Simulation.** [v0.7 fictional reviewer packet](benchmarks/epmo-governance/BLINDED_REVIEW_PREFLIGHT_V07.md) freezes **16 synthetic approval/execution/correction decisions** (3 valid / 13 invalid), separates the gold key from two order-counterbalanced packets, and rejects malformed/incomplete private reviewer responses. [Final executable-head CI #40222952196](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40222952196) passed **117/117 tests on Ubuntu and Windows** (16 new); [registry](benchmarks/epmo-governance/BLINDED_REVIEW_PREFLIGHT_V07_REGISTRY.json). **No human review results exist**; false-approval rate, correction time and arm difference remain **TBD**. Public source permits key reconstruction, so procedural blinding is not cryptographic. **Largest gap:** independent, consented blinded reviewers plus authenticated sandbox identity/time/outbox. **Next experiment:** predeclare reviewer assignment, privately collect case-level decisions/times, measure false approvals and correction burden versus manual notes; independently complete [Issue #14](https://github.com/Vermicare/Haridas-Satheesh/issues/14) action-safety gate. **Advance only if** reproducible independent evidence supports lower errors/burden without security bypass; **reframe** if structured review worsens human burden or identity/replay guarantees fail. No employer data, external actions, releases or stage advancement.

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


### EPMO v0.8 reviewer packet integrity — 2026-10-26 (draft PR #13)

The v0.7 fictional private scorer could score modified candidate/context/instructions against unchanged gold labels. A before-fix negative-control run [#40265362490](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40265362490) reproduced three failures on Ubuntu. The separate v0.8 implementation binds each full packet to its private gold key and rejects mismatches; [CI #40265457537](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40265457537) passed **139/139 tests on Ubuntu and Windows**. [Evidence record](benchmarks/epmo-governance/REVIEW_PACKET_BINDING_V08.md) · [registry](benchmarks/epmo-governance/REVIEW_PACKET_BINDING_V08_REGISTRY.json).

**New highest-value design gate:** the manual and structured review packets still differ mainly in order and arm label; no experimental treatment contrast exists yet. Define genuinely different review aids and independently assigned, consented reviewers before attempting any reviewer-burden or ROI claim. Packet hashing is not authenticated provenance. Human results, trusted actors, real actions and employer outcomes remain **TBD**. Preserve Research / Simulation evidence classification for the fictional demo; no portfolio maturity change or merge.

### EPMO v0.9 — distinct fictional review treatments (draft PR #13; 2026-10-26)

**Stage unchanged: Research / Simulation.** The [v0.9 treatment protocol](benchmarks/epmo-governance/REVIEW_TREATMENT_V09.md) corrects a design flaw in v0.8: manual and structured arms previously differed chiefly by label and case order, so no presentation effect was identifiable. v0.9 preserves the **same 16 raw fictional cases and order** and gives only the structured arm a deterministic evidence-comparison worksheet with **no policy verdict**. Private gold is bound to complete packets, source v0.8 scoring remains frozen, and negative controls reject altered cases/worksheets/keys/responses. [Verified executable-head CI #40352437149](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40352437149) passed **156/156 tests on Ubuntu and Windows**, CPython 3.13.16; both logs and public demo inspected. [Registry](benchmarks/epmo-governance/REVIEW_TREATMENT_V09_REGISTRY.json).

**Strongest evidence:** reproducible fictional software-contract tests, not people. **Largest gap:** no independently assigned/consenting human reviewers, measured false approvals, correction time or uncertainty; separately no authenticated actors, trusted clock or transactional fake-action outbox. **Next:** preregister reviewer allocation and sample size, then privately collect a between-subject pilot; separately complete [Issue #14](https://github.com/Vermicare/Haridas-Satheesh/issues/14). **Advance only if** independently collected results support acceptable error/time and sandbox safety; **reframe** if the worksheet adds burden without benefit or safety guarantees fail. Human effects, employer ROI and deployment remain **TBD**. No merge, release or external action.


### EPMO v1.0 — reviewer study sensitivity gate (draft PR #13; 2026-10-27)

**Current maturity: Research / Simulation; no advancement.** The [v1.0 executable simulation](benchmarks/epmo-governance/REVIEWER_POWER_V10.md) adds an **assumption-based, reviewer-level** feasibility check before external recruitment. Local Linux CPython 3.13.5 execution: 8/8 unit tests passed; 400 Monte Carlo replications per arm size, 199 reviewer-label permutations each. The [frozen machine-readable result](benchmarks/epmo-governance/REVIEWER_POWER_V10_RESULT.json) reports hypothetical 20% → 10% false-approval detection probability **0.305 at 12**, **0.5975 at 24**, **0.905 at 48**, and **0.9975 at 96 reviewers per arm** (assumed within-reviewer ICC 0.10). Null rejection ranged 0.025–0.05. Cross-OS hosted verification: [Actions #40433944874](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40433944874) passed **164/164 tests on Ubuntu and Windows** at commit `cb80b467beee09d04fa93ae2abc26cee994ac946`; both logs inspected and full frozen simulation outputs matched exactly. No human-study evidence.

**Strongest evidence:** v0.9's verified fictional treatment/packet contract plus v1.0's deterministic *planning* simulation; **no actual reviewers or measured treatment effect**. **Largest gap:** realistic baseline false-approval rates, item effects, heterogeneity, consented independent assignment and review burden are all **TBD**. **Next decisive experiment:** freeze a consent/assignment/missingness plan, privately pilot actual independent reviewers only after outreach checks, estimate plausible effect and heterogeneity, then recompute power including shared case effects before any full study. **Advance only when** independent consented human data support a repeatable benefit and acceptable time cost, with separately verified authorization boundaries. **Kill/reframe** if the worksheet fails to reduce errors, adds disproportionate time, or cannot be evaluated without label leakage. No employer ROI, product, deployment, novelty, or human-study result claimed.
