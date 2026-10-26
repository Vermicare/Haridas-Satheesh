# Portfolio R&D Roadmap

This roadmap is an evidence-gated control document for the public portfolio. It does **not** upgrade a project's maturity by itself. Advancement requires reproducible or independently inspectable evidence.

## Stage gates

**Idea → Research → Simulation → Prototype → Bench Validation → External Review → Real-world Pilot → Product Candidate**

A project may skip a gate only when existing evidence genuinely satisfies that gate's intent. A project can also move backward, merge, or be archived when evidence weakens the thesis.

## Flagship evidence queue

| Project | Current public maturity | Strongest public evidence | Biggest evidence gap | Highest-value next action | Advance only when | Kill / reframe trigger |
|---|---|---|---|---|---|---|
| Wireless Brain Interface | Research / Simulation | Documented simulated EEG + ECG-style architecture; explicit separation of decoding, uncertainty, safety gating and action | A deterministic synthetic selective-action evaluator is committed, but clean-run reproducibility/results and a public real-EEG benchmark are not yet verified | Execute the committed Issue #3 evaluator in a clean environment twice; verify contract tests and byte-identical risk–coverage output; preserve the benchmark artifact; then connect the frozen evaluator unchanged to longitudinal public motor-imagery EEG | Clean deterministic reruns pass the evaluator contract and preserve reproducible synthetic outputs; then reproducible public-data runs compare the authorization gate fairly with both ungated decoding and simple abstention at comparable coverage | Reframe if safety gating provides no useful false-action reduction after accounting for lost useful actions, or if the claimed contribution collapses into established methods |
| Retail Demand Intelligence | Research / Architecture | [Pinned real TRAIN-only execution, 2026-10-26](benchmarks/retail-demand/observable_baseline/PINNED_TRAIN_EXECUTION_2026_10_26.md): GitHub Actions [#40316866555](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40316866555) verified publisher-reported TRAIN Parquet SHA-256, exported 4,500,000 rows and completed frozen three-fold evaluation; selected series has **10 in-stock scored days**, seasonal-naive MAE **0.56** versus stockout-history MAE **0.67** (worse by 19.6%). [Machine record](benchmarks/retail-demand/observable_baseline/PINNED_TRAIN_EXECUTION_2026_10_26.json); prior synthetic integrity CI retained | Single selected series, 11 censored days excluded, no uncertainty or independent rerun; **not** official publisher held-out 90/7; latent demand, decision and revenue uplift **TBD** | Preregister and independently reproduce multi-series official held-out evaluation with frozen cohort selection, in-stock denominator, simple seasonal and daily-count stockout baselines, uncertainty and failure analysis | Only advance with repeatable real held-out improvements and measured decision relevance under matched conditions; one train-only smoke cannot advance | Reframe if stockout correction does not consistently outperform simpler baselines on matched eligible observations, or added complexity has no decision benefit |
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

The next evidence gate is **Wireless Brain Interface held-out decoding with rest-aware evaluation**. [Draft PR #5](https://github.com/Vermicare/Haridas-Satheesh/pull/5) reports reproducible synthetic evaluator CI, independent EDF+ annotation-reader agreement and a publisher companion-file discrepancy; these are **draft-branch evidence only**, not merged main-branch capabilities or real EEG decoding accuracy. Freeze subject-disjoint preprocessing, train/calibration/test partitions, rest exposure denominators and matched imagery coverage; then compare ungated, confidence-abstention and authorization-gated policies on held-out subjects. Retain negative results and do not advance maturity without demonstrated real-data value.

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


## October 26, 2026 — Retail v1.0 horizon-boundary regression (draft branch)

[Reproducible evidence and failure log](benchmarks/retail-demand/observable_baseline/HORIZON_BOUNDED_SELECTION_V10.md) · [machine-readable registry](benchmarks/retail-demand/observable_baseline/HORIZON_BOUNDED_SELECTION_V10_REGISTRY.json). A fictional 84-day negative control exposed an erroneous cohort rejection caused by a missing day **after** the last scored horizon. The first correction exposed a separate selected-series API regression; both failures are preserved. Final code-bearing [CI #40237113875](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40237113875) passed **71/71 tests on Ubuntu and Windows**. No publisher Parquet or real forecasting benchmark was executed; real-data metrics remain **TBD**, stage **Research / Architecture**. Next: acquire and checksum publisher data, verify stockout semantics, run chronological baseline and independently review PR #9 before merge.


## 2026-10-26 — Retail publisher split contract (draft PR #9)

The official [FreshRetailNet-50K dataset card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K) has separate 4.5M-row train and 350k-row eval splits, equivalent to 90 + 7 days per 50,000 store-product series. The draft retail pipeline's origins 42/56/70 are **within-training rolling backtests**, not the publisher's held-out evaluation. [Publisher split preflight v1.1](benchmarks/retail-demand/observable_baseline/PUBLISHER_SPLIT_PREFLIGHT_V11.md) now checks fictional date manifests for 90/7 chronology, boundary overlap/gaps and declared fitting-date contamination. Twelve fictional tests passed twice in clean Linux directories; GitHub CI for the latest commit remains TBD. This is *not* real-data validation and does not exclude feature leakage. **Stage unchanged: Research / Architecture.** Next: pin and verify both official Parquet splits, run identity-bound per-series checks, freeze training-only preprocessing, then score held-out eval against publisher and seasonal-naive baselines. **Reframe** if actual data contradict assumptions or corrected demand does not improve preregistered metrics.

## 2026-10-26 — Retail real-data execution attempt and prior-art decision (draft PR #9)

[Decision and primary sources](benchmarks/retail-demand/observable_baseline/PRIOR_ART_DECISION_2026_10_26.md) document Azar's peer-reviewed **2026-08-30** leakage-free FreshRetailNet forecast-to-order study. This existing published work means a generic stockout-aware, leakage-free forecasting pipeline **cannot be presented as novel**. A falsifiable follow-up is exact-hour status-aware recovery versus the simpler daily-count and seasonal baselines under the same frozen 90/7 evaluation; no benefit has been measured here.

A new [publisher-pinned train-only GitHub Actions smoke workflow](.github/workflows/retail-pinned-data.yml) on this draft branch is intended to download the exact official train snapshot, verify SHA-256, execute the existing exporter and SQLite rolling-origin evaluator, and preserve **only** JSON evidence. **At publication, no matching hosted run or downloaded-byte verification is observable: CI execution TBD, actual real-data scores TBD.** Even a passing train-only rolling smoke is **not** the publisher's official held-out 90/7 benchmark and cannot be compared to the paper's WAPE. The strongest existing synthetic CI results remain valid but do not satisfy this real-data gate. **Maturity unchanged: Research / Architecture.** If the publisher bytes/schema cannot be verified, preserve the failure and do not substitute a synthetic source. If exact-hour recovery offers no gain at matched evaluation conditions, reframe the method.


## 2026-10-26 — Retail first publisher-pinned TRAIN-only result (draft PR #9)

[Full evidence, negative result and limits](benchmarks/retail-demand/observable_baseline/PINNED_TRAIN_EXECUTION_2026_10_26.md) · [machine-readable summary](benchmarks/retail-demand/observable_baseline/PINNED_TRAIN_EXECUTION_2026_10_26.json) · [successful GitHub Actions run #40316866555](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40316866555). The runner locally verified the exact publisher-reported train Parquet SHA-256, exported **4,500,000 rows**, and completed the frozen 42/56/70-day TRAIN-only rolling origins. One training-selected series (store 0, product 104) supplied only **10 in-stock test days**; **11 stockout days were excluded**. Day-weighted in-stock MAE: last observed **0.83**, seasonal naive **0.56**, causal stockout-history **0.67**. Thus the more complex correction is **19.6% worse than seasonal naive** on this limited cohort; fold three is the largest reversal. This is a real-data negative result, not a generalized conclusion or latent-demand test. Source-origin independent attestation, independent rerun, official 90/7 held-out accuracy, statistical uncertainty and intervention outcomes remain **TBD**. Retain Research / Architecture; do not merge or release as validated forecasting. Next: frozen multi-series official held-out comparison, with daily-count and seasonal baselines, matched in-stock denominators, uncertainty and independent rerun. Earlier dated entries describing the train download as pending are historical and are superseded by this result.

## October 26, 2026 — Retail official publisher holdout (draft PR #9)

**Stage unchanged: Research / Architecture.** [Verified GitHub Actions #40342565683](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40342565683) executed the pinned **90-day TRAIN + seven-day EVAL** FreshRetailNet split with publisher-reported train/eval SHA-256 checks and **512 preselected train-only series**. The frozen evaluator passed 10/10 fictional contract tests and scored **2,183 uncensored days**, excluding 1,401 stockout-censored days. Day-weighted MAE: **last observed 0.478562**, **seasonal naive 0.485180**, **causal stockout-history 0.479906**. Correction was **1.09% better than seasonal naive**, but **0.28% worse than last observed**; paired per-series bootstrap interval for correction-minus-seasonal macro MAE **[−0.042840, +0.012164] crosses zero**. This is a **mixed result, not robust superiority**. The earlier single-series train-only negative result is preserved.

**Strongest evidence:** [official held-out execution record](benchmarks/retail-demand/observable_baseline/OFFICIAL_HOLDOUT_V12_EXECUTION_2026_10_26.md), [machine-readable provenance/results](benchmarks/retail-demand/observable_baseline/OFFICIAL_HOLDOUT_V12_RESULT.json), [frozen protocol](benchmarks/retail-demand/observable_baseline/OFFICIAL_HOLDOUT_V12_PROTOCOL.md). **Largest gap:** no lost-demand ground truth, intervention value, store-clustered uncertainty or independent rerun; current bootstrapping assumes exchangeable series. **Next:** independent pinned rerun, store-clustered uncertainty and stronger daily-count baseline on the **same cohort**. **Advance only** on independently reproducible, predeclared decision-relevant gains beyond simple baselines; **reframe** toward stockout observability if improvements vanish or inventory effects cannot be tested. No stage upgrade, release, merge or outreach.
