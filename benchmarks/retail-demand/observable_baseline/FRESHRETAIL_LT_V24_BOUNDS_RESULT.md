# Retail v2.4 — frozen 2025 stockout-demand partial-identification result

**Executed 2026-10-29. Decision: FULL-PERIOD RANKING NOT IDENTIFIED.** Research / Architecture, unchanged. This is **post-hoc sensitivity on already-public 2025 labels**, not a new confirmatory holdout, lost-demand estimate, statistical confidence interval, commercial result, or causal study.

## Question and unchanged evidence

The [v2.1 preregistered comparison](FRESHRETAIL_LT_V21_TEMPORAL_TRANSFER_RESULT.md) passed on **observed in-stock days** for weekday median versus last observed. The [v2.2 strongest-simple-comparator interval](FRESHRETAIL_LT_V22_EXPLORATORY_STRONGEST_COMPARATOR.md) included zero. **1,818 of 3,584 selected days (50.73%) were stockout-censored**. A ranking on the 1,766 observed days need not identify a ranking on latent demand over all days.

The [v2.3 executable](stockout_identification_bounds_v23.py) establishes sharp mathematical bounds on paired absolute-error differences when unobserved demand is nonnegative and otherwise unconstrained. This v2.4 experiment applies that **unchanged bound engine** to the **unchanged four-model 512-series TRAIN-only forecast commitment**. No new model, tuning, selected cohort or demand imputation.

## Independently inspected hosted result

[GitHub Actions #40830505831](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40830505831), code-bearing head `85f29aa7c5997b6e1df35b60f3e8339cd6cd7848`, **completed successfully**. The new 12 fictional adversarial tests passed on **Ubuntu and Windows**; the existing 12 v2.3 bounds-engine tests also passed on each OS. The Ubuntu publisher-data job ran CPython **3.13.17** with **PyArrow 20.0.0**, rehashed pinned TRAIN/EVAL source bytes, independently rebuilt the original TRAIN-only prediction seal **before EVAL parsing**, and reconciled the historical v2.1 PASS and v2.2 INCONCLUSIVE. This is **one** hosted publisher-data execution, not two independent real-data reruns.

| Paired day-weighted MAE difference: weekday median minus comparator | Observed-only 1,766 days | Logical full-period lower | Logical full-period upper | Full-period ranking |
|---|---:|---:|---:|---|
| **Causal stockout-history** | −0.009671291 | **−0.118096401** | **+0.108565430** | **NOT IDENTIFIED** |
| **Last observed** | −0.080647792 | **−0.415067383** | **+0.335589704** | **NOT IDENTIFIED** |

Both logical intervals contain zero. **Even the previously preregistered in-stock win over last observed cannot establish a full-period latent-demand win without additional assumptions or measurements.** The original v2.1 primary gate remains **PASSED for observed in-stock MAE only**; v2.2 stronger-comparator inference remains **INCONCLUSIVE**; the 2024 v1.5 gate remains **FAILED**. None is overwritten.

## Source, artifact integrity and reproducibility

- Publisher: [FreshRetailNet-LT](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-LT), revision `01c3bb306415e09d3ccd2fe762f33eb3aeb2affd`. TRAIN SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`; EVAL SHA-256 `370ca7f995d2a059744e1659eb681e60db694bec2f80a84252426afdd2b6d626`. Source identity is checked against publisher LFS pointers, **not independent publisher authenticity**.
- Frozen 512-series TRAIN cohort SHA-256 `dc128d3bed90035214c80529bf58e685ad7d49c717d95bd10c30c2b9407ca016`; frozen four-model forecast SHA-256 `5c21bce8c9a436ecc0d3173128b0812e4408cc025558faedc2ed0e3497a54e20`.
- [v2.4 executable](freshretail_lt_stockout_bounds_v24.py), [fictional tests](test_freshretail_lt_stockout_bounds_v24.py), [workflow](../../../.github/workflows/retail-lt-stockout-bounds-v24.yml), [registry](FRESHRETAIL_LT_V24_BOUNDS_REGISTRY.json).
- [Aggregate-only artifact #12878772004](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40830505831/artifacts/12878772004) was downloaded, ZIP independently inspected and SHA-256 matched GitHub's artifact metadata: `e8e98521df2a4e2174cdb60a2824f635fbaf8f5e37da2d09ef12866f7a6d0180`. It contains only `retail_v24_aggregate.json` (member SHA-256 `e13f7e44434523000aa0b40121a7b5aff27d6154f34678c75105ad9d16448c95`). The member's counts, source hashes, historical decisions and both intervals match the hosted job log.
- To reproduce after acquiring the **exact pinned publisher files**, from this directory run `python -B -m unittest -v test_freshretail_lt_stockout_bounds_v24`, then `python -B freshretail_lt_stockout_bounds_v24.py --train /private/train.parquet --eval /private/eval.parquet --output /new/aggregate.json`. Python 3.13 / PyArrow 20.0.0. Output is exclusive-create; never commit raw publisher rows, series identifiers, daily predictions or residuals.

## Assumptions and negative result

The bounds assume the **same paired forecast target**, nonnegative demand and forecasts, and independently unconstrained demand on censored days. They use **no hypothetical global cap** and **no assumed demand recovery**. The endpoints are sharp **logical identification bounds**, **not** a 95% interval, sampling uncertainty, realized error, or proof of either model's superiority. Even a sign-identified interval would not by itself establish generalization or business value. Public labels have been seen, so this analysis cannot be called blinded.

**Four lenses:** hiring manager — a reproducible negative result that narrows claims; technical reviewer — inspect the prediction-before-label firewall, unchanged paired day-weighted estimand and no-censored-label rule; innovation leader — no novelty or patentability claim; founder — no observed unmet demand, intervention, revenue effect, deployment or customers.

**Next decisive gate:** freeze a genuinely unseen/independently sourced evaluation and a strongest-simple-comparator decision metric before labels; obtain independently justified stockout-demand constraints or measured fulfillment outcomes rather than choosing arbitrary caps to force a win. If model rankings remain unidentifiable, reframe the thesis toward transparent uncertainty bounds and decisions robust to censoring. No stage advancement, release, merge, employer data, outreach or external commitment.
