# Retail R&D — decision-changing prior art and data execution gate (2026-10-26)

**Stage:** Research / Architecture (unchanged). **Evidence:** literature review plus a committed *attempt* to execute pinned publisher data. **No public-data results are claimed until an actual run and its outputs are inspected.**

## Primary-source prior art

Joseph Azar, *A Reproducible, Leakage-Free Pipeline for Censored Demand Forecasting and Inventory Optimization on FreshRetailNet-50K*, **Inventions** 11(5), 89, published **2026-08-30**, DOI [10.3390/inventions11050089](https://doi.org/10.3390/inventions11050089). The author's [public reproducibility repository](https://github.com/josephazar/FreshRetailnet-50k-Analysis) documents code, tests and an immutable release. The paper evaluates the official 90-day train / 7-day evaluation split across 50,000 store-product series, with train-only feature fitting and recursive forecasting. Its reported **32.79% WAPE after validation-defined recentering** and inventory profit are **the author's results**, not results reproduced here. The paper explicitly calls inventory profit an **observed-sales proxy**, not identified latent-demand profit.

Original dataset and pinned train snapshot: [Dingdong-Inc FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K); [revision 08c1fab... train.parquet](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/blob/08c1fab7f9257bc73679d415d65d644165d351d4/data/train.parquet), publisher-reported SHA-256 `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d`. CC BY 4.0 is declared by the dataset publisher. **The local research environment cannot download this file; no local byte hash has been verified.**

## Decision, not novelty claim

The paper already supplies a leakage-free forecasting / inventory pipeline with real publisher-data experiments. Accordingly, **do not present the portfolio's chronological split, stockout correction or forecast-to-order concept as novel**. A plausible *testable differentiation* is to use the exact positions of the 24 hourly stock-status flags rather than only the daily stockout count; the paper identifies exact-hour recovery as a follow-up, not as a demonstrated improvement. Any such claim needs a same-protocol, same-data, leakage-safe ablation and an independent reviewer. Another plausible contribution is rigorously audited provenance and negative controls, but that is software-method evidence rather than forecasting superiority.

## Committed real-data attempt

The [pinned-data GitHub Actions workflow](../../../.github/workflows/retail-pinned-data.yml) was added to the **existing Retail draft PR #9**, not to main and not as a scheduled automation. It is designed to download **only the official training Parquet**, verify the publisher-reported SHA-256 against the downloaded bytes, run the existing strict exporter and disk-backed frozen three-origin baseline, check 4,500,000 rows, and retain only small provenance and score JSON artifacts (no raw publisher rows). Python 3.13 and `pyarrow==20.0.0` are declared; actual runner OS, package version, output digests, elapsed time and outcomes remain **TBD** until execution.

**Important comparison boundary:** This would be a **train-only rolling-origin observable-sales smoke test**, with frozen offsets 42/56/70 and seven-day horizons. It **does not execute the official held-out 90/7 evaluation**, does not reproduce the cited paper's model, and cannot be compared numerically to the paper's 32.79% WAPE. The existing `publisher_split_gate_v11.py` is a date-only preflight, not a complete official evaluator.

## Advancement / reframe

1. Observe a hosted run for the exact workflow commit; preserve logs, artifacts, actual downloaded-byte SHA-256, exporter output SHA-256, dependency versions, runtime and any failures. Until then: **CI status TBD; real-data results TBD**.
2. If the pinned train hash or schema fails, **record the mismatch and stop**; do not relax provenance, change the source revision silently, or label fictional data as real.
3. If the rolling-origin smoke passes, freeze a separate **official 90/7** evaluation, then compare transparent baselines and exact-hour versus daily-count recovery under identical chronology, matched evaluation populations and predeclared metrics.
4. Reframe/stop the differentiated method if exact-hour recovery offers no reproducible gain against simpler count-based or seasonal baselines, or if the apparent gain disappears under strict leakage controls.
5. No maturity upgrade, release, collaboration claim, commercial impact or patentability conclusion follows from the workflow's existence.

**Four lenses:** Hiring manager — show executed, inspectable evidence rather than workflow presence; technical reviewer — demand official-split comparability and source hashes; innovation leader — distinguish hypothesis from established prior art; founder — observed-sales proxy is not validated inventory profit.
