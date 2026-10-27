# EPMO reviewer-level sample-size sensitivity v1.0 (2026-10-27)

**Decision:** The v0.9 fictional manual-notes versus worksheet experiment is not ready for a credible small-sample efficacy claim. This is a **simulation of assumed reviewer behavior**, not an observed human result, randomized trial, employer evaluation, or proof of productivity benefit. No participant was contacted or measured. Stage stays **Research / Simulation**.

## Question and design

Before any invitation or study commitment, how likely is a reviewer-level, two-sided randomization test to detect a hypothetical ten-percentage-point reduction in false approvals, given the **13 oracle-negative fictional cases per reviewer** in [v0.9](REVIEW_TREATMENT_V09.md)?

- **Unit of randomization and analysis:** one reviewer assigned to exactly one arm; never treat 13 case decisions as 13 independent reviewers.
- **Control hypothesis:** 20% mean false-approval probability on fictional negative cases (assumption, not a measurement).
- **Treatment hypothesis:** 10% mean probability, a hypothetical 10 percentage-point absolute improvement (not a claim).
- **Null scenario:** 20% in both arms, used to inspect the test's false-positive behavior.
- **Within-reviewer heterogeneity:** beta-binomial model with intraclass correlation 0.10, **assumed**, and 13 Bernoulli decisions per reviewer. Reviewers are simulated independently; case difficulty, shared-case correlation across reviewers, recruitment bias, learning, noncompliance and attrition are **not** modeled.
- **Arm sizes:** 12, 24, 48 and 96 reviewers **per arm**, not total.
- **Analysis:** two-sided reviewer-level difference in mean false-approval fraction, Monte Carlo randomization test with 199 label permutations; p = (1 + number of as-extreme permutations)/(1 + 199); alpha 0.05.
- **Run:** Python 3.13.5 / Linux; standard library only; fixed seed 20261027; 400 simulation replications per scenario and sample size. Monte Carlo uncertainty is reported, not hidden.

## Executed assumption-based result

| Reviewers per arm | Null rejection probability | Hypothetical 20% → 10% detection probability | Monte Carlo SE for detection |
|---:|---:|---:|---:|
| 12 | 0.0250 | 0.3050 | 0.0230 |
| 24 | 0.0475 | 0.5975 | 0.0245 |
| 48 | 0.0250 | 0.9050 | 0.0147 |
| 96 | 0.0500 | 0.9975 | 0.0025 |

**Interpretation:** Under *these exact invented assumptions*, a 12-per-arm study would often fail to detect even a substantial hypothetical benefit. At 48 per arm the simulated detection rate is 90.5%, but this is **not** a validated sample-size prescription or an actual efficacy result. The null simulations ranged from 2.5% to 5.0% rejection; the finite-permutation/discrete test can be conservative. A different baseline, smaller effect, greater heterogeneity, shared case effects or missing reviewers could change the numbers materially.

The primary v0.9 study remains **unexecuted**: observed false approvals **TBD**, observed review time **TBD**, consent **TBD**, independent reviewer count **0**. Neither simulation nor a passing software test advances maturity.

## Reproduce and inspect

From `benchmarks/epmo-governance`:

```sh
python -B -m unittest -v test_reviewer_power_sensitivity_v10
python -B reviewer_power_sensitivity_v10.py > /tmp/epmo-reviewer-power-v10.json
sha256sum /tmp/epmo-reviewer-power-v10.json
```

The saved output is [REVIEWER_POWER_V10_RESULT.json](REVIEWER_POWER_V10_RESULT.json). The local result SHA-256 was `b6eef6d872f2de56793d367b0c7f9da27a0005df446aada4c73c5707931f69da`. The Python source SHA-256 was `70455a68426c8bdf4b676f918c10e9c7e2524dc912e9cd3e2415ff2f47866dcf`, and the test source SHA-256 was `4cd6fc39a06bc57737d011515a6e15584598cc27c3fda831cef88596f4231261`. These hashes cover this **local** execution; GitHub-hosted cross-OS CI verification is a separate gate and must not be inferred until it passes.

## Next evidence-producing decision

**Do not recruit on the strength of the simulated 90.5%.** First freeze a defensible consent/assignment/analysis plan, obtain a realistic independent estimate of baseline reviewer errors and heterogeneity through an approved, privately managed pilot, then rerun sensitivity under plausible smaller effects and item-level dependence. Preserve all participant data and assignments outside public GitHub. Report null and negative results. Do not claim employer workflow improvements, validated users, commercial value or real-world authorization safety.

**Four lenses:** hiring manager—transparent uncertainty rather than inflated claims; technical reviewer—check the model and finite-permutation null behavior; innovation leader—question whether the worksheet is worth reviewer burden; founder—no demand, adoption, revenue or defensibility evidence.
