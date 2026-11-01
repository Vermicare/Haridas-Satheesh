# Retail v2.8 — complete publisher-target last-observed baseline (2026-11-01)

**Status: VERIFIED full-target prediction coverage, NOT an official forecast score.** Research / Architecture unchanged. This is a historical-only, intentionally simple baseline. The publisher's evaluation labels were **not read by the v2.8 generator or v2.7 coverage preflight**; target identifiers and dates were read to construct the 70,000-row private CSV. The evaluation file's original bytes were SHA-pinned, but original source authenticity beyond publisher remains TBD.

## Independently inspected execution

- [Final successful GitHub Actions run #41307879620](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41307879620), source checkout `b4cd020148b2e5f1fe44af5fe3efdbc63db84352`, Python **3.13.17**, PyArrow **20.0.0**, Ubuntu public-data job. Both Ubuntu and Windows separately passed **15/15 fictional adversarial contract tests**. Original job logs were inspected.
- Publisher revision `01c3bb306415e09d3ccd2fe762f33eb3aeb2affd`; verified TRAIN **315,398,578 bytes**, SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`; verified EVAL **2,009,424 bytes**, SHA-256 `370ca7f995d2a059744e1659eb681e60db694bec2f80a84252426afdd2b6d626`.
- **7,869,549 TRAIN rows scanned** across **22,939 historical series**. For each EVAL target key, the baseline uses the most recent strictly pre-2025-07-14 `sale_amount` for its store/product series, with a declared zero fallback for missing series. **0 fallback rows** occurred on this publisher snapshot.
- Generated **70,000 private prediction rows**, exactly **10,000 on each of 2025-07-14 through 2025-07-20**; canonical prediction CSV **2,219,321 bytes**, SHA-256 `54b5bdd957b6e3c367489b2236109df95a27e95b141d088cc23c8155be6792d1`. Raw prediction rows were **not uploaded to GitHub**.
- Independent existing [v2.7 full-target preflight](freshretail_lt_full_target_gate_v27.py) returned `PASS_FULL_TARGET_ONLY`: **70,000 unique targets = 70,000 predictions**, no missing/duplicate/extra target keys or invalid predictions.
- [Original aggregate-only GitHub artifact #13084430550](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41307879620/artifacts/13084430550) downloaded independently. ZIP SHA-256 `fe41d780fd6e3f4e3ba3763cd70e29964f303f46ce80d5b256a6e1a0702bd5b0`, ZIP integrity PASS, exactly two JSON files: `retail-v28-aggregate.json` SHA-256 `d7c6391a42325ff1e0cce179de6f14bf4105f17f3a5001bd45b0ea1e441e394a` and `retail-v28-coverage.json` SHA-256 `244a87d213d3fe073aa5004568fb4db70b18d9d3536756c9d04cef89f8e21ff9`. Both contents independently parsed and cross-checked against logs. Artifact retention: **14 days**, expected expiry ~2026-11-15.

## Reproduce / inspect in 30–90 seconds (fictional contract)

From `benchmarks/retail-demand/observable_baseline`:

```bash
python -B -m unittest -v test_freshretail_lt_full_target_last_observed_v28
```

For the actual public dataset, acquire the publisher-pinned TRAIN/EVAL Parquet files to private ephemeral storage, verify both SHA-256 hashes, then run:

```bash
python -B freshretail_lt_full_target_last_observed_v28.py --train /private/train.parquet --eval /private/eval.parquet --predictions /private/predictions.csv --report /private/v28.json
python -B freshretail_lt_full_target_gate_v27.py --eval /private/eval.parquet --predictions /private/predictions.csv --output /private/v28_coverage.json
```

The [read-only workflow](../../../../.github/workflows/retail-lt-full-target-v28.yml) pins PyArrow 20.0.0 and uploads **only aggregate reports**. The forecast implementation retains only the latest historical value per series; it does **not** independently audit duplicates on earlier, nonselected history dates. All physical/private or employer data are excluded.

## Interpretation / decision

**Strongest new evidence:** complete, pinned, TRAIN-only last-observed predictions for every publisher EVAL key and independent v2.7 coverage PASS. This closes the **full-target baseline generation/coverage gap**, not the performance or latent-demand gap. It does **not** establish the publisher's eligibility-mask scoring, competitive accuracy, model superiority, latent-demand recovery, inventory benefit, external review or leaderboard acceptance. Public EVAL labels exist, so later scoring must be labeled exploratory rather than blinded.

**Largest gap:** independently reproduce the 70,000-row prediction SHA on a clean second host, apply the publisher's exact `psd >= 0` and `stock_hour6_22_cnt == 0` mask with frozen metric definitions, and compare against stronger predeclared historical-only baselines. **Next experiment:** independent clean-runner re-generation and exact-key/hash comparison, followed by explicitly exploratory publisher-consistent scoring; preserve v2.1 within-subset results and negative strongest-comparator/partial-identification findings unchanged.

**Kill/reframe:** stop leaderboard or superiority claims on source/coverage mismatch, post-origin feature leakage, changed prediction hash, inconsistent scoring mask, or a result that does not outperform transparent comparators. If latent demand remains unidentifiable, reframe toward observed-sales forecasting/partial identification. No stage change, merge, release, patentability, commercial or deployment claim.

**Four lenses:** hiring manager—traceable full-target reproducibility; technical reviewer—source pin, label firewall, independent coverage check and limitations; innovation leader—falsifiable comparator, no novelty assertion; founder—no demonstrated financial/customer outcome.
