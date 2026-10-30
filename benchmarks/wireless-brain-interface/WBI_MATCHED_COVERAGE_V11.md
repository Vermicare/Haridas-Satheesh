# WBI v1.1 — exploratory equal-action-budget diagnostic (synthetic only)

**Date:** 2026-10-30. **Maturity:** Research / Simulation, unchanged. **Source:** frozen September synthetic evaluator Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9`; its [original execution record](EXECUTION_RECORD.md) and [contract](SYNTHETIC_EVALUATOR.md) remain unchanged.

## Question and protocol

The frozen September report compares different coverage levels (confidence abstention 0.5125; drift gate 0.5833), so it cannot establish a matched-coverage advantage. This **new post-hoc exploratory diagnostic** compares two *ranking policies* at exactly 25%, 50%, and 75% acted rows:

- Confidence-only score = classifier confidence.
- Drift-aware score = classifier confidence minus `alpha * declared_drift`; select alpha from `[0, .05, .10, .20, .40, .80]` using **calibration labels only**, minimizing calibration incorrect-action count at the same budget, with smaller alpha winning ties.
- For each budget, select the top `k` test scores for each policy. This uses the **unlabeled full test cohort's feature distribution** to set an exact action budget; it is **not** an online policy. Stable input index breaks score ties. Test labels are used only for reporting risk after selection.
- The underlying fictional classifier and fixed seeds are unchanged. This is **not** the original frozen threshold-based gate, a preregistered confirmatory test, or EEG evidence.

## Local independent diagnostic result

An independently assembled local execution on **CPython 3.13.5**, using the exact frozen synthetic evaluator blob, produced:

| Exact test action budget | Calibrated alpha | Confidence-only incorrect | Drift-aware incorrect | Risk difference (drift minus confidence) |
|---|---:|---:|---:|---:|
| 60/240 (25%) | 0.10 | 6/60 (10.00%) | 6/60 (10.00%) | 0.00 percentage points |
| 120/240 (50%) | 0.05 | 16/120 (13.33%) | 13/120 (10.83%) | -2.50 percentage points |
| 180/240 (75%) | 0.10 | 37/180 (20.56%) | 36/180 (20.00%) | -0.56 percentage points |

**Interpretation:** the new *ranking* has a small favorable descriptive result at two budgets on **one deterministic fictional fixture**, and no difference at 25%. No statistical interval, multiple-seed robustness, independent real-signal verification, or online deployment test is claimed. A post-hoc positive point estimate does **not** overturn the original frozen gate's negative/inconclusive comparison. The original threshold-based gate still has **no demonstrated matched-coverage advantage**.

The standalone [diagnostic](wbi_matched_coverage_v11.py), [fictional negative controls](test_wbi_matched_coverage_v11.py) and [cross-platform workflow](../../.github/workflows/wbi-matched-budget-v11.yml) are additive; none changes the frozen evaluator or CSV. Local equivalent-implementation controls passed **8/8**. **Hosted verification is now PASS on both Ubuntu and Windows** at [run #41091908815](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41091908815), head `523e60b6b8976be786cc7a394edeea9de4f5fc9d`: **10/10 negative-control tests per OS**, frozen-fixture diagnostic PASS, and independently inspected job logs show the same 25%/50%/75% incorrect counts (**6/6, 16/13, 37/36**, confidence/drift). The original evaluator blob remains `2becec81a8002cc5ff2f445889b7617baf9937b9` on the research branch.

**Documented failure and correction:** [initial hosted run #41083598639](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41083598639) passed 10/10 tests on each OS, but Windows failed the diagnostic because its checkout had converted the frozen source's LF endings to CRLF; the runtime-computed Git blob was `889b4b4614aa7c2b65932641330c95225c38f71e` instead of the frozen Git blob. A branch-local [`.gitattributes`](../../.gitattributes) rule now enforces `text eol=lf` for **only** `synthetic_evaluator.py`; the workflow path filter was updated to include this rule. **The frozen evaluator itself was not edited or weakened**, and the subsequent hosted run passed both OS jobs. This is checkout-byte reproducibility, not independent EEG validation. GitHub Actions ZIP artifact hashes can differ because ZIP packaging metadata differs; no byte-identical cross-platform ZIP claim is made.

## Reproduce / 30–90 second demo

From repository root with Python 3.13, standard library only:

```bash
python -m unittest discover -s benchmarks/wireless-brain-interface -p 'test_wbi_matched_coverage_v11.py' -v
python benchmarks/wireless-brain-interface/wbi_matched_coverage_v11.py --output wbi_v11_result.json
```

The executable fails closed if the original evaluator's Git blob differs. Verify the exact per-budget counts above; record Python version, repository commit, frozen source blob, action budget, alpha grid and output hash. No datasets or labels are downloaded.

## Evidence gates and four-lens review

**Hiring manager:** executable, small and transparent; no clinical or commercial claims. **Technical reviewer:** check calibration/test isolation, top-k cohort dependence, post-hoc alpha grid, tie behavior and original evaluator blob. **Innovation leader:** a more promising *question*, not an established new method. **Founder:** no safe-actuation, usability, regulatory, or economic basis for deployment.

**Strongest evidence:** one locally reproduced exact-blob fictional matched-budget diagnostic, plus unchanged stronger prior synthetic reproduction. **Largest gap:** independent multi-seed, multi-subject public-EEG matched-coverage evaluation with no label leakage and an online policy that does not require the full future cohort. **Next experiment:** preregister *before new outcome access* a realistic online threshold comparison across held-out subjects/sessions; independently reacquire the Zhou2020 S01 source archive and verify recording-to-event mappings. **Kill/reframe:** if improvement disappears with new seeds, real EEG, matched coverage, or prospective online thresholds, retain confidence-only abstention as the simpler baseline. **Unknowns:** all real-EEG risk, calibration, latency, safety, external-review and clinical metrics = TBD.

No physical actions, employer data, external participants, stage advancement, release, or novelty/patent claim.
