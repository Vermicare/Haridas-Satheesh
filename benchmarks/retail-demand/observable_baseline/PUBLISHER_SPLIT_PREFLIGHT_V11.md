# Retail v1.1 — publisher train/eval split preflight (2026-10-26)

**Stage: Research / Architecture — unchanged.** This is a fictional date-only software contract, **not** a public-data benchmark, model evaluation, publisher-origin attestation, or deployment.

## Decision-changing dataset distinction

The [official FreshRetailNet-50K dataset card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K) describes 50,000 store-product series and separate 4,500,000-row train and 350,000-row eval splits: 90 train dates and seven evaluation dates per series. The [original paper](https://arxiv.org/abs/2505.16319) is prior art for stockout-aware forecasting. The existing 42/56/70 rolling-origin seven-day tests are **historical within-train backtests**, not evaluation on the publisher's held-out split. Both may be useful, but they must be labeled separately.

## Executable contribution

- [publisher_split_gate_v11.py](publisher_split_gate_v11.py) verifies a **single per-series** fictional date manifest: exactly 90 chronological consecutive training dates, seven chronological consecutive evaluation dates, and no gap or overlap across the boundary.
- Optional declared fitting dates must all belong to the training window. Missing fit evidence is explicitly **unchecked**; dates alone cannot prove the absence of feature leakage.
- [12 fictional tests](test_publisher_split_gate_v11.py) cover valid 90/7, short splits, overlaps, boundary/internal gaps, out-of-order dates, invalid dates, held-out/pre-train fitting, malformed fit evidence, and deterministic output.
- CPython 3.13.5/Linux standard library, two independent clean-directory executions: **12/12 passed in each**; same test outcomes and byte-identical demo SHA-256 **52e2247fcd93e78a234d9f5ebb16da838f7c36773c4146a026159e57023023f3**. Unittest elapsed-time log lines are not byte-identical.
- Code Git blob: **d171d90470c59b9cebce9c56714ba25a75440bb1**; tests Git blob: **46c32c50eb89cf3dc9f273ede146c6f0864e5960**.
- GitHub Actions Linux/Windows CI: **TBD until the branch head workflow jobs are inspected**.

Run from this directory: 'python -m unittest -v test_publisher_split_gate_v11.py' and 'python publisher_split_gate_v11.py'.

## Next evidence gate

1. Download publisher-pinned **train and eval** Parquet bytes and verify immutable revision, separate SHA-256s and license. Current publisher file hashes locally verified: **TBD**.
2. Extract per-series train/eval dates **with identity and duplicate checks** and run this preflight on real bytes. This helper alone does not check store/product identity.
3. Ensure fitting, learned preprocessing, feature construction, cohort selection and hyperparameter tuning never use eval labels or future information; preserve an independently reviewable training provenance record.
4. Compare the frozen baseline with the publisher's reference method on official held-out data, reporting both forecast and decision metrics with honest uncertainty. Real-data scores: **TBD**.

**Reframe** if pinned data violate assumed split structure, or if stockout correction does not beat seasonal naive under preregistered comparable conditions. No maturity advancement or release.

**Four-lens review:** hiring manager—visible reproducibility; technical reviewer—fail-closed split boundary; innovation leader—distinguishes prior art and protocols; founder—no fabricated business outcome.
