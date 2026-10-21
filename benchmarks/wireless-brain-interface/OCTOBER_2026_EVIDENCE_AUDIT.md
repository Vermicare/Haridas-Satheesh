# WBI — October 2026 evidence audit

**Stage: Research / Simulation.** No real EEG, clinical, or device validation.

The committed [execution record](EXECUTION_RECORD.md) reports two same-runtime deterministic executions, identical risk–coverage CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a`, and contract tests passing. [SYNTHETIC_EVALUATOR.md](SYNTHETIC_EVALUATOR.md) still calls execution unverified: its status is stale; the execution record is stronger, but does not establish independent cross-environment reproduction.

The synthetic authorization gate had higher incorrect-action risk than simple confidence abstention at *different* coverage (0.1571 at 0.5833 vs 0.1301 at 0.5125). No superiority claim follows. An additional local-only October 22 negative-control package (`wbi_drift_negative_control_v03_2026-10-22.zip`, not committed) reported only small effects of permuting fictional drift scores; it is a research lead, not published validated EEG evidence.

**Next:** independently reproduce frozen evaluator in clean environments; perform preregistered subject/session-separated public EEG comparisons at matched coverage. **Reframe** if drift gate is Pareto-dominated by confidence abstention across repeated conditions. Unknown real EEG metrics: **TBD**.
