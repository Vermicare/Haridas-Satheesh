# Portfolio R&D Roadmap

This roadmap is an evidence-gated control document for the public portfolio. It does **not** upgrade a project's maturity by itself. Advancement requires reproducible or independently inspectable evidence.

## Stage gates

**Idea → Research → Simulation → Prototype → Bench Validation → External Review → Real-world Pilot → Product Candidate**

A project may skip a gate only when existing evidence genuinely satisfies that gate's intent. A project can also move backward, merge, or be archived when evidence weakens the thesis.

## Flagship evidence queue

| Project | Current public maturity | Strongest public evidence | Biggest evidence gap | Highest-value next action | Advance only when | Kill / reframe trigger |
|---|---|---|---|---|---|---|
| Wireless Brain Interface | Research / Simulation | Main synthetic evaluator [execution record](benchmarks/wireless-brain-interface/EXECUTION_RECORD.md) has unchanged CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`; [draft #16](https://github.com/Vermicare/Haridas-Satheesh/pull/16) independently reproduced the synthetic evaluator and inspected A01T/A02T/A04T public EEG **structure only**; [A04T cross-OS reacquisition](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40633875375) independently matched its observed training-file SHA-256 on Ubuntu and Windows | Real EEG decoding, matched-coverage benefit, remaining 15 MAT-file structures, independent review TBD | Complete remaining 15-file label-safe provenance; freeze held-out EEG decoding and matched-coverage comparison | Held-out EEG shows reproducible benefit over abstention at matched coverage | Reframe if added drift gate fails simpler abstention across subjects/sessions |
| Retail Demand Intelligence | Research / Architecture | [Draft #19](https://github.com/Vermicare/Haridas-Satheesh/pull/19) tested publisher data across 293 new stores; predeclared superiority gate FAILED. Post-hoc day-weighted difference −0.020454 with 95% store-cluster interval [−0.067105, +0.022735] | Unseen chronological confirmation, latent-demand ground truth and decision value TBD | Freeze comparator and estimand; evaluate truly unseen temporal/external holdout | Predeclared forecast and decision metrics improve on new data | Reframe if complexity does not beat simple baselines |
| CORTEX | Architecture / R&D | [Draft #4](https://github.com/Vermicare/Haridas-Satheesh/pull/4) has verified synthetic cross-platform regression and negative controls | Blinded human annotation, general semantic accuracy and correction burden TBD | Freeze fictional scenario; obtain two independent voluntary annotations; compare general extractor to manual notes | Auditable extraction on unseen examples with acceptable measured review burden | Reframe if false positives or review time exceed manual notes |
| Adaptive Personal Cooling | Prototype / Documented R&D | Main instrument schema plus [draft #6](https://github.com/Vermicare/Haridas-Satheesh/pull/6) synthetic drift-order counterexamples; no physical measurement | Actual instruments, 600-second logging, uncertainty and controlled comparison TBD | Perform real instrumented dry run and position-balanced ambient/fan/prototype trials | Measured benefit survives fan-only, energy, humidity and uncertainty checks | Reframe if real fan-only comparison or heat rejection erases benefit |
| Companion Intelligence — Life OS | In Progress; implementation private | [Draft #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10) has verified fictional SQLite crash/revocation tests; zero external actions | Legacy base-store bypass **and revoked-outbox dispatch gap** (v1.3 reproduced on both operating systems), real identity, physical power loss and reviewer benefit TBD | Bind approval to pending fake outbox work; serialize revocation versus dispatch, retire legacy paths, then inject acknowledgment crash | Independent authorization/correction review without exposing private systems | Reframe to read-only if consent/replay boundaries cannot be enforced |
| EPMO Microsoft 365 Automation | Implemented / In Progress — Professional | Main sanitized architecture plus [draft #13](https://github.com/Vermicare/Haridas-Satheesh/pull/13) fictional attrition negative control (44.3% false-positive rate under intentionally selective dropout, 1,000 simulations) | Human outcomes and measured time savings TBD; employer data excluded | Preregister fictional comparator and missing-outcome sensitivity before voluntary review | Public-safe independent evidence supports usefulness | Do not disclose employer data for portfolio proof |
| Hardware & IoT | Prototype / Hardware Architecture | [Draft #7](https://github.com/Vermicare/Haridas-Satheesh/pull/7) synthetic capture preflight and offline flash-probe tests; no physical measurement | Connected board flash identity and genuine 600-second BH1750/SCD40 capture TBD | Read-only flash ID and timestamped dual-sensor log with provenance | Independently reviewable physical capture passes quality gates | Reframe if physical provenance/capture reliability cannot be established |

## October 28, 2026 — main-versus-draft evidence reconciliation

This mainline roadmap previously said CORTEX verified regression and Retail public-data evaluation were pending; that was stale relative to **public, unmerged draft** research. The main branch does not contain the draft implementations. All seven PRs below were independently checked as **open, draft and unmerged**. CI job conclusions were inspected; successful software workflows are not human review, physical measurements, or product validation. **No maturity advancement.**

| Family | Hosted evidence | Boundary / next decisive experiment |
|---|---|---|
| [WBI #16](https://github.com/Vermicare/Haridas-Satheesh/pull/16) | [Frozen cross-OS synthetic reproduction](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40301577095), [real A04T structure](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40589338663), [A04T cross-OS source reacquisition](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40633875375) | A04T has 7 blocks vs A01T/A02T 9; **no EEG decoding**. A04T training SHA-256 independently matched on Ubuntu/Windows (26/26 tests per OS); finish 15 remaining source identities, then frozen matched-coverage evaluation. |
| [Retail #19](https://github.com/Vermicare/Haridas-Satheesh/pull/19) | [Publisher-data run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40561762763) | Predeclared superiority gate failed; post-hoc interval crosses zero. Next: unseen chronological test. |
| [CORTEX #4](https://github.com/Vermicare/Haridas-Satheesh/pull/4) | [Synthetic contract run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40515618065) | No independent semantic reviewers or measured correction burden. |
| [Cooling #6](https://github.com/Vermicare/Haridas-Satheesh/pull/6) | [Fictional order-drift run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40554073145) | Zero real thermal/energy observations; real 600-second logging required. |
| [Companion #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10) | [SQLite process-kill run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40596492153); [revoked-outbox negative control](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40610312405) **116/116 per OS** | A revoked fictional approval still reaches the legacy fake sink; legacy base-store bypass also remains. No real identity/external action. |
| [Hardware #7](https://github.com/Vermicare/Haridas-Satheesh/pull/7) | [Offline flash-probe run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40581214709) | Connected board flash identity and real dual-sensor recording TBD. |
| [EPMO #13](https://github.com/Vermicare/Haridas-Satheesh/pull/13) | [Fictional attrition run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40544802878) | Simulated selection bias, not measured reviewer or employer outcomes. |

**WBI source integrity:** main `synthetic_evaluator.py` blob `2becec81a8002cc5ff2f445889b7617baf9937b9` matches [SYNTHETIC_EVALUATOR.md](benchmarks/wireless-brain-interface/SYNTHETIC_EVALUATOR.md) and [EXECUTION_RECORD.md](benchmarks/wireless-brain-interface/EXECUTION_RECORD.md); preserved synthetic CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`. Do not overwrite it or claim EEG policy validation.

**Four-lens review:** hiring manager — runnable drafts, not merged releases; technical reviewer — clear provenance and negative results but absent human/physical validation; innovation leader — no novelty or patentability conclusion; founder — no validated users, deployment, cost or product readiness. No outreach tracker or employer-confidential material belongs in this public document.


### October 28 — A04T cross-platform training-source reacquisition (no maturity change)

[Draft PR #16](https://github.com/Vermicare/Haridas-Satheesh/pull/16) now includes a separately executed [Ubuntu/Windows A04T reacquisition run](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40633875375): each job passed 26/26 fictional metadata-contract tests and downloaded 37,150,377 official A04T **training** bytes, independently matching the previously observed SHA-256 `15850d81b95fc88cc8b9589eb9b713d49fa071e28adaf32d675b3eaa30591d6e`. Seven blocks (one cue-free baseline, six task blocks) and 288 cue positions were reconfirmed. The code and evidence remain in an **unmerged draft**; metadata-only CI artifacts were uploaded. Same publisher host and same parser mean no publisher signature or independent parser verification. **No decoding, class-label inspection, clinical validation, maturity advance or release.** [Method and verified limitations](https://github.com/Vermicare/Haridas-Satheesh/blob/research/wbi-independent-repro-20261026/benchmarks/wireless-brain-interface/BNCI_A04T_REACQUISITION_V06.md). The next scientific gate is a leakage-safe, held-out real EEG comparison at matched action coverage, after completing source provenance.

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

The frozen WBI synthetic evaluator has already been executed and cross-platform reproduced in [draft #16](https://github.com/Vermicare/Haridas-Satheesh/pull/16). **Do not repeat its first-run milestone or treat structural EEG acquisition as decoding.** Prioritize genuine instrumented Cooling/Hardware dry runs, held-out WBI EEG policy comparison at matched coverage, unseen Retail chronological confirmation and voluntary blinded CORTEX review. Keep drafts explicitly unmerged.


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
