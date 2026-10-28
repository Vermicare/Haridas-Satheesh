# Retail v2.0 — TRAIN-only prediction commitment (2026-10-28)

**Protocol frozen before any v2.0 evaluation-label access.** This is prediction provenance, not accuracy, superiority or latent-demand validation. Retail stays **Research / Architecture**. The v1.5 primary superiority gate remains **FAILED**; no prior evidence is overwritten.

## Decision and immutable inputs

Question: can the four existing frozen v1.2/v1.4 methods produce 7-day predictions for the **same 512 TRAIN-selected** FreshRetailNet-LT series without touching EVAL labels? **Stop** on publisher TRAIN SHA mismatch, missing/invalid selected history, cohort digest mismatch, nonfinite forecast or changed method contract. Do not select replacements based on EVAL presence.

Publisher: [FreshRetailNet-LT v1.0](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-LT/commit/01c3bb306415e09d3ccd2fe762f33eb3aeb2affd), CC BY 4.0 as declared. TRAIN is 315,398,578 bytes, SHA-256 `e744c537ed16a8254c50f8456de7c5614866d4d8b6787e3cc3b67be02ea2f1e3`. Cohort digest `dc128d3bed90035214c80529bf58e685ad7d49c717d95bd10c30c2b9407ca016`. Training dates: 2025-04-15 through 2025-07-13. Forecast dates: 2025-07-14 through 2025-07-20.

Methods must call existing `retail_gate.forecast_at_origin` (last-observed, seasonal naive, causal stockout history) and `weekday_median_v14.weekday_median_forecast` (last four uncensored same weekdays, last-14 fallback, zero fallback). Use business-hour observed sales `hours_sale[6:22]`, and matching stockout flags. Do not tune, refit or change target definitions. Future placeholders contain **dates only**, no future sales or stock status. The v2.0 program has **no EVAL input argument**.

## Commitment and reproducibility

Canonical SHA-256 stream: in frozen SHA-ranked cohort order, one compact, sorted-key ASCII JSON object per series containing its integer store/product key, seven future ISO dates and the four named prediction arrays; append LF to each object. Publish **only** aggregate SHA-256, counts, fallback counts, source/cohort fingerprints and versions, never raw publisher rows, series identifiers or prediction arrays. Later scoring must independently regenerate and match this sealed digest **before** parsing EVAL labels.

Run fictional negative controls on Ubuntu/Windows, pinned publisher TRAIN-only execution on Ubuntu (Python 3.13, PyArrow 20.0.0), independently inspect job logs and aggregate-only artifact. Record exact code-bearing commit, source identity, run ID, artifact integrity and any failures. **Until execution, result, prediction digest and independent replication remain TBD.** A source hash is agreement with publisher bytes, not independent publisher authentication.

The later, separate label-reading experiment must preserve v1.8 preregistered day-weighted MAE with paired whole-store cluster percentile interval (2,000 draws, seed 20261028), in-stock scoring denominators, and the explicit stop/negative decision. No latent-demand recovery, inventory savings, causal effect, product readiness, patentability or employer data claim.

**Four lenses:** hiring—inspect executable frozen-label discipline; technical—challenge source/schema, leakage and digest reproducibility; innovation—temporal transfer, not novelty; founder—commercial value and independent review TBD.


## Verified execution and negative result — October 28, 2026

**Final code-bearing head:** `99f54de22d2f783d1270f420f21658fc454f99f6`. [Push execution #40709694133](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40709694133) and [separate PR execution #40709707033](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40709707033) both completed successfully. Each passed **17/17 fictional negative-control tests on Ubuntu and Windows**; both independently downloaded the pinned **TRAIN-only** 315,398,578-byte file, passed its SHA-256 check, and generated **512 × 7 = 3,584 forecast days across four frozen models**. The prediction SHA-256 independently matched across runs: `5c21bce8c9a436ecc0d3173128b0812e4408cc025558faedc2ed0e3497a54e20`. The cohort SHA-256 also reproduced v1.9 unchanged. Weekday-median training-only fallback counts: **3,534 same-weekday / 42 recent-14 / 8 zero**.

**Independent artifact integrity:** Both ZIP archives were downloaded and SHA-256 checked against GitHub metadata: push `6b66d3bc84fc9b84818ca9f0989edcd929b553bdad602989536f97c7ccfd7d2c`, PR `ecb13b7a8787a4f99f3b5fc8c9038c6b99e2e95bda6a4b6c1fdd50423f514e5f`. The extracted JSON members had SHA-256 `8fcb27ede62f293d6593466076f068cc46d85d95777b28b5817bdcf92568248b` and `7b45a07ec89fc1b57ac0db060243d1294786db2a358189e3ef82ed9dfd827f52`; **their only substantive difference is Git checkout provenance** (push head versus PR merge ref). Both contain identical cohort, model counts, fallbacks and prediction commitment. [Machine-readable aggregate registry](FRESHRETAIL_LT_V20_SEAL_RESULT.json) preserves exact conditions and limits.

**Failure preserved:** The first [push execution #40709259647](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40709259647) failed **after successful source hash** because the new v2.0 selected-row stream mistakenly passed legitimate *earlier TRAIN years* to the frozen 90-day evaluator. This was a v2.0 input-filter defect, not a data-quality failure. The corrected stream discards rows before 2025-04-15 and still rejects rows on/after the EVAL origin; two additional fictional negative controls passed. The failed run is not represented as a successful forecast seal.

**Decision:** only TRAIN-side forecast commitment is now verified. **EVAL labels remain unread in v2.0**. The separate v2.1 scorer must independently regenerate and compare this pinned digest **before opening EVAL**, then fail closed on missing seven-day cohort coverage, preserve the v1.8 matching day-weighted paired whole-store interval and report success/failure/inconclusive without retuning. Forecast scores, lost demand, intervention value, human review and deployment remain **TBD**. No maturity change, merge or release.
