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


### October 27, 2026 — WBI publisher archive integrity and held-out-label firewall (draft PR #16)

**Strongest evidence unchanged:** cross-platform reproducible **synthetic** evaluator, not public EEG validation. New [source-archive preflight](benchmarks/wireless-brain-interface/bnci2a_source_archive_preflight.py) plus [14 synthetic negative-control tests](benchmarks/wireless-brain-interface/test_bnci2a_source_archive_preflight.py) reject malformed/missing GDF sessions, corrupt CRC, path traversal, duplicate members, symlinks, unexpected files and embedded evaluation-label MAT files. [Registry](benchmarks/wireless-brain-interface/BNCI2A_SOURCE_ARCHIVE_V01_REGISTRY.json) preserves code Git blobs, local run conditions and unknowns; [hosted CI #40451014392](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40451014392) **passed 14/14 archive and 9/9 fictional split tests on Ubuntu and Windows**; both job logs inspected, original frozen evaluator blob and CSV SHA-256 unchanged. Official source confirms evaluation GDF cues are unlabeled and separate E class labels must remain outside calibration. **Largest gap:** official ~420 MB archive not acquired here; all actual source hashes, event/trial counts and EEG outcomes **TBD**. **Next evidence-producing experiment:** acquire publisher archive, verify SHA-256 and actual source-derived T/E event metadata, freeze the decoder/thresholds and only then score E labels separately. **Advance** only on reproducible real EEG matched-coverage evidence with subject-aware uncertainty; **reframe** if drift gating adds no benefit over simple confidence abstention. **Stage remains Research / Simulation**. No claims of idle false-action safety, clinical validity, or real device operation.

### October 27, 2026 — WBI ZIP document-integrity correction (draft PR #16)

**Verified software negative control:** the earlier ZIP preflight streamed GDF files but did not read permitted `.txt`/`.md`/`.pdf` members, leaving their CRC unchecked. The revised no-extraction validator now streams and hashes allowed documents and rejects a deliberately corrupted README ZIP payload. [Execution record](benchmarks/wireless-brain-interface/ZIP_DOCUMENT_CRC_V02.md) and [registry](benchmarks/wireless-brain-interface/BNCI2A_SOURCE_ARCHIVE_V02_REGISTRY.json) preserve exact source/test blobs and [GitHub Actions #40474963906](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40474963906): **17/17 archive and 9/9 fictional split tests passed on each of Ubuntu and Windows**. The frozen September synthetic evaluator source and CSV hash are unchanged.

**Stage:** Research / Simulation, unchanged. **Strongest evidence:** cross-OS synthetic evaluator and integrity-contract tests, *not* EEG. **Largest gap:** no official archive acquired or authenticated, no real event/trial metadata, no held-out EEG outcomes. **Next experiment:** obtain the publisher's GDF archive and record source URL, terms and SHA-256, validate source-derived metadata, freeze the decoder and only then score held-out E labels in an isolated step. **Advance only** on independently inspectable matched-coverage public EEG risk–coverage with subject-level uncertainty; **reframe** drift-specific claims if confidence-only abstention performs as well. No clinical, live-device or source-authenticity claim.

### October 27, 2026 — WBI first real upstream MAT source-byte acquisition (draft PR #16)

**Decision-changing source split:** [BNCI Horizon 2020](https://bnci-horizon-2020.eu/database/data-sets) provides individual **MAT** files for BNCI2014_001 under its catalog's CC BY-ND 4.0 notice, whereas the original competition route provides a **GDF ZIP**. The existing GDF ZIP preflight must **not** be used to validate the MAT route.

**New strongest acquisition evidence:** [Actions #40490939415](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40490939415) passed 10/10 synthetic source-contract tests and twice streamed the *actual upstream* **A01T.mat** training-session file on GitHub-hosted Ubuntu/Python 3.13.16. Both successful fetches independently calculated **42,806,453 bytes**, MATLAB 5 signature, and SHA-256 `054f02e70cf9c4ada1517e9b9864f45407939c1062c6793516585c6f511d0325` at the same tested commit; both job logs inspected. No raw EEG, signal samples or E labels were saved or uploaded; artifacts contain metadata only. [Protocol](benchmarks/wireless-brain-interface/BNCI_MAT_SOURCE_PROBE_V01.md) · [registry](benchmarks/wireless-brain-interface/BNCI_MAT_SOURCE_PROBE_V01_REGISTRY.json) · [source](benchmarks/wireless-brain-interface/bnci2014_001_source_probe.py).

**Largest gap:** 17 remaining source sessions, genuine signal/event metadata, held-out decoder/policy results, external review and independent publisher-signed reference checks are **TBD**. Two matching fetch hashes show reproducible source-byte identity, **not** dataset authenticity, decoding accuracy, motor-imagery safety, rest false-action safety or clinical performance. The frozen synthetic evaluator remains the strongest *policy* evidence.

**Next experiment:** acquire/hash the other 17 T/E files without redistribution, pin a MAT loader, derive actual run/trial metadata without E label leakage, validate the predeclared 18 folds, freeze decoding and action thresholds, then score held-out E at matched coverage with subject-level uncertainty. **Advance** only on independent real-data policy comparison; **reframe** if drift gating cannot outperform confidence abstention at comparable coverage. **Stage remains Research / Simulation**; PR stays draft/unmerged.

### October 27, 2026 — WBI real A01T MAT run structure (draft PR #16)

**Maturity unchanged: Research / Simulation.** [Hosted Actions #40506426387](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40506426387) passed 7/7 fictional structural tests and read the previously hashed, real **A01T training** file using pinned NumPy 2.3.3 / SciPy 1.16.2 / Python 3.13.16. The source hash matched the prior acquisition. **New real-source finding:** the file has **9 MAT blocks: 3 cue-free baseline blocks followed by 6 task blocks of 48 cues each (288 total)**, 25 channels at 250 Hz. MAT block indices must not be confused with task-run indices: task run 1 is block 3 (zero-based) in this file. [Full evidence](benchmarks/wireless-brain-interface/BNCI_MAT_RUN_METADATA_V02.md) · [registry](benchmarks/wireless-brain-interface/BNCI_MAT_RUN_METADATA_V02_REGISTRY.json).

**Largest gap:** the other 17 files, independent source authentication, actual E-session label isolation, decoder performance and matched-coverage false-action risk are **TBD**. **Next:** hash and inspect remaining files individually, map baseline versus cued blocks, freeze all preprocessing/calibration/action-policy decisions before held-out E scoring. **Advance only if** independently reproducible subject/session evidence establishes defensible matched-coverage benefit; **kill/reframe drift-specific claims** if no benefit over confidence-only abstention. This metadata milestone is **not** EEG decoding or clinical validation. No raw EEG, class labels, E-session files, employer data or personal information published; no merge or release.


### October 28, 2026 — WBI A02T real-source metadata fail-closed acceptance (draft PR #16)

**Stage: Research / Simulation; unchanged.** The prior A02T inspector could exit successfully while reporting a malformed fictional block pattern (`six_task_runs_48_cues_each: false`), so a green source-fetch workflow alone was not a structural acceptance decision. A separate [fail-closed A02T metadata gate](benchmarks/wireless-brain-interface/bnci_a02t_structural_gate_v04.py) now rejects mismatched pinned source bytes/hash, incorrect nine-block order/counts, unexpected channels/sample rate, missing privacy/provenance flags and unsupported performance claims **before** artifact upload. Its [15 synthetic adversarial tests](benchmarks/wireless-brain-interface/test_bnci_a02t_structural_gate_v04.py) and the original 7 inspector tests passed in [GitHub Actions #40571300834](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40571300834), commit `63a2c964f7cb40087876f6b8b3eae22560a7a4b7`; the real A02T source matched its previously observed 43,068,077-byte SHA-256 `5ddd5cb520b1692c3ba1363f48d98f58f0e46f3699ee50d749947950fc39db27` and **passed the gate**. [Evidence](benchmarks/wireless-brain-interface/BNCI_A02T_METADATA_GATE_V04.md) · [registry](benchmarks/wireless-brain-interface/BNCI_A02T_METADATA_GATE_V04_REGISTRY.json).

**Strongest evidence:** original frozen synthetic policy evaluator reproduced cross-OS; **real-source acquisition/structure evidence** for A01T and A02T only. Neither establishes EEG decoding accuracy. **Largest gap:** the remaining 16 T/E files, source authenticity, leakage-safe held-out evaluation and matched-coverage policy benefit are **TBD**. **Next experiment:** inspect the next T file with the same gate, then complete an 18-file metadata/provenance manifest without peeking at E labels; freeze decoder/thresholds before E scoring. **Advance only** with reproducible subject/session-aware held-out risk–coverage and uncertainty. **Reframe** if drift gating cannot outperform simple confidence abstention at matched coverage. No raw EEG/labels uploaded, physical/clinical claims, merge or release.
