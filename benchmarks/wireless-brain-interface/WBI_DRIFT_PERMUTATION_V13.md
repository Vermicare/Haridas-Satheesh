# WBI v1.3 — Drift informativeness and calibration-mismatch negative controls

**Evidence date:** 2026-10-30 UTC. **Stage:** Research / Simulation (unchanged). **Evidence:** local deterministic fictional-only execution, not EEG, clinical validation or online authorization. **Hosted cross-platform status:** **PASS**, [GitHub Actions #41117999443](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41117999443), commit `07776d6c546ea359d0c74e31867e5b4944c2e848`, Ubuntu job `124277125530` and Windows job `124277126154`; both logs independently inspected, **8/8 tests per operating system**, frozen evaluator blob check PASS and all three aggregate delta counts reproduced exactly.

## Question and decision

The [v1.2 200-pair result](WBI_MULTI_SEED_V12.md) found 71 fewer wrong top-k selections when a drift penalty was added to confidence. But the original [frozen synthetic generator](synthetic_evaluator.py) **deliberately** makes high-drift segments less accurate. Is the observed advantage dependent on that built-in association?

We held every original prediction, confidence, label, 50% action budget and seed pair fixed. We then applied deterministic independent **within-split permutations of the drift column only**, retaining its marginal values but breaking its row-level association with errors. The penalty weight is always selected on calibration rows only. No test labels are used in selection. The entire design is **post-hoc** and selects the top 120 among a known cohort of 240; it is not an online authorization gate.

## Local reproducible results

Each policy takes exactly **24,000 actions across 200 pairs** (120 test actions/pair). All counts are fictional. Candidate-minus-confidence-only errors:

| Condition | Confidence-only wrong | Drift-penalty wrong | Candidate minus baseline | Pairs better / tied / worse |
|---|---:|---:|---:|---|
| Original informative drift (v1.2 parity) | 3,716 | 3,645 | **−71** (−0.296 percentage points) | 76 / 86 / 38 |
| Independently permute drift in calibration **and** test | 3,716 | 3,773 | **+57** (+0.238 percentage points) | 13 / 153 / 34 |
| Keep informative calibration, permute **test only** | 3,716 | 3,857 | **+141** (+0.588 percentage points) | 39 / 86 / 75 |

In the permuted-both control, calibration selected alpha=0 in **131/200** pairs (versus **64/200** in original). The mismatched test-only condition retained the original calibration choices but produced the largest deterioration.

**Interpretation:** The original improvement is not robust to these feature-informativeness and calibration-shift perturbations. This does **not** prove that drift is useless, quantify a population effect, or establish any EEG finding. One deterministic permutation per pair is a stress test, **not** a permutation-test p-value or confidence interval. It is possible that different synthetic generators or permutations yield different magnitudes or signs.

## Reproduce (30–90 second software demonstration)

From `benchmarks/wireless-brain-interface` on the research branch:

```bash
python -B -m unittest -v test_wbi_v13_drift_negative_controls.py
python -B wbi_v13_drift_negative_controls.py --output v13_result.json
```

The second command refuses to overwrite an existing output. Inspect `cases.*.delta_wrong` and `cases.*.records`. Keep the generated result locally; do not commit private signals. The v1.3 script imports the existing v1.1 ranking and v1.2 seed constants; the original frozen evaluator must pass Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9`. Local reproduction on **CPython 3.13.5 / Linux x86_64** passed **8/8 regression tests**. Cross-platform hosted verification is **PASS** on Ubuntu and Windows; both job logs were independently inspected. This verifies fictional software reproducibility only. [Machine-readable registry](WBI_DRIFT_PERMUTATION_V13_REGISTRY.json) contains the aggregate counts and exact source blob IDs.

## Decision gates and failures

**Strongest evidence:** original synthetic frozen evaluator cross-platform verified separately, exploratory v1.2 result, and this local v1.3 negative control. **Largest gap:** genuine, independently authenticated multi-session EEG with prospective online/matched-coverage policy and drift calibration under shift. **Next experiment:** independently re-acquire Zhou2020 S01, map source-to-events, preregister an *online-feasible* matched-coverage comparison with explicit drift miscalibration controls before seeing held-out labels. **Kill/reframe:** if the drift term does not consistently beat confidence-only on genuinely unseen subjects/sessions, keep the simpler confidence-only abstention policy; never use a cohort top-k diagnostic as a real-time safety authorization gate.

No real EEG was accessed; no physical or clinical measurements, new product, novelty, patentability, deployment, users or maturity advancement are claimed. No employer data, private collaborator tracking or personal information are included.

**Four-lens review:** Hiring manager—negative evidence disclosed; technical reviewer—calibration/test permutations preserve labels and confidence and are executable; innovation leader—drift reliability is a design dependency, not a benefit claim; founder—prioritize independent signals and online constraints before commercialization.
