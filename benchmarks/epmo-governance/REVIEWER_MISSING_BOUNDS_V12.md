# EPMO v1.2 — no-assumption bounds for fictional reviewer attrition (2026-10-28)

**Stage: Research / Simulation (unchanged).** This is an **independent fictional statistical preflight**, not a human pilot, observed false-approval reduction, authenticated approval system, employer result, product or clinical trial. **0 human reviewers, 0 external actions.** No recruitment, identity data, employer process or confidential material.

## Question and preregistered estimand

Does a complete-case comparison identify the difference in average false-approval rates **across all assigned reviewers**, when completion can depend on potential outcomes? The planned two-arm fictional study has 13 oracle-negative decisions per reviewer, with assignment at reviewer level. A completed reviewer's outcome is the number of false approvals divided by 13. An incomplete reviewer's unobserved 13-case outcome is conservatively bounded between 0 and 1; no missing-at-random assumption is made. Partial completions are **not** modeled in v1.2 and would require a separate preregistered handling rule.

For arm `a`, with `N_a` assigned, `n_a` complete and `S_a` total false approvals among completers, the sharp no-assumption finite-sample bounds on the assigned-reviewer mean are:

`L_a = S_a / (13 * N_a)` and `U_a = (S_a + 13*(N_a-n_a)) / (13*N_a)`.

For worksheet-minus-manual difference, the bounds are `[L_worksheet - U_manual, U_worksheet - L_manual]`. Each extreme is attainable by assigning all unobserved reviewer outcomes to zero or one. **These are identification bounds, not confidence intervals or causal effect estimates.** Sampling uncertainty, cluster dependence, noncompliance, partial records, and generalization remain outside this experiment.

## Frozen fictional generator and conditions

- Reuse **unchanged** `reviewer_attrition_sensitivity_v11.reviewer_rate` and `retained` from the existing unmerged [PR #13](https://github.com/Vermicare/Haridas-Satheesh/pull/13), source Git blob `9a30b12c0efad22fe5dcd216f9f9fe6c0ada1367`. New script does **not** change v1.1.
- Deterministic seed `20261028`, 48 **fictional assigned** reviewers per arm, 13 negative fictional cases, 20% assumed true-null error propensity in both arms, assumed intrareviewer correlation 0.10. Second scenario consumes seed+1.
- Scenarios: independent 25% random dropout; v1.1's deliberately adversarial selective worksheet dropout (80% when potential error >=4/13, otherwise 5%; manual dropout 5%). These probabilities are invented, not estimates of actual participation.
- Python 3.13 standard library, no network, no dependencies, no real accounts. Exact arithmetic uses `fractions.Fraction`; output decimals are display-only six-place rounding. Unknown human outcomes `TBD`.
- Local first execution: CPython 3.13.5 Linux; 17/17 new tests passed. Cross-platform verification: [GitHub Actions #40699223219](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40699223219) **passed 191/191 tests on Ubuntu and 191/191 on Windows** at commit `4a7f55a7b7b2bdfb323f25917b17e561f00552ad`, including all 17 v1.2 tests. Both final-head job logs were inspected. This verifies deterministic fictional software behavior, not human outcomes.

## Executed fictional results

| Hypothetical missingness | Completed manual / worksheet (of 48 each) | Naive complete-case worksheet-minus-manual | Sharp assigned-reviewer difference bounds | Includes no benefit? |
|---|---:|---:|---:|---|
| Random 25% | 39 / 34 | +0.001334 | [−0.208333, +0.270833] | Yes |
| Selective worksheet dropout | 45 / 38 | **−0.054431** | **[−0.133013, +0.137821]** | **Yes** |

The selectively missing fictional example appears to favor the worksheet among completers by 5.44 percentage points, but **the assigned-reviewer mean difference is not identified as beneficial**: the compatible range includes harm, no effect and benefit. This is one predeclared seeded fictional realization, **not** a measured effect, a 95% confidence interval or an estimated dropout rate. The earlier v1.1 443/1,000 false rejections under invented selection remain the stronger Monte Carlo negative control and are not overwritten.

## Reproduction and falsification

From `benchmarks/epmo-governance` on PR #13's branch:

```sh
python -B -m unittest -v test_reviewer_missing_bounds_v12 test_demo_reviewer_missing_bounds_v12
python -B reviewer_missing_bounds_v12.py > reproduced_v12.json
python -B -c "import json; assert json.load(open('reproduced_v12.json')) == json.load(open('REVIEWER_MISSING_BOUNDS_V12_RESULT.json'))"
python -B demo_reviewer_missing_bounds_45s.py
```

The two new suites have **17 tests** covering exact arithmetic, complete/no completions, extremal sharpness, no complete-case estimate with zero completers, invalid counts/types, randomized fixture bounds, deterministic reproduction, frozen JSON and a 30–60-second narratable fictional demo. The standard cross-platform EPMO workflow discovered all new tests and independently reproduced the frozen result on both operating systems. Git blob identities, local source/test SHA-256 and run conditions are in [registry](REVIEWER_MISSING_BOUNDS_V12_REGISTRY.json). No private gold, reviewer IDs, responses or contact details are committed.

## External method relevance — not evidence of project efficacy

The [2010 National Academies consensus report](https://www.nationalacademies.org/publications/12955) emphasizes maximizing outcome collection and stating untestable missingness assumptions, with sensitivity analyses. The [ICH E9(R1) addendum](https://www.ema.europa.eu/en/scientific-guidelines/ich-e9-statistical-principles-clinical-trials) distinguishes meaningful missing data from intercurrent events and aligns analysis with a prespecified estimand. These sources are about clinical-trial methodology, **not validation of this fictional EPMO study or an assertion that EPMO is a clinical trial**. Decision-changing transfer: freeze assigned denominators and missingness treatment **before** any optional independent reviewer study; do not interpret completer-only p-values as randomized treatment effects.

## Decision and four lenses

**No stage advancement, release, or reviewer recruitment.** Before a privately consented pilot, predefine the assigned-reviewer outcome, reasons for missingness, possible partial completions, time burden, missingness bounds and any assumption-based sensitivity analysis; seek appropriate review where needed. Reframe if uncertainty includes substantial harm or reviewers cannot complete without disproportionate burden.

**Hiring manager:** shows reproducible negative evidence and caution. **Technical reviewer:** exact finite-sample bounds but no sampling inference. **Innovation leader:** review burden may itself induce missingness. **Founder:** no validated benefit, demand, adoption, or ROI. Private outreach logs and all employer material stay outside public GitHub.
