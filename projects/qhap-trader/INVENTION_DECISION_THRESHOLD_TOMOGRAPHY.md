# QHAP-TRADER Research Invention Proposal: Decision-Threshold Tomography (DTT)

**Proposed:** 2026-11-03  
**Classification:** Original research proposal / unvalidated mathematical method, **not** a verified world-first invention, patentability finding, or profitable trading strategy.  
**Deployment:** Offline research and simulated trading only. No broker, live order API, leverage, or money movement.

## One-sentence concept

Map the *density of hypothetical trading-policy changes* under small counterfactual price, volume and information shocks; then test whether the resulting "**decision cliffs**" explain subsequent observed order-flow instability beyond existing microstructure features.

Instead of forecasting the next price directly, the method asks: **where might precommitted trading plans flip together, and does the real market show independent signs of that hypothetical coordination?**

The word *tomography* is metaphorical. It does not imply access to actual private investor beliefs, identity, portfolios, order instructions or intentions.

## Novelty and evidence boundary

Prior work already examines opening auction imbalance, price discovery, retail attention, heterogeneous-agent models, order-book trader clustering and stop-loss cascades. We must not claim these are new inventions. DTT proposes a distinct **pre-frozen hypothetical plan ensemble → counterfactual switching surface → independently confirmed behavior → net-of-cost rejection or paper decision** research sequence.

Its global novelty is **unverified** and may prove absent after a proper literature, patent, or commercial system review. Its prediction and profit claims are **unverified**. The research is useful even if every proposed market hypothesis fails: the counterfactual decision record and falsification infrastructure remain auditable.

## Representation: the market of conditional plans

Before observing the day's intraday prices, define a frozen population of *hypothetical* policies indexed by j. These are not actual traders and their weights are not estimates of the actual market population unless independently identified.

Examples:
- Opening-range breakout learner: activate a buy hypothesis only after confirmed price and turnover thresholds.
- Gap-fade watcher: activate a wait/buy rule only after a preregistered reversal confirmation.
- Prior-low risk exit: activate an exit flag when a predefined level breaks.
- No-trade uncertainty watcher: abstain when data or liquidity becomes unreliable.
- Common-model follower: a stylized agent using widely available technical signals; shared decision thresholds represent a **testable crowding hypothesis**, not evidence that AI traders are synchronized.

Every plan contains an objective threshold, timestamp, permitted input schema, activation condition, unit weight, and immutable version hash. The candidate weight distribution must be fit only on historical training dates (or declared uniform) and stress-tested under alternative distributions.

## A switching surface

Let:
- \`s_t\` be features that were actually available at market time t, with data timestamps <= t;
- \`pi_j(s)\` be the bounded action of hypothetical plan j in {-1, 0, +1} meaning *exit/inactive-hold/buy intention* for **simulation**, not a live short or an exchange order;
- \`w_j >= 0\` be fixed weights summing to one;
- \`delta\` a plausible local **hypothetical** price/volume shock, not a predicted future outcome.

Define:

\`\`\`text
Switching mass:   C_t(delta) = Σ_j w_j · 1[pi_j(s_t ⊕ delta) ≠ pi_j(s_t)]
Signed change:    D_t(delta) = Σ_j w_j · (pi_j(s_t ⊕ delta) − pi_j(s_t))
Local fragility:  F_t(h) = E_delta[ C_t(delta) ], delta ~ predeclared stress grid within ±h
Direction split:  (BUY-activating mass, EXIT-activating mass, disagreement)
\`\`\`

The \`⊕\` operator changes *only* predeclared perturbable variables, respecting consistency constraints such as positive prices and attainable volume. A rich extension uses interval-valued uncertainty in the state and policy weights; a simple bounded grid is enough for a first falsifiable study.

A high \`C\` is **not** equivalent to a directional trading edge. It may suggest possible volatility, a false positive from an unrealistic population model, or nothing at all.

### The genuinely important second stage: independent confirmation

Observe **post-event** features from authorized timestamps:
- signed order-flow or order-book imbalance if lawfully available;
- gap between prior pre-open expectation and opening response;
- relative volume, realized volatility and liquidity changes;
- whether the specific beforehand-predicted activation side appears in the *subsequent* data.

**No future information is permitted to validate a trade decision at time t.** The confirmatory snapshot becomes eligible only when actually observed, and execution must occur no earlier than a later permitted price observation.

Compute a **falsifiable activation hypothesis**, for example:

\`\`\`text
A_t = separately calibrated agreement between DTT's *prior* directional
      policy-switching prediction and subsequently observed independent
      order-flow/liquidity evidence.

Trade candidacy = F_t above a prospectively fixed threshold
                  AND A_t valid
                  AND net-of-cost strategy edge positive
                  AND every independent risk gate PASS.

Otherwise: abstain.
\`\`\`

The final \`A_t\` calculation is to be specified and frozen *before* final holdout analysis. **Do not** select a convenient post-event confirmation signal after looking at returns.

## Core innovation test: predictable instability, not price fortune-telling

The *primary preregistered endpoint* should be one of the following, not a chosen-after-the-fact profitable equity curve:

1. Does frozen \`F_t\` improve prediction of short-horizon realized volatility / large price excursions after controlling for realized recent volatility, spreads, turnover, order imbalance, time-of-day, and opening gap?
2. Does the *signed* \`D_t\` add incremental **directional** out-of-sample information under realistic execution assumptions?
3. Does an independent confirmation gate improve selective-execution net expectancy and tail risk over the same baseline strategy without DTT?
4. Are results robust to removing all assumed crowd weights, shifting plan thresholds, disabling psychology proxies, or replacing simulated plans with randomized placebo plans?

### Essential null and placebo experiments

- **Placebo-policy ensemble:** preserve plan counts and aggregate activity but randomly shift decision thresholds within historically feasible bounds.
- **Matched-complexity control:** ordinary opening range, VWAP, volatility, liquidity and imbalance features with equally flexible model capacity.
- **Temporal falsification:** do forward-only tests; randomizing the relation between pre-open hypothesis and later day should destroy genuine explanatory power.
- **Cross-security control:** compare liquid eligible stocks on independent trade dates, not only a highly curated set of winners.
- **Ablation:** remove pre-open state, remove shared-model followers, remove switching-surface, remove independent confirmation.
- **Transaction-cost stress:** pessimistic fills, slippage, exchange/statutory charges and 2× modeled fees; skip if no robust positive advantage.
- **Calibration/uncertainty:** limit trade candidacy in out-of-distribution sessions and when signals rest on an unstable agent population or poor data.
- **Multiple testing:** freeze code and hypotheses before evaluating untouched holdout; record all variants tried.

### Failure criteria

DTT should be **retired or remain academic** if its effects vanish after adding normal market features, are too small to survive costs, depend on unobservable data, or appear only after optimizing weights to the same period being evaluated.

Do not put unvalidated dynamic agent learning into the live trading session. Freeze versions before market open; learning/evolution occurs offline with independent validation.

## One worked conceptual example (not market evidence)

Assume 100 equally weighted **hypothetical** rule policies. The observed stock price is ₹1,009.80. A small price increase could cross 32 buy activation thresholds; a different hypothetical price drop could cross 18 exit thresholds. Then, for that **specific upward hypothetical shock**, the simulated buy-switching mass is 0.32. This is an artifact of the invented policy population, **not** "32% of real investors" or a forecast of buying volume.

DTT would next ask whether legally observed order flow *after* the price approaches the zone supports a separately calibrated effect. If not, the default decision is **NO TRADE**.

## Required data

- Correctly timestamped corporate events and prior closes, authorized NSE intraday data, exchange calendar, complete fee tables.
- The exchange disseminates indicative pre-open equilibrium prices, quantities and imbalance fields. Availability of *historical point-in-time snapshots* depends on a separate data source/license; do not assume public webpage access gives historical depth or a redistribution right.
- No inference from scraped investor accounts, private order books, private social content, or unauthorized broker data.
- If only one-minute OHLCV is available, test a weaker **price-threshold-only DTT**; omit unmeasured order-flow claims.

## Implementation roadmap

1. Pure, deterministic policy-switching scanner and synthetic invariants — software feasibility **only**.
2. Freeze a transparent, small policy taxonomy before selecting market history.
3. Obtain lawful point-in-time NSE data; align pre-open and continuous session timestamps.
4. Baseline + placebo + DTT ex ante evaluation on multiple chronological windows.
5. Estimate out-of-sample calibration, statistical confidence and cost-aware utility; reject if no improvement.
6. At least 60 complete prospective paper sessions under fixed rules, with full incident and abstention ledger, then independent review.
7. **No live execution implied or authorized.**

## Related research (not evidence of DTT's profitability)

- Tripathi, Dixit & Vipul, 2021: Indian NSE order imbalance and short-run information content: https://doi.org/10.1016/j.frl.2020.101863
- Jindal, Bajpai & Yadav, 2026: some NSE order-imbalance strategy gains vanish after costs: https://www.ubplj.org/index.php/jpm/article/view/2235
- Gupta & Kumar, 2025: deeper NSE order-book levels and return predictability: https://digitalcommons.newhaven.edu/americanbusinessreview/vol28/iss1/3/
- Liston, Gretton & Lensky, 2024: agent-based stop-loss cascades: https://doi.org/10.5220/0012371400003636
- NSE 2026 pre-open session: https://www.nseindia.com/static/products-services/equity-market-pre-open
- Meshcheryakov & Winters, 2022: retail investor attention and intraday order-book patterns: https://doi.org/10.1016/j.irfa.2020.101627

**Boundary:** this document defines a potentially differentiated hypothesis. It does not establish scientific priority, novelty, a patent, predictive performance, or investment returns.
