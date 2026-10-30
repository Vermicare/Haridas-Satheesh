# Retail v2.6 — TRAIN-only daily/hourly numeric identity gate (2026-10-30)

**Status: pinned TRAIN execution VERIFIED (Ubuntu); fictional controls VERIFIED (Ubuntu and Windows).** This is a separately testable, additive consistency audit. No evaluation labels are read, no model retraining or performance comparison is made, and no project stage changes. The previous v2.5 conditional logical bounds and v1.5 negative superiority result remain intact.


## Independently inspected source-data result (2026-10-30)

[GitHub Actions #41022154149](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41022154149), checkout `e7c3e12394a2610d0c6d77a425afdc457fd355a7`, completed **PASS**. Ubuntu and Windows each passed **12/12 fictional contract tests**, with both logs inspected. The publisher-TRAIN-only Ubuntu job downloaded the pinned 315,398,578-byte Parquet file and passed SHA-256 verification; its log reports the full 7,869,549-row scan and zero tolerance failures. The original 870-byte hosted ZIP artifact was independently downloaded, passed ZIP integrity checks and its sole JSON result was parsed and checked against the job log. ZIP SHA-256: `6b0186d8745a8d9c73920966ddba698de8d13f6e31a8ecc2c4f4e5043297ed46`.

| Aggregate-only TRAIN result | Observed |
|---|---:|
| Rows examined | 7,869,549 |
| Daily vs 24-hour-sum differences beyond frozen tolerance | **0** |
| Maximum absolute difference | 1.4210854715202004e-14 |
| Sum of absolute differences | 5.926595741945206e-10 |
| Negative daily quantities | 0 |
| Negative hourly quantities | 0 |
| EVAL bytes opened / labels read | **No / No** |

**Decision:** the pinned publisher TRAIN fields are **numerically consistent with daily = sum of 24 hourly quantities** at the declared tolerance. This resolves the *TRAIN numeric aggregation* question only; it **does not** independently establish what transactions the quantities represent, how global normalization was constructed, whether the 2025 EVAL split behaves identically, or whether recorded sales lower-bound the same latent-demand estimand. The v2.5 conditional bounds still cross zero; Retail remains **Research / Architecture**, no advancement. Next: obtain publisher-confirmed gross/net, returns, substitutions, cancellations and business-day boundary definitions before any stronger floor or demand claim.

## Question and preregistered test

Does `sale_amount` numerically equal the sum of the 24 `hours_sale` values for every row of the **pinned 7,869,549-row TRAIN split**, to within `abs(delta) <= 1e-8 + 1e-6 * max(abs(daily), abs(hourly_sum))`? This checks **only a numeric aggregation identity**. It cannot verify net-versus-gross transaction definitions, same-target latent-demand floors, returns, cancellations, substitutions, time-zone/business-day boundaries, forecast accuracy or sales/revenue impact.

The publisher [FreshRetailNet-LT card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-LT) describes daily/hourly sales as globally normalized quantities; its [official leaderboard](https://huggingface.co/spaces/Dingdong-Inc/FreshRetailNet-LT-Leaderboard) has public EVAL labels. The [v2.5 semantic audit](FRESHRETAIL_LT_PUBLISHER_SEMANTICS_AUDIT_20261030.md) leaves the latent-demand lower-bound assumption **unverified**.

## Fail-closed execution

The workflow acquires **TRAIN only** at publisher revision `01c3bb306415e09d3ccd2fe762f33eb3aeb2affd`, requires exactly **315,398,578 bytes** and SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`, and checks 7,869,549 rows. It refuses null/non-finite values, malformed hourly vectors, source hash mismatch and output overwrite. PyArrow 20.0.0 and NumPy 2.2.6 are pinned; runner/Python versions and commit are captured at runtime. All numeric statistics are aggregate-only; no identifiers or publisher rows are published.

**Decision:** if any rows exceed tolerance, report **REVIEW REQUIRED**, with counts and maximum difference, not an assumed cause. If all match, report **numeric consistency only**, not validated transaction semantics or a sales floor. Either way, stage remains **Research / Architecture**. Source authenticity beyond publisher LFS pointer is **TBD**. No patents, deployment, employer data, external-review or novelty claim.

**Reproduce (private runner):** `python -B -m unittest -v test_freshretail_lt_train_hourly_identity_v26` and `python -B freshretail_lt_train_hourly_identity_v26.py --train /private/train.parquet --output /new/report.json`. The test suite uses fictional arrays only. The workflow uses a fresh ephemeral runner and uploads only the summary JSON. No EVAL path exists in the command-line interface.

**Four lenses:** hiring manager—traceable decision boundary; technical reviewer—full pinned TRAIN, numerical tolerance and adversarial checks; innovation leader—falsifiable assumption rather than claimed novelty; founder—no validated demand, revenue, inventory or customer benefit.

**Largest gap / next experiment:** obtain publisher-confirmed transaction and normalization semantics after the numeric check. If numeric consistency fails, investigate whether a business-hour/day-boundary mismatch explains it without touching EVAL. If it passes, do not promote the v2.5 conditional bounds without independent same-target floor evidence.
