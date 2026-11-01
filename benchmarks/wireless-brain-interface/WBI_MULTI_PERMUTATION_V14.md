# WBI v1.4 — repeated synthetic drift-permutation sensitivity

**Evidence date:** 2026-11-01 UTC. **Stage:** Research / Simulation (unchanged). **Evidence class:** fictional, deterministic, post-hoc software stress test. **No real EEG, online authorization, human safety or clinical result.**

## Decision question

The v1.3 diagnostic used one deterministic permutation of synthetic drift per calibration/test seed pair. Was its negative result dependent on that single shuffle? v1.4 keeps the same 200 original synthetic seed pairs and the same **120/240 top-k action budget**, but runs **eight distinct deterministic permutations** of drift within calibration and/or test. Labels, confidence, cohort membership and the original frozen evaluator are unchanged. Calibration-only selection of the drift penalty is preserved. The baseline is confidence-only.

## Reproduction and verified hosted result

- [Evaluator](wbi_v14_multi_permutation.py), [11 regression tests](test_wbi_v14_multi_permutation.py), [read-only cross-platform workflow](../../.github/workflows/wbi-v14-multi-permutation.yml).
- [GitHub Actions run #41322810271](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41322810271), commit `761de946a139097d994edfb2274b121bbe48fa63`: **Ubuntu and Windows SUCCESS**; **11/11 tests per OS**; both original job logs inspected.
- Original frozen evaluator blob: `2becec81a8002cc5ff2f445889b7617baf9937b9` (unchanged; checked by workflow).
- Source v1.4 Git blob: `4d11cd7bc03da69e224618199211f15fde1f01f5`; test Git blob: `431689d876a26f97247d99e81580855cefc8c030`.
- Python 3.13 on GitHub-hosted `ubuntu-latest` and `windows-latest`; dependency-free standard library; GitHub Actions runner image patch versions are not independently pinned. Two aggregate-only workflow artifacts were uploaded (Ubuntu ID `13090370584`, Windows ID `13090051297`); artifact ZIP bytes were **not independently downloaded/rehashed** in this run.
- For local reproduction from `benchmarks/wireless-brain-interface` on the research branch:

```bash
python -B -m unittest -v test_wbi_v14_multi_permutation.py
python -B wbi_v14_multi_permutation.py --pairs 200 --repeats 8 --output v14_result.json
```

The command refuses to overwrite an existing output. Source Git blob is verified before evaluator import. Permutation seeds: `1400000 + 20000*repeat + 2*pair` (plus 1 for test); each repeat has 200 seed pairs.

## Observed fictional results

Across 200 original pairs (24,000 acted rows per policy), the original informative-drift case reproduces **3,716 confidence-only errors versus 3,645 drift-penalty errors** (candidate minus baseline **−71**), matching v1.2/v1.3.

| Synthetic condition | Repeated aggregate candidate-minus-baseline incorrect selections | Repeats with no advantage |
|---|---|---:|
| Drift permuted separately in calibration and test | **+18 to +68**, median **+35.5** | **8/8** |
| Calibration drift informative, test drift permuted | **+113 to +184**, median **+134.5** | **8/8** |

Each condition uses exactly the same confidence-only baseline per seed pair; repeated shuffles alter **drift values only**. The result indicates that the synthetic advantage is contingent on a drift/error association surviving into test. **This is not an inferential permutation test**: the seed pairs, generators, policy family and analysis were chosen after earlier results, the repeated shuffles share rows, and there is no p-value, confidence interval, independent human sample or real-EEG effect. The cohort top-k ranking sees all test-row features before selecting actions, so it is **not an online-feasible permission-to-act gate**.

## Evidence gates and failure/learning

**Strongest evidence:** unchanged frozen synthetic evaluator and reproducible cross-platform v1.4 repeated negative controls. **Largest gap:** independently authenticated longitudinal EEG, prospective held-out event/recording pairing and an online-feasible, matched-coverage policy with drift calibration under shift remain **TBD**.

**Next experiment:** independently reacquire and authenticate original Zhou2020 S01 recording bytes, verify acquisition chronology and event-to-recording pairing, freeze the unseen session protocol, and test a causal/online threshold policy against confidence-only abstention at actual matched coverage. Do not use these synthetic results as EEG evidence.

**Kill/reframe:** if real unseen-session drift is uninformative, miscalibrated or worse than confidence-only at comparable useful-action retention, keep confidence-only abstention and stop describing drift as a safety benefit. No maturity advancement, release, merge, patentability, real users or deployment.

**Four lenses:** hiring manager—negative result preserved; technical reviewer—exact seed formulas and immutable evaluator; innovation leader—drift informativeness is a prerequisite rather than a benefit; founder—no product or safety claim without authentic longitudinal signals and external review. No employer data or private collaborator tracking.
