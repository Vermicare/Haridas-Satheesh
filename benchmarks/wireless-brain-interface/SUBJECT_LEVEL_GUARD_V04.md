# WBI — subject-level matched-coverage guard v0.4 (2026-10-26)

**Stage:** Research / Simulation, unchanged. **Evidence:** executable **fictional** paired-policy evaluation contract; no EEG waveform, decoder training, independent human subjects, clinical/device safety, or demonstrated drift-gate benefit.

## Decision-changing failure mode

The [v0.3 common-opportunity evaluator](MATCHED_OPPORTUNITY_CONTRACT_V03.md) correctly withholds a risk difference when the two policies have unmatched imagery coverage *within a recording*. A downstream analysis could nevertheless select only the matched recordings, silently drop difficult subjects, and report an apparently favorable pooled result. Pooling opportunities also hides subject-level heterogeneity.

This additive v0.4 calls the actual v0.3 evaluator for each fictional subject, validates unique \`F###\` identifiers, canonicalizes subject order, and **withholds the entire unweighted subject-mean risk difference** unless all subjects have comparable coverage and the predeclared minimum subject count is reached. It independently reports per-subject imagery coverage gap, incorrect-action risk delta, rest false-action rate delta, and correct-action recall delta. Any rest-rate or recall regression is marked as a tradeoff rather than hidden behind a favorable overall risk difference.

The \`F###\` IDs are fictional repetitions, **not actual independent participants**. The minimum of three is a software smoke-test threshold, not statistical adequacy.

## Reproduce

From \`benchmarks/wireless-brain-interface\`:

\`\`\`sh
python -m unittest -v test_subject_level_v04.py
python subject_level_v04.py > subject_level_v04_demo.json
sha256sum subject_level_v04_demo.json
\`\`\`

**Local CPython 3.13.5/Linux (2026-10-26):** 11/11 tests passed against a separately implemented *local API-compatible stand-in* for v0.3; the exact new source/test Git blob IDs were checked against GitHub after publication. This is **not** evidence that the new tests passed against the actual committed v0.3 implementation; cross-platform GitHub CI is the authoritative integration gate. The deterministic demo has SHA-256 (LF) \`b283d2b543e09b5fe99bf99a7bc3dc427f5153595559053a888e63b175e7ff42\`. In the intentionally unfavorable demo, one of three fictional subjects never acts under the gate, so the aggregate risk difference is \`null\` rather than a misleading number.

**Adversarial cases:** one unmatched subject, insufficient subjects, equal coverage but increased rest actions, wrong-direction imagery/recall regression, duplicate subject IDs, missing policy decision, invalid IDs/tolerances, input-order invariance, deterministic no-EEG demo.

## What this does not prove

- No EEG was acquired or decoded by v0.4. Previously published checksum-verified EDF+ annotation work is separate and remains intact.
- No independent cross-subject performance estimate, confidence interval, causal effect, novelty, medical-device validation or clinical safety is established.
- A complete-looking annotation partition does not prove true T0 boundaries. The observed publisher EDF+/WFDB initial-T0 discrepancy must remain visible.
- The v0.4 contract cannot prove that decisions were made without access to labels or that thresholds were calibrated without test leakage; future real EEG runs must preserve source hashes, preprocessing fit scope, split provenance, decision timing, and frozen thresholds.

**Next evidence gate:** subject-disjoint public EEG decoder decisions with complete T0 exposure, source-level clock reconciliation, calibration-only thresholds, common action opportunities, predeclared coverage tolerance, per-subject results and uncertainty. If matched-coverage advantage disappears or rest false actions increase, **reframe** the gate rather than selecting favorable subjects.

**Four lenses:** hiring—fail-closed comparisons; technical—no post-hoc subject exclusion; innovation—falsifiable heterogeneity; founder—no user benefit or deployment evidence yet. No personal or employer data.
