# EPMO v1.1 — selective reviewer attrition negative control (2026-10-27)

**Status:** independent fictional Monte Carlo sensitivity only. **Zero human reviewers, zero external actions, zero employer records.** This does not establish efficacy, real false-approval rates, recruitment feasibility, or sample size. Maturity remains **Research / Simulation**.

## Why this changes the next experiment

The [v1.0 reviewer-power sensitivity](REVIEWER_POWER_V10.md) assumes independent reviewers complete all 13 negative fictional cases. The [v0.9 treatment comparison](REVIEW_TREATMENT_V09.md) plans reviewer-level random assignment. But if reviewers with higher potential false-approval rates disproportionately fail to finish the worksheet arm, comparing only completed reviews can produce **apparent treatment benefit under a true no-effect null**. This is a selection-bias counterexample, not evidence that such dropout will occur.

## Predeclared fictional assumptions

- **Unit:** reviewer, not case; 48 assigned to each arm; 13 oracle-negative fictional cases per reviewer; independent reviewer propensities sampled from a beta-binomial model with *assumed* intraclass correlation 0.10.
- **Control null:** both arms have assumed 20% false-approval probability. Hypothetical-effect scenario uses 20% control versus 10% worksheet probability, without missingness.
- **Missingness mechanisms:** complete cases; 25% random dropout in each arm; or **outcome-dependent selective dropout**: in worksheet arm, 80% dropout when the fictional reviewer would falsely approve at least 4/13 cases, otherwise 5%; in manual arm, 5% dropout regardless of rate. This strong selection mechanism is deliberately adversarial and not an estimated real-world mechanism.
- **Analysis:** deliberately naive *complete-case* two-sided reviewer-level permutation test (199 permutations, p = [1 + as-extreme]/200, alpha 0.05), 1,000 independent Monte Carlo replications per scenario; seed 20261027. Each scenario consumes its own segment of the deterministic random stream. All observations and missingness are simulated.

## Locally executed results (CPython 3.13.5, Linux)

| Fictional scenario | True treatment effect | Null rejection / detection rate | Monte Carlo standard error | Mean observed worksheet-minus-manual false-approval rate | Mean retained manual / worksheet reviewers |
|---|---|---:|---:|---:|---:|
| Complete data, null | 0 | 6.6% | 0.79 percentage points | -0.0017 | 48.00 / 48.00 |
| Random 25% dropout, null | 0 | 5.0% | 0.69 percentage points | +0.0006 | 36.09 / 35.86 |
| Selective worksheet dropout, **null** | **0** | **44.3%** | 1.57 percentage points | **-0.0632** | 45.55 / 34.90 |
| No dropout, hypothetical 20% to 10% improvement | Assumed 10-point improvement | 89.9% | 0.95 percentage points | -0.1004 | 48.00 / 48.00 |

**Interpretation:** under this *invented* selective-missingness mechanism, a naive complete-case test rejects the true null in 443 of 1,000 simulated studies. The simulated 44.3% is **not** an estimate of the actual false-positive rate of the planned study. Even the complete-data null estimate is 6.6%, above the nominal 5% in this finite seeded Monte Carlo; do not treat any scenario as calibrated beyond the reported Monte Carlo uncertainty. Additional 300-replication seeds 1, 2, 3 produced selective-dropout null rejection rates 49.67%, 49.33%, 51.67% respectively. These checks establish that the negative control is not unique to the primary seed; they do not validate the missingness assumptions.

## Reproduce

From `benchmarks/epmo-governance`:

~~~sh
python -B -m unittest -v test_reviewer_attrition_sensitivity_v11
python -B reviewer_attrition_sensitivity_v11.py > REVIEWER_ATTRITION_V11_RESULT.json
~~~

The test suite compares the complete 1,000-replication output to the committed JSON, in addition to nine quick contract and adversarial checks. **Local 10/10 tests passed**, including exact JSON reproduction. The source/result SHA-256 hashes and Python environment are in [the registry](REVIEWER_ATTRITION_V11_REGISTRY.json). Independently inspected [GitHub Actions run #40544802878](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40544802878) passed **174/174 tests on Ubuntu and 174/174 on Windows**, including the v1.1 exact 1,000-replication result check, at executable-unchanged branch commit `ad3527cae8b5d90e8615963448f7d6257ed59068`. Both job logs were inspected. This verifies reproducible fictional software behavior, not model validity or human outcomes. Earlier v1.0 results and stronger evidence are preserved unchanged.

## Decision / next gate

**Do not use v1.0's hypothetical power estimate as a recruitment target or report v1.1 as a measured human result.** Before any reviewer pilot, privately preregister a randomized assignment and consent plan, capture denominators for *all assigned* reviewers, preserve completion/missingness and timestamps privately, define an intention-to-treat primary analysis and explicit bounds/sensitivity for missing outcomes, and report time burden and negative results. Obtain approved consented independent pilot data before selecting realistic attrition, baseline and effect assumptions. Participant data, assignments and outreach remain off public GitHub.

**Four lenses:** hiring—demonstrates refusal to claim fictional efficacy; technical—explicitly stress-tests exchangeability under selective missingness; innovation—tests whether review aids may discourage completion; founder—no user demand, adoption or ROI evidence. No maturity change, release, real external action or human-study commitment.
