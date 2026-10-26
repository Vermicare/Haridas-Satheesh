# FreshRetailNet-50K official holdout v1.2 — fresh-runner reproduction (2026-10-26)

**Evidence class:** publisher-hash-checked observational in-stock-sales benchmark, **same frozen implementation on a second clean GitHub-hosted runner**. This is **not** an independent algorithmic implementation, an independent attestation of publisher origin, latent-demand validation, or a real-world intervention.

## Frozen original and new reproduction

- Original publisher 90+7 holdout: [GitHub Actions #40342565683](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40342565683), original code-bearing commit `aee03661442111a727e0fda44a534ad492e2e251`, [permanent aggregate result](OFFICIAL_HOLDOUT_V12_RESULT.json).
- Initial fresh-runner attempt: [GitHub Actions #40362031480](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40362031480), **FAILED** before evaluation because the publisher's immutable-revision `resolve/<SHA>/data/train.parquet` URL returned HTTP 404. Ten fictional contract tests and source Git-blob checks had passed. Failure is preserved, not counted as a replication.
- Corrected fresh-runner execution: [GitHub Actions #40362197198](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40362197198), commit `01d1762478d17d1708ba38b04001b8724e863594`, **SUCCESS**. The pinned-revision download URLs again returned HTTP 404; the workflow fetched the same named files from the publisher's `main` ref instead and required both files to match the **original immutable byte hashes**. Both `sha256sum --check` checks passed. A mutable-ref fallback is a reproducibility fragility and is **not** independent origin authentication.
- Original evaluator source Git blob: `ddd12a4e0695c474f752d98c99fd781931373bce`; original ten-test file Git blob: `6153f7631f143d62e915ef0f70482fa90d42ddee`; committed original result Git blob: `3a914fc3834759fabde9bb0fd2f524e7cfd162ab`. The new runner checked all three identities before acquisition.
- Runtime: Ubuntu GitHub Actions, Python 3.13.16, `pyarrow==20.0.0`. Ten/ten fictional contract tests passed. Workflow uses `contents: read` and `persist-credentials: false`.
- New aggregate-only evidence archive: artifact ID `12669146259`, ZIP SHA-256 `7e0d3025dfd80f8a0e78d5af515d4093e5f3efde81b8848591803745208d2c48`, [run artifacts](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40362197198). The runner log confirms artifact upload. Artifact retention is limited; this document preserves the verified checks, not the raw publisher data.

## Predeclared replication acceptance and outcome

The independent-runner workflow reran the **unmodified** v1.2 evaluator and compared the new aggregate against the original registry with absolute tolerance `1e-12` for floating-point values. **All 13 comparisons passed**: experiment ID, evidence class, both publisher file hashes, train-selected cohort digest, cohort size, uncensored day count, censored day count, day-weighted MAEs, series-macro MAEs, paired bootstrap interval, explicit absence of latent-demand ground truth, and explicit absence of revenue evidence.

The underlying original observational results are **unchanged**: 512 train-selected series, 2,183 in-stock scored days, 1,401 censored days excluded; day-weighted MAE last observed **0.478562**, seasonal naive **0.485180**, stockout-history correction **0.479906**. The paired series-level 95% interval for correction-minus-seasonal macro MAE **[−0.042840, +0.012164]** crosses zero. The new execution independently reproduces the **same code's** numerical outcome; it does not make that outcome statistically robust or validate its causal interpretation.

## Decision / gaps / next experiment

**Decision:** retain the mixed/negative comparative evidence and stage **Research / Architecture**. No maturity advancement, merge, release, deployment, product, patentability or inventory-impact claim.

**Strongest evidence:** two successful hosted runs of the same frozen official holdout with matching publisher file hashes, cohort identity and aggregate outputs, plus preserved initial 404 failure.

**Largest gap:** no independent implementation or external review; related series share stores/products, so the existing per-series bootstrap can understate dependence. Latent demand, inventory decisions and revenue effects remain **TBD**.

**Next preregistered experiment:** keep the original 512-series cohort and 90+7 split fixed; report a **store-clustered** paired uncertainty interval and compare a stronger daily-count baseline against last-observed and seasonal naive. Do not tune or resample based on held-out outcomes. If correction remains inferior to the strongest simple baseline, reframe the contribution around observability/measurement rather than forecast uplift.

**Four-lens check:** Hiring manager—auditable negative result and rerun; technical reviewer—same implementation is not independent replication, cluster dependence unresolved; innovation leader—correction advantage unproven; founder—no inventory or commercial ROI evidence.

**Confidentiality:** public publisher data accessed only in ephemeral runner storage; uploaded artifacts contain aggregate JSON, not publisher rows, employer information or private outreach tracking.
