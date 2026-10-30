# FreshRetailNet-LT — publisher semantics evidence audit (2026-10-30)

**Evidence type:** public-documentation review, not a benchmark rerun, author confirmation, raw-row audit, or external review. **Maturity:** Retail Research / Architecture, unchanged. **Purpose:** determine whether the additional observed-sales-floor assumption used in [v2.5](FRESHRETAIL_LT_V25_SALES_FLOOR_RESULT.md) is independently supported.

## Sources checked (public, retrieved 2026-10-30)

1. [Dataset publisher's FreshRetailNet-LT card](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-LT) (card states version 1.0, 2026-02-02). It calls `sale_amount` **daily sales quantity after global normalization**, `hours_sale` **hourly sales quantity after global normalization**, `stock_hour6_22_cnt` the **number of out-of-stock hours from 06:00 to 22:00**, and `hours_stock_status` hourly out-of-stock status. These are publisher field descriptions, not an audit of underlying transaction semantics.
2. [Publisher's LT forecasting leaderboard/evaluation notes](https://huggingface.co/spaces/Dingdong-Inc/FreshRetailNet-LT-Leaderboard) and [published static evaluation notes](https://dingdong-inc-freshretailnet-lt-leaderboard.static.hf.space/index.html): forecast July 14–20, 2025 using pre-July-14 history; evaluation-period sales and stockout answer fields must not enter prediction inputs/tuning. Local scoring filters to `psd >= 0` and `stock_hour6_22_cnt == 0`. **Evaluation labels are public**, not a hidden-label test. The notes explicitly state that true unmet demand during actual stockouts is not directly observed.
3. [Original FreshRetailNet-50K paper](https://arxiv.org/abs/2505.16319) and [publisher baseline](https://github.com/Dingdong-Inc/frn-50k-baseline) are related **prior dataset/method references**, **not** a substitute for missing LT-specific field-level transaction definitions. The LT card's technical-report link says *it will be posted later* and its bibliography includes a placeholder arXiv identifier. This is an observed documentation gap, not proof that no further documentation exists elsewhere.

## Decision table

| Question | Public evidence | Gate |
|---|---|---|
| Is `sale_amount` labeled a normalized sales **quantity** rather than monetary revenue? | **Yes**, publisher dataset card. | Field-description supported; underlying transaction construction unverified. |
| Is `hours_sale` described as normalized hourly sales quantity? | **Yes**, publisher dataset card. | Field-description supported; `sale_amount == sum(hours_sale)` across actual target rows **TBD**. |
| Does official forecasting scoring use fully in-stock rows only? | **Yes**, leaderboard `stock_hour6_22_cnt == 0`. | Scoring rule supported; does not identify latent demand during censored days. |
| Is `sale_amount` guaranteed a lower bound for **the same normalized latent-demand target** on every censored day? | **Not established** by the checked public documentation. | **UNVERIFIED**. Return/cancellation/substitution handling, inventory/transaction timing, global scaling positivity/consistency, and day/window alignment **TBD**. |
| Is the 2025 evaluation a hidden-label confirmatory cohort? | **No**; labels are explicitly public. | Prior v2.5 is post-hoc sensitivity only. |

## Consequence for the existing v2.5 result

Do **not** replace or strengthen the verified v2.5 numeric intervals. Conditional on its *unverified* same-target floor assumption, the interval for weekday-median minus causal stockout history is **[−0.046500140, +0.070014369]** and versus last-observed is **[−0.175996512, +0.260968890]**; **both cross zero**. These are logical sensitivity bounds, **not** confidence intervals or proof of latent-demand model superiority. The publisher's quantity label is useful semantic clarification, **not** independent validation of the floor assumption. No new model was trained, no additional dataset rows were fetched, and no test metrics were generated in this audit.

## One decisive next experiment / stop condition

Before any stronger full-period ranking claim, obtain **independently inspectable publisher documentation or a direct nonbinding technical clarification** on (1) net versus gross sales, returns, cancellations and substitutions, (2) same-period hourly/daily aggregation and scaling, (3) whether stockout flags and target quantities share the same business-day boundary, and (4) whether every recorded sale is included in the defined latent-demand estimand. Separately test the `sale_amount`/hourly aggregation identity on the **already pinned** public dataset without refitting models or reading any new held-out labels. If the floor is not justified, withdraw the v2.5 conditional interpretation and retain v2.4's weaker bounds; if ranking remains unidentifiable, reframe toward robust decisions under partial identification.

**Four-lens review:** hiring manager — responsible negative research decision; technical reviewer — explicit estimand/normalization/transaction checks; innovation leader — established censored-demand prior art, no novelty/patentability assertion; founder — no measured inventory, revenue, customer or deployment value. **Unknown = TBD.** No confidential data, private contact details, outreach tracking, releases, merges, or external commitments.
