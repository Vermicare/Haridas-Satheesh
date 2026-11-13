# QHAP-TRADER — prospective statistical sample design (13 November 2026)

**Status: OFFLINE MATHEMATICAL FEASIBILITY ONLY. NO_TRADE.**

This research plan is deliberately independent of any still-unresolved
Upstox data licence, any market-opening-time feed, and the previously
inspected February 2021 development outcomes. It introduces **no new
historical or forward observations** and is neither a calibrated
strategy nor proof of a positive expected return.

## Why a fixed 60-session milestone is insufficient

QHAP's earlier forward protocol asks for *at least* 60 complete
authorized, independently reviewed **market sessions** as a
precondition for external review. Sixty session dates can contain
many trades or very few. Neither 60 sessions nor 60 trades proves
a favourable return distribution, independent samples, or an
economic advantage over NO_TRADE.

The merged [cost-aware hypothetical payoff model](precommitted_payoff_viability.mjs)
has a fixed long position of ₹2,000, gross +1.5% target and -1.0% stop,
and theoretical break-even win percentages of **51.94%, 55.96%,
64.00%, and 92.25%** at 0, 5, 15, and 50 additional basis points of
economic adversity *per side*. If hypothetically 5% of losing trades
suffer an additional 200-basis-point stop gap, these thresholds become
**53.78%, 57.64%, 65.37%, and 92.55%**. All are illustrative
under indicative brokerage, tax and fee rounding, **not** an empirically
estimated strategy win rate or tail-gap probability.

We now ask: *If* each of a given number of imaginary trades had a
fixed independent binary target/stop outcome with those exact net
payoffs, how many target outcomes would be required so that a
two-sided 95% Wilson **lower confidence bound on the hit fraction**
was strictly above the applicable theoretical break-even fraction?

It is a **research power/sampling diagnostic**, not a live model.
This bound is only valid under strong IID Bernoulli assumptions;
actual signals may cluster by date, instrument or market regime,
and payout magnitudes may differ from the fixed hypothetical levels.
The expected net return, daily loss concentration, execution
liquidity and source permission require separate independent evidence.

## Precommitted grid

Fixed imaginary independent trade counts: **30, 60, 100, 250, 500**.
All 4 fee/adversity levels and both 0%/5% losing-trade-gap
hypotheses are retained; no case is optimized or selected later.
The 95% Wilson lower bound uses \(z=1.959963984540054\).
There is no use of random seeds, data prices, indicator thresholds,
market-event streams, or price-history downloads.

| Extra adverse slippage each side | Theoretical break-even win rate, no gap | Minimum target wins / 60 imaginary trades | Minimum target wins / 250 imaginary trades | With 5% tail gaps, wins / 60 | With 5% tail gaps, wins / 250 |
|---:|---:|---:|---:|---:|---:|
| 0 bp | 51.94% | **39/60** | **146/250** | 40/60 | 150/250 |
| 5 bp | 55.96% | **42/60** | **156/250** | 43/60 | 160/250 |
| 15 bp | 64.00% | **46/60** | **175/250** | 47/60 | 179/250 |
| 50 bp | 92.25% | **60/60** | **239/250** | 60/60 | 240/250 |

At 30 imaginary trades, even **30/30** cannot put a
two-sided 95% Wilson lower bound above the >92% high-friction
break-even requirement. At 60 imaginary trades, even the favorable
fixed-payoff scenario would require a spectacular **60/60 wins**
under the harshest friction assumption. This does NOT mean any
real QHAP trading strategy achieved or can achieve such a hit rate.

For comparison, 42/60 = 70% hypothetical hits has a Wilson lower
bound of only **57.49%**; 48/60 = 80% hypothetical hits has a
lower bound of **68.22%**; 175/250 = 70% has **64.05%**. These
are mathematical examples, not data observations.

## What a real holdout assessment would require

1. Independently legitimate source entitlement for *exact* proposed
   cash-equity historical analysis and separately for any real-feed
   virtual paper activity; no unapproved licensed data collection.
2. Pre-frozen unchanged source, algorithm, calendar, cost model,
   decision window, and all comparison policies before unseen data
   access. No reused February 2021 inspected days.
3. Full authorized session reporting, 60+ independently verified
   prospective trading dates, explicit missing/outage and no-trade
   days, real gap/partial-fill behaviour and correct symbol risk
   accounting; 60 dates alone never substitutes for adequate sample
   size and independence.
4. **Primary statistical evidence:** net costed rupee return
   *per independent session* with uncertainty intervals using
   appropriate **block/day-level** resampling or independently
   validated sequential/multiple-testing procedures. Preserve
   serial dependence and include all losing, no-trade and data-gap
   dates. An observed hit count alone does not certify positive
   net rupees.
5. Negative holdouts, loss tails and each distinct economic/regime
   stress scenario remain visible. Do not quietly tune after
   observing results. NO_TRADE remains an unconditional
   comparator worth ₹0 gross and net.
6. Independent review and explicit account/SEBI/broker approval
   remain **separate future conditions** for any real-money
   execution; none are given or created by this study.

## Offline code, tests and hard limits

[statistical_evidence_sample_design.mjs](statistical_evidence_sample_design.mjs)
derives *only* fixed conditional sample-size thresholds from the
unchanged merged 2026 indicative Upstox cost calculation. Its
[regression tests](test_statistical_evidence_sample_design.mjs)
verify monotonic adverse cost and gap effects, count validity,
minimal required-win arithmetic and lack of any real-order route.

Run:
    node --test projects/qhap-trader/live_readiness/test_*.mjs

Every result preserves:
- \`anyActualTradeObservationsUsed:false\`
- \`independentlyVerifiedForwardSessions:0\`
- \`strategyPositiveEdgeIndependentlyVerified:false\`
- \`marketDataEntitlementVerified:false\`
- \`canTrade:false\`, \`realOrderRoutePresent:false\`
- \`recommendedAction:NO_TRADE\`

The next non-synthetic source of **strategy performance** remains
an **independently permitted, complete, previously unseen** dataset;
unavailable licence proof must not be fabricated by statistical code.
