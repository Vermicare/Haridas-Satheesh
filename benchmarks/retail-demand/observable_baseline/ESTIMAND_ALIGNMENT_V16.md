# Retail v1.6 — post-hoc estimand-alignment audit (2026-10-27)

**Stage unchanged: Research / Architecture.** This is an independent *interpretation audit* of the existing aggregate in v1.5, not a new forecast, holdout, stockout-recovery result, intervention, or temporal validation. It does not amend the preregistered v1.5 gate or its **failed** decision.

## Finding

The [v1.5 protocol](STORE_DISJOINT_V15_PROTOCOL.md) combines **day-weighted** weekday-vs-last-observed mean absolute error (MAE) for its favorable point comparison with a **store-clustered interval for series-macro** MAE differences. These are different estimands when selected series have different numbers of observed in-stock days. The interval is **not** a 95% interval for the day-weighted point estimate.

On the unchanged [v1.5 preserved aggregate](STORE_DISJOINT_V15_RESULT.json):

| Quantity | Weekday minus last observed |
|---|---:|
| Day-weighted MAE delta | -0.020453871892925468 |
| Series-macro MAE delta | -0.014229287574404765 |
| Difference between estimands | -0.006224584318520703 |
| Published series-macro store-cluster interval | [-0.06301918683448345, +0.03328524212354505] |
| Day-weighted store-cluster interval | **TBD** (requires paired per-series error sums and in-stock day counts) |
| Original preregistered v1.5 gate | **FAILED**, unchanged |

Both point estimates favor weekday median, but the **published macro interval crosses zero**. The original negative decision is unaffected. These aggregate differences alone cannot reconstruct a valid day-weighted cluster interval.

## Reproducible adversarial counterexample — FICTIONAL ONLY

A deliberately constructed cohort of **100 fictional stores**, exactly one fictional series per store, has 80 stores with one observed day and a paired MAE difference of -1.0, and 20 stores with seven observed days and a paired difference of +0.5. Both point estimands are negative. With 2,000 fixed-seed store-cluster resamples, the **series-macro** interval is approximately **[-0.805, -0.580]**, whereas the **day-weighted** interval is approximately **[-0.233, +0.097]**. Thus an interval excluding zero for one estimand does **not** establish an interval excluding zero for the other. These values are synthetic method diagnostics, not publisher-data performance.

## Reproduce

From this directory (Python 3.13, standard library only):

```sh
python -B -m unittest -v test_estimand_alignment_v16
python -B estimand_alignment_v16.py --source STORE_DISJOINT_V15_RESULT.json --output /new/path/estimand_alignment_v16_output.json
```

The [dedicated GitHub Actions workflow](../../../.github/workflows/retail-estimand-audit-v16.yml) pins the existing v1.5 result Git blob `399099b75745ccaae6ad1aa1cc62ef6c67bc7a67`, tests on Ubuntu and Windows, and uploads only a derived aggregate audit. It downloads **no publisher rows** and does not modify the v1.2–v1.5 source/results. Exact successful CI run and operating-system patch versions: **TBD until verified**.

## Next decisive evidence

For a **new** predeclared study, choose one primary estimand in advance. If day-weighted MAE is primary, store-bootstrap the paired **error sums and observed-day counts together**, keeping every product series in each sampled store. If series-macro is primary, use the matching series-macro point and cluster interval. Record store and product dependence, missing/censored days, cluster count, and sensitivity to high-volume stores. Do not retrofit the 2024-06-26 to 2024-07-02 already-inspected holdout into an independent confirmation. A genuinely unseen chronological/external period and decision-relevant opportunity metric remain the maturity gate.

**Four-lens check:** hiring manager—honest negative-result interpretation; technical reviewer—point/interval estimand alignment; innovation leader—falsifiable predeclared superiority criterion; founder—no inventory, revenue, customer or pilot evidence. No private retailer/employer data, outreach, release, novelty or patentability claim.
