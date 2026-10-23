# WBI — Multi-regime synthetic negative controls (2026-10-24)

**Stage:** Research / Simulation, unchanged. **Evidence:** executable fictional simulations only. **No EEG subjects, clinical evidence, physical hardware, or operational safety claims.**

## Hypothesis and frozen protocol

Does the drift-aware authorization gate reduce incorrect-action risk relative to simple confidence abstention at approximately comparable held-out coverage, across changes to the usefulness of the fictional drift signal?

This is a *stress diagnostic*, not a claim of superiority. It imports the original frozen [synthetic evaluator](synthetic_evaluator.py) at Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9` and the separate [coverage-target diagnostic](coverage_target_diagnostic.py) unchanged.

**Predeclared design in executable constants:** five independent calibration/test seed pairs `(1103,2103), (1117,2117), (1129,2129), (1143,2143), (1151,2151)`; 240 fictional rows per split; calibration coverage targets 0.30/0.50/0.70; absolute held-out coverage tolerance 0.05. The four drift-score regimes, applied independently to calibration and test without inspecting labels, are:

1. **Original:** existing synthetic drift-score generator.
2. **Permuted:** shuffle drift scores within each split (preserves score distribution, weakens segment association).
3. **Inverted:** replace every score with `1 - score` (deliberately misleading signal).
4. **Constant:** set all drift scores to 0.5 (uninformative control).

Both policies choose thresholds using only calibration probabilities and drift scores. Held-out labels are accessed **only** for scoring. The diagnostic suppresses risk deltas when test coverage differs by more than 0.05 or either policy takes no actions. The 60 operating-point comparisons share base rows across regimes and are **not independent observations**.

## Executed local synthetic result

CPython 3.13.5, Linux, standard library only. Eleven new regression tests passed. The JSON report was deterministic across local reruns. These are local checks against a reconstructed interface; the public GitHub CI is the authoritative test against the exact committed sources.

| Drift-score regime | Comparable / total | Gate better | Gate worse | Tie | Mean gate − confidence incorrect-action risk, comparable only |
|---|---:|---:|---:|---:|---:|
| Original | 9 / 15 | 3 | 6 | 0 | +0.036554 |
| Permuted | 10 / 15 | 2 | 8 | 0 | +0.089641 |
| Inverted | 8 / 15 | 1 | 7 | 0 | +0.137443 |
| Constant | 15 / 15 | 0 | 0 | 15 | 0.000000 |
| **Total** | **42 / 60** | **6** | **21** | **15** | **Do not pool correlated regimes** |

**Negative finding:** Under these fictional conditions, the drift gate more often increases than decreases incorrect-action risk among coverage-comparable operating points. An uninformative constant drift score produces identical decisions under both policies. This challenges the benefit of the current *synthetic* drift gate, not the feasibility of brain interfaces or real EEG decoding. The result is not a hypothesis test or an estimated clinical effect.

## Reproduce / 30–60-second demonstration

From `benchmarks/wireless-brain-interface/`:

```sh
python -m unittest -v test_coverage_target_diagnostic.py test_synthetic_regime_stress.py
python synthetic_regime_stress.py --out synthetic_regime_stress.json
sha256sum synthetic_regime_stress.json
```

Expected Linux CPython 3.13.5 local JSON SHA-256: `d17b5e01c5d47d9fe1a6c2adaf564d30a0a4c75cc6849d24144fcad642158db1`. The JSON contains all seed pairs, thresholds, counts, mismatch exclusions, per-case held-out risk and a machine-readable summary. GitHub CI reruns twice per OS and preserves result artifacts; confirm CI outcome before claiming cross-platform reproduction.

## Failure, learning, and next decision gate

- **Failure:** 18 of 60 candidate comparisons did not satisfy the declared held-out coverage tolerance. Exclude them; do not imply equal coverage or favorable gate risk.
- **Learning:** A drift score's numerical presence is not evidence of useful error detection. Inverted/permuted signals are negative controls; all regimes reuse the same fictional generator and are correlated.
- **Decision:** retain Research / Simulation; do not merge or release as validated performance. Consider **reframing the drift gate as an unproven optional diagnostic** if it remains dominated after capacity-matched threshold grids, paired uncertainty analysis, independent generators, and real subject/session-separated EEG.
- **Next:** preregister an external public EEG dataset and held-out subject/session split, calibration budget, baselines, operating coverage and stop rule **before** accessing test labels. Real EEG, streaming latency, action utility, generalization and safety: **TBD**.

## Review lenses and boundaries

Hiring manager: reproducible negative results rather than activity counts. Technical reviewer: inspect fixed seeds, leakage guards, per-case thresholds and excluded comparisons. Innovation leader: an explicit stop/reframe decision. Founder: no product, clinical, novelty, patentability, deployment, or user-value claim.

No private identities, company systems, personal sensor readings, contact lists, credentials or collaborator tracking are included.
