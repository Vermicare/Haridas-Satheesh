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
