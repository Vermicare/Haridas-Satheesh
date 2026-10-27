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
| Companion Intelligence — Life OS | In Progress; private implementation; public fictional Simulation/contract evidence only | Draft [PR #10](https://github.com/Vermicare/Haridas-Satheesh/pull/10): v0.2 fictional approval negative controls, v0.3 SQLite idempotent receipt tests, v0.4 ambiguous-evidence checks; [v0.5 correction ledger](benchmarks/companion-life-os/CORRECTION_LINEAGE_V05.md) has two local 18/18 runs and [cross-platform CI 49/49](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40148356063) using a **test-seeded** original receipt; [v0.6 integration](benchmarks/companion-life-os/ACTUAL_RECEIPT_INTEGRATION_V06.md) invokes the actual v0.3 fictional receipt producer; [v0.7 outbox](benchmarks/companion-life-os/FICTIONAL_OUTBOX_CRASH_WINDOW_V07.md) tests a separate fictional sink, crash/retry, and the non-idempotent duplicate-effect negative control | Real identity/consent, trusted clock, actual adapter effects and reversal, independent review, tamper resistance and reviewer burden all **TBD**; v0.3→v0.5 fictional interface integration is now exercised | [v0.6 end-to-end fictional receipt/correction tests](benchmarks/companion-life-os/ACTUAL_RECEIPT_INTEGRATION_V06.md) now pass 57/57 on each OS at [verified executable CI head](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40181623928); v0.7 local fictional outbox tests 13/13 passed with one idempotent fake sink row after crash/retry, but a deliberately non-idempotent fake adapter produced two effects; next add authenticated sandbox identity, trusted clock, and independent adapter acknowledgment | Advance only after independently reproducible sandbox identity-bound authorization, durable correction/receipt integrity and measured review burden; do not infer private-system effectiveness | Reframe as read-only advisory if authenticated safe action/reversal cannot be achieved or complexity exceeds measured value |
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


## Draft-branch reconciliation — 2026-10-25

The Companion v0.5 correction experiment above is on **draft PR #10**, not merged to main. Its original receipt is test-seeded, and cross-platform v0.5 CI passed at code head `c3693707` (49 tests per OS); it is not an integrated or production approval/reversal system. WBI's main-roadmap priority text above also predates the stronger synthetic reproductions and single-file real EDF structural evidence recorded in [draft PR #5](https://github.com/Vermicare/Haridas-Satheesh/pull/5); those results do not establish real EEG decoding or longitudinal validation. Do not discard or overwrite that verified synthetic evidence during future reconciliation.

## Companion integration evidence — 2026-10-25

Draft PR #10 now contains an executable v0.3 original-receipt → v0.5 correction integration and 8 fictional-only regression cases. The previous v0.5 test-seeded evidence remains intact; do not rewrite its original provenance. This is not authenticated consent, real action reversal, or security validation. Executable-head [CI #40181623928](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40181623928) passed 57/57 tests per OS; subsequent evidence-document commits are not themselves cross-platform validation. **No maturity change.**


## Companion sink contract reconciliation — 2026-10-26

On **draft PR #10 only**, [v0.9 independent fake-sink integrity](benchmarks/companion-life-os/FICTIONAL_SINK_INTEGRITY_V09.md) adds three reproduced before-fix false-acceptance controls (missing action, blank decision, corrupted stored acknowledgment). [Red CI #40334808905](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40334808905) had three expected failures among 79 tests on each OS; [green CI #40334887066](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40334887066) passed **79/79 on Ubuntu and Windows** at corrected code head `450d395f08363cd7fafec8193fef817cebfc4425`. Earlier v0.7/v0.8 verified results are preserved. This does not change the public **Simulation / fictional software-contract** boundary or private implementation status. Strongest evidence: cross-platform negative controls and idempotent fake-sink replay. Largest gap: trusted identity/time, real adapter semantics, independent reviewer burden. Next: [Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11) sandbox identity issuance and adversarial review. Reframe to read-only advisory if identity-bound safe action is too costly or cannot be demonstrated. No merge or release.

## Companion signed-sandbox evidence — 2026-10-27 (draft PR #10 only)

**Strongest new evidence:** [v1.0 registry](benchmarks/companion-life-os/SANDBOX_SIGNED_BOUNDARY_V10_REGISTRY.json) and [cross-platform run #40428436801](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40428436801) show **94/94 tests on each OS** for the fictional signed-issuer identity/approval boundary, preserving earlier v0.1–v0.9 evidence. The public maturity remains **fictional Simulation / contract testing**; the private implementation is unassessed. This does not change the earlier flagship queue's mainline status or imply a production agent.

**Largest gap:** test-only HMAC keys and caller-provided clock do not authenticate a real person, establish consent, guarantee durable revocation, prove physical crash recovery, or establish real connector semantics. Reviewer error/time and real benefit are **TBD**.

**Next experiment:** [Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11) — independently reviewed identity-provider/trusted-clock sandbox with signed approval revocation, concurrent restart/crash tests and blinded reviewer burden comparison. **Advance only** after independent evidence of identity-bound authorization, acceptable reviewer burden and reversible action receipts; **kill/reframe** to read-only advice if safe authorization/reversal is infeasible or costs exceed measured value. No release, pilot, product or real integration claims.

## Companion revocation gate — 2026-10-27 (draft PR #10 only)

**Current maturity:** private implementation **unassessed**; public evidence remains **fictional Simulation / software-contract testing**. This addendum does not modify the main-branch flagship queue or imply a real agent.

**Strongest evidence:** [v1.0 signed-sandbox cross-platform CI](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40428436801) remains preserved. [v1.1 revocation protocol](benchmarks/companion-life-os/FICTIONAL_REVOCATION_V11.md) adds an executable baseline negative control: the fictional v1.0 signed path accepts an approval withdrawn by the test harness, whereas a new SQLite `BEGIN IMMEDIATE` revocation-aware path rejects post-revocation use without erasing earlier receipts. An intermediate [109-test CI run #40498978104](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40498978104) passed both OS targets, but further negative testing reproduced an inherited unguarded `execute` method that accepted a revoked fictional approval. The new subclass now rejects that direct path; [final CI #40499334471](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40499334471) passed **110/110 tests on Ubuntu and 110/110 on Windows** at executable commit `b725bac8a2623c1a197f0803c78b518a414d7af9`, both logs inspected, both demo artifacts uploaded. **Residual gap:** separate use of the legacy base class remains possible, so global revocation is unproven. The first Windows run [#40498874654](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40498874654) failed two fixture cleanup cases due to unclosed SQLite handles; the test correction is preserved, not concealed.

**Largest gap:** the revocation operator, test HMAC issuer, clock and database filesystem are not independently trusted; no real human authentication, consent, actual connector, power-loss guarantee, external review or measured reviewer time. **Next decisive experiment:** separate trusted test IdP/clock and authenticated revocation operator, then controlled process-kill, tamper and blinded review-burden tests ([Issue #11](https://github.com/Vermicare/Haridas-Satheesh/issues/11)). **Advance only** with independent identity-bound authorization and measured burden, preserving reversible receipts. **Kill/reframe** to read-only advice if revoked approvals can still authorize new effects or if credible identity/reversal is infeasible. No release, pilot or product claim.


## 2026-10-28 — Companion fictional process-kill durability gate (draft PR #10 only)

**Current public maturity:** fictional software-contract simulation; private implementation not evaluated. **Strongest new evidence:** [cross-platform Actions #40596492153](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40596492153) passed 114/114 tests on Ubuntu and 114/114 on Windows, including four actual disposable-child-process termination tests at SQLite commit boundaries. [Protocol](benchmarks/companion-life-os/PROCESS_KILL_CRASH_WINDOW_V12.md) and [registry](benchmarks/companion-life-os/PROCESS_KILL_CRASH_WINDOW_V12_REGISTRY.json) retain provenance and explicit unknowns. No physical power cut, real authentication, consent, external effect or product evidence.

**Largest gap:** independent legacy `FictionalDurableStore` callers can bypass the revocation-aware v1.1 wrapper; test-harness keys and clock are untrusted. **Next decisive experiment:** in a separately versioned fictional adapter, deny every legacy direct write path and test the outbox/ack crash window with an independent fake sink. **Advance only when:** independently reproducible bounded authorization, durable receipt/revocation and all execution entry points are covered, then obtain real identity/consent and independent review before any real pilot. **Kill/reframe:** retain read-only advisory behavior if bypass-free, revocable authorization cannot be demonstrated without unacceptable complexity. No maturity advancement, merge or release.
