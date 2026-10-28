# Retail v2.1 — 2025 preregistered temporal-transfer score (2026-10-28)

**Decision: the narrow, preregistered weekday-median versus last-observed MAE gate PASSED.** This is a *public-label, same-publisher, observed-in-stock-only* comparison, **not** a claim of latent-demand recovery, inventory savings, general model superiority, independent external validation or product readiness. Retail remains **Research / Architecture**. The separate 2024 v1.5 primary superiority gate **FAILED** and is preserved unchanged.

## Why this experiment matters

The earlier 2024 comparison did not establish superiority: its correctly matched day-weighted whole-store interval crossed zero. A later 2025 FreshRetailNet-LT calendar provides a prospective temporal-transfer check. The [v1.8 preregistration](FRESHRETAIL_LT_V18_PREREGISTRATION.md) froze the source revision, 512 TRAIN-only cohort, four unmodified methods, primary estimand, 2,000 whole-store bootstrap resamples (seed 20261028), and the stop/failure rules **before** the new EVAL labels were parsed. [v1.9](FRESHRETAIL_LT_V19_TRAIN_COHORT.md) selected TRAIN series and [v2.0](FRESHRETAIL_LT_V20_PREDICTION_SEAL.md) sealed their predictions before the v2.1 scoring implementation.

## Fail-closed label firewall

1. Hash the pinned TRAIN bytes (315,398,578 bytes; SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`).
2. Rerun the v2.0 TRAIN-only predictor, then **independently reconstruct all 512 × 7 × four forecasts** and require the previously published SHA-256 `5c21bce8c9a436ecc0d3173128b0812e4408cc025558faedc2ed0e3497a54e20`. Abort without parsing EVAL if either seal differs.
3. Only after both matches, hash the pinned EVAL bytes (2,009,424 bytes; SHA-256 `370ca7f995d2a059744e1659eb681e60db694bec2f80a84252426afdd2b6d626`) and parse the selected public labels. Reject duplicate/missing future days, out-of-horizon dates, changed method names, invalid hourly status, nonfinite predictions or changed source bytes. **Never replace a selected series using EVAL availability.**
4. Score observed *in-stock* business-hour sales only. Compute the day-weighted weekday-minus-last-observed MAE and its **matching** paired whole-store percentile interval. Report all four methods and denominator/censoring counts; no post-hoc model promotion.

Executable: [v2.1 scorer](freshretail_lt_score_v21.py), [15 fictional adversarial tests](test_freshretail_lt_score_v21.py), [hosted workflow](../../../.github/workflows/retail-lt-presealed-score-v21.yml), [machine-readable registry](FRESHRETAIL_LT_V21_SCORE_REGISTRY.json). Local execution after independently obtaining exact publisher files:

```sh
python -B -m unittest -v test_freshretail_lt_score_v21
python -B freshretail_lt_score_v21.py --train /private/train.parquet --eval /private/eval.parquet --output /new/aggregate.json
```

Requires Python 3.13, PyArrow 20.0.0 and unchanged repository dependencies. Do not publish raw publisher rows, identifiers or prediction arrays.

## Independently reproduced hosted result

Both [push run #40728652213](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40728652213) and [separate PR run #40728662310](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40728662310) completed successfully on the same code-bearing head `22296e4db214f9eeb59b2db846d5fda9aee01aed`. Each passed **15/15 fictional negative-control tests on Ubuntu and 15/15 on Windows**, then the Ubuntu pinned-data job completed with Python **3.13.16** and PyArrow **20.0.0**. Both logged the exact prior prediction digest before EVAL scoring.

| Predeclared or descriptive outcome | Verified 2025 result |
|---|---:|
| Frozen TRAIN-selected series / stores / products | 512 / 374 / 104 |
| Expected future days | 3,584 |
| Observed in-stock days scored | **1,766** |
| Stockout-censored days excluded | **1,818** (50.73% of days) |
| Missing future dates | **0** |
| Last-observed day-weighted MAE | 0.647912 |
| Seasonal-naive day-weighted MAE | 0.607723 |
| Causal stockout-history day-weighted MAE | 0.576935 |
| Weekday-median day-weighted MAE | **0.567264** |
| **Primary weekday minus last-observed delta** | **−0.080648** |
| **Matched whole-store 95% bootstrap interval** | **[−0.137362, −0.030217]** |
| Whole-store clusters / resamples / seed | 374 / 2,000 / 20261028 |
| Preregistered primary gate | **PASS** |
| Stage change | **NONE** |

The weekday median's MAE is **12.45% lower than last-observed** on this selected observed-in-stock evaluation. That percentage is descriptive, not a causal effect or inventory benefit. The leave-one-store-out primary delta ranges from −0.089204 to −0.066841. The weekday method also has **−0.100006 weighted prediction error** (forecast minus observed divided by observed sales), indicating underprediction on the scored observations; this matters for any future decision study.

**Independent artifact integrity:** the push ZIP SHA-256 is `53064330ff8b41befa16ea07897443c845da0cea782748bc761ab6069d9a9bf1` (aggregate JSON `e785209bac38685d0a050a0c6b43d4377132653721c5d1e1e064cb5dcd71a3f9`). The PR ZIP SHA-256 is `5099403d5818bdd564e00b4c99bb4f7efd1018cd934e47e78e6a83ed940c2cfa` (aggregate JSON `60e4e3c76f460a1b70be8411a084a63fd88570f88a48f3e476e94ab7cc73af5e`). Both ZIPs were downloaded and independently SHA-256-checked against GitHub artifact metadata; **all substantive JSON fields match** after excluding the expected `provenance.git_checkout` difference between push head and PR merge checkout. No raw publisher rows or series IDs were uploaded.

## Limits, negative evidence and next decision

The 2024 v1.5 superiority gate **failed** and must not be rewritten as a success. The new 2025 primary gate compares **only weekday median versus last observed**. Although weekday median has a slightly lower point MAE than causal stockout history (0.567264 versus 0.576935), **no preregistered matched interval for that secondary difference** was established; do not claim superiority over all methods. Over half of selected days are censored and therefore excluded from observed-sales accuracy. This does **not** identify lost demand, recover unobserved sales, establish generalization to another retailer, or demonstrate inventory/revenue impact. Public labels were not blinded, and source identity is verified against publisher bytes, not an independent publisher signature.

**Next evidence-producing step:** freeze a *different-publisher or genuinely blinded* future evaluation with a predeclared comparison against the **strongest simple comparator**, include stockout/selection sensitivity and an independently justified inventory decision metric, then seek independent technical review. Reframe the correction/latent-demand thesis if it cannot beat the strongest baseline under matched uncertainty or if decision errors dominate. No stage advancement, pilot, release, patentability claim, employer data or external commitment.

**Four lenses:** hiring manager — executable public-data reproducibility and preserved failure; technical reviewer — inspect prediction-before-label firewall, whole-store estimand and 50.73% censoring; innovation leader — one same-publisher temporal transfer, no novelty conclusion; founder — no validated commercial value, users or deployment.
