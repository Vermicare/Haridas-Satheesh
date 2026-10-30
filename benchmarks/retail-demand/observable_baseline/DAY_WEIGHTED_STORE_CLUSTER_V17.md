# Retail v1.7 — paired store-cluster day-weighted uncertainty (2026-10-28 IST)

**Evidence classification: post-hoc descriptive sensitivity, NOT independent temporal confirmation.** Maturity remains **Research / Architecture**. The preregistered v1.5 superiority gate **FAILED** and is not changed.

## Decision-changing question

[v1.6](ESTIMAND_ALIGNMENT_V16.md) found that the v1.5 favorable day-weighted MAE point estimate was paired with a confidence interval for a different estimand (series-macro MAE). This experiment computes the missing *matching* 95% descriptive store-cluster percentile interval for **day-weighted** weekday-median minus last-observed MAE on the exact original store-disjoint cohort and same previously inspected publisher dates. This repairs the uncertainty interpretation, **not** the confirmatory design.

## Verified publisher-data result

[Hosted GitHub Actions run #40561762763](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40561762763) completed successfully: **5/5 fictional/adversarial tests on Ubuntu, 5/5 on Windows**, plus publisher-data reanalysis on Ubuntu. Both operating-system test logs and the publisher job log were inspected. The downloaded [aggregate-only artifact #12761436621](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40561762763/artifacts/12761436621) was opened independently: ZIP SHA-256 **38747180f9fa170697f549c699ddc6caa23fc54fcdd4ddaec7402a1d17ba42b8** matched the hosted digest; the two committed JSON files have the exact Git blob identities of the artifact members.

| Quantity | Verified value |
|---|---:|
| Same frozen v1.5 cohort | 512 store-product series / 293 stores |
| In-stock scored days | 2,092 |
| Day-weighted weekday-minus-last MAE difference | **-0.020453871892925433** |
| **Matching paired whole-store bootstrap 95% interval** | **[-0.06710535800851568, +0.022735340645572123]** |
| Bootstrap draws / fixed seed | 2,000 / 20261028 |
| Leave-one-store-out point-difference range | [-0.029026239768897448, -0.012945458913983665] |
| Earlier v1.5 series-macro 95% interval (different estimand) | [-0.06301918683448345, +0.03328524212354505] |
| Superiority established? | **NO — both intervals cross zero** |
| New evaluation dates / latent demand / revenue uplift | **None / unavailable / TBD** |

**Important negative result:** even after matching the interval to the day-weighted point estimate, the 95% interval still crosses zero. The weekday median's favorable point estimate is **not** established as a robust improvement. A leave-one-store-out point estimate remaining negative is not proof of significance and does not replace the interval.

## Method and independent checks

The code uses the **unchanged** v1.2 and v1.4 evaluators, frozen v1.5 cohort-selection logic, original published v1.5 result, and publisher TRAIN/EVAL Parquet files. It verifies the pinned source hashes, original evaluator/result Git blobs, frozen cohort hash, publisher dates, original point estimates, number of series/stores and scored-day denominator. It computes **paired per-series sums of absolute errors and in-stock day counts**, aggregates within each store, then resamples **whole stores with all products retained**. Each bootstrap draw computes a *ratio of summed paired error differences to summed observed days*; it does not average per-series means.

Fictional-only negative controls reject duplicate series, invalid day counts, nonfinite or negative error sums, boolean inputs, single-store uncertainty and invalid bootstrap settings; they check deterministic results and multi-series cluster retention.

Reproduce from the benchmark directory with Python 3.13 and pinned PyArrow 20.0.0:

    python -B -m unittest -v test_store_cluster_day_weighted_v17
    python -B store_cluster_day_weighted_v17.py --train /private/train.parquet --eval /private/eval.parquet --preserved STORE_DISJOINT_V15_RESULT.json --output /new/path/v17.json

The [workflow](../../../.github/workflows/retail-dayweighted-sensitivity-v17.yml) downloads publisher files to runner temporary storage, checks both SHA-256 values, and uploads **only aggregate JSON**. No raw publisher rows, store identifiers, individual predictions, private retailer records, or employer data are published.

## Reproducibility identities

- Tested executable workflow commit: **875536dd3f2849b62caab8625b3f345096843121**.
- Executable source Git blob: **ae3b8fab13d1e34200286a681a61b8697d07a920**.
- [Committed aggregate result](DAY_WEIGHTED_STORE_CLUSTER_V17_RESULT.json): SHA-256 **52a87d45b7574be642851299f3a848b9a497e59b7b0a8f47caddb757715fe650**, Git blob **cebc5e8b38994e30da77556d5ebcd510f5bc10af**.
- [Committed provenance](DAY_WEIGHTED_STORE_CLUSTER_V17_PROVENANCE.json): SHA-256 **5230b89c131536fd12531f368160cb061d452d103d68373f94c19b0d362ac220**, Git blob **186d015460cb404ed94ed413f3e9f143af18fbb7**.
- Publisher TRAIN SHA-256 **6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d**; EVAL SHA-256 **1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e**.
- Runner: Linux, Python **3.13.16**, PyArrow **20.0.0**. Full platform and source identity in committed provenance.

The immutable revision download endpoint returned HTTP 404; the workflow used the explicitly permitted publisher main fallback **only after checking both frozen SHA-256 values**. This is a source-availability limitation, not permission to accept different bytes.

## Limits and next gate

This analysis is post-hoc on the **same 2024-06-26 through 2024-07-02 holdout** already inspected during comparator selection. Percentile bootstrap relies on the adequacy of the store clustering and does not address cross-store dependence, temporal shift, selection after inspection, latent demand, inventory decisions or causal outcomes. Neither CI should be used to claim production benefit.

**Next decisive experiment:** predeclare the **day-weighted paired store-cluster estimand and uncertainty procedure** and score an actually untouched chronological or independent public cohort. Report product/store dependence, observed-day counts, failure cases and a decision-relevant metric where observable. Reframe the forecasting complexity if a simple baseline remains competitive.

Four lenses: hiring manager—reproducible negative-result discipline; technical reviewer—correct matching of estimand and cluster uncertainty; innovation leader—no advancement without untouched data; founder—no inventory, revenue, user or deployment claims. No external reviewer, outreach, release, merge, novelty or patentability claim.
