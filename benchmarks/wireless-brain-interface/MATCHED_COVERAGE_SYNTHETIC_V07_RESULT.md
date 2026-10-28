# WBI v0.7 — exact-coverage synthetic drift falsification: verified result (2026-10-28)

**Evidence:** deterministic *fictional* software experiment only. **No EEG was loaded, no brain signal was decoded, no clinical or safety result exists.** Maturity remains **Research / Simulation**. The original main-branch `synthetic_evaluator.py` Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9`, original CSV and execution record were **not edited**.

## Hypothesis and preregistered comparison

The [preregistered protocol](MATCHED_COVERAGE_SYNTHETIC_V07.md) fixed 12 calibration/test seed pairs, exactly **120 of 240 acted fictional rows (50% coverage)** per policy, and a calibration-only weight search `[0, 0.1, 0.25, 0.5, 1.0]`. Baseline ranked confidence alone; candidate ranked `confidence − weight × drift`. Test labels were used **only to score** frozen selections, never to choose a weight. Stable index tie-breaking ensures exact action counts. A separate test-only drift permutation preserves confidence, labels and marginal drift distribution while disrupting their association.

### Reproduced results

| Fictional held-out regime | Candidate − baseline incorrect actions | Candidate wins / ties / losses across 12 fixtures | Actions per policy |
|---|---:|---|---:|
| Original synthetic drift | **−7** | **4 / 5 / 3** | 1,440 |
| Permuted test-only drift | **+8** | **1 / 6 / 5** | 1,440 |

The original regime's pooled paired incorrect-action difference is **−7/1,440 ≈ −0.00486**, or **−0.486 percentage points** in observed selective risk. After the synthetic drift values are permuted, the difference reverses to **+8/1,440 ≈ +0.00556**, or **+0.556 percentage points**. Both policies retain exactly 50% coverage in every replicate. These are **descriptive deterministic synthetic differences**, not confidence intervals, EEG results or evidence of clinical risk reduction. There is no superiority or statistical-significance claim.

Frozen calibration-selected weights across the 12 seed pairs: `[0.1, 0.25, 0, 0, 0, 0.25, 0.25, 0.1, 0.25, 0.25, 0.1, 0]`. Original-regime per-replicate incorrect-count deltas: `[-3, -3, 0, 0, 0, +2, +1, 0, -4, +2, -2, 0]`. Permuted-drift deltas: `[+1, -1, 0, 0, 0, 0, +1, +1, 0, +3, +3, 0]`.

### Independent cross-operating-system verification

[GitHub Actions run #40718361067](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40718361067) completed successfully from code-bearing commit `a9479b766b578edff744946e34d04f90699b0527`.

- **Ubuntu**, CPython 3.13.17, job `122922130852`: **14/14 adversarial tests PASS** and aggregate-only JSON generated.
- **Windows**, CPython 3.13.16, job `122922131242`: **14/14 adversarial tests PASS** and aggregate-only JSON generated.
- Both ZIP artifacts were independently downloaded and rehashed against GitHub's artifact metadata. Ubuntu artifact `12829137804` ZIP SHA-256 `b0dc46f7103958a30a727b42dee657000adf58ec84094fca9bc8d10ddf81c062`; Windows artifact `12830170932` ZIP SHA-256 `0a128f7d420861b7e44bbb5074e776b799a17e0f2dbb8725d4767ed289df5977`.
- Their JSON member SHA-256 values were `f84121751719f31e737718d7e011f99feafa52008dc73214301e1ef43894e478` and `0754a91dd5daad07671be6fc62c4ad1bb45db5174b3428d1f8493c5fc379fa12`. Their substantive results, per-replicate rows, frozen evaluator Git blob and source SHA-256 were **identical**; JSON differs in recorded runner Python/OS provenance. Original evaluator source SHA-256: `dd40d8b22c4b03194b4ba6ea82da832fcd7754b5434d4e41b4d944f21b11de7d`.

The source-identity/tamper test, exact coverage, index ties, test-label invariance, drift-permutation invariants and deterministic repetition all passed. No physical instrument, EEG recording, participant or external reviewer was involved.

## Negative learning / decision

The tiny advantage under the generator's original synthetic drift association **reverses** under a distribution-shift negative control. This exposes dependence on a particular synthetic drift/label relationship. The new experiment is **not** evidence that the drift gate is safer than simple abstention on real EEG. Preserve the original frozen result's failure to establish matched-coverage superiority; do not overwrite it with the new result. **No maturity advancement, release, deployment or patentability claim.**

The next highest-value experiment is a **preregistered public-EEG, held-out subject/session** evaluation using a label-safe split and comparable action coverage, with drift-feature provenance and explicit per-subject failure reporting. Complete the remaining BNCI MAT structural provenance checks before any decoding, then independently replicate. If drift ranking does not beat confidence-only at matched coverage on EEG, **reframe** the authorization feature as unproven.

## Prior art and reviewer lenses

[Geifman & El-Yaniv, NeurIPS 2017](https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html) formalizes selective risk versus coverage as an established research problem. [Jayaram & Barachant, Journal of Neural Engineering 2018](https://doi.org/10.1088/1741-2552/aadea0) motivates standardized, multi-dataset BCI benchmarking. These references inform the evaluation design, **not novelty or WBI performance claims**.

Hiring manager: inspect executable falsification and retained negative controls. Technical reviewer: challenge synthetic score leakage, fixed 50% top-k selection and drift shift. Innovation leader: no novelty claimed for abstention or selective classification. Founder: hardware feasibility, clinical acceptability, false-action cost, real-world value and external review remain **TBD**.

## Reproduce

From `benchmarks/wireless-brain-interface`, run:

```sh
python -B -m unittest -v test_matched_coverage_synthetic_v07
python -B matched_coverage_synthetic_v07.py --output /new/empty/path/wbi_v07.json
```

No third-party Python dependencies. Output is aggregate fictional data only and refuses overwrite. The executable package remains on **draft, unmerged PR #16**; main has only the evidence boundary if linked from its roadmap.
