# QHAP-TRADER — frozen hypothetical payoff viability (13 November 2026)

**Decision: NO_TRADE / do not simulate market-driven fills with unapproved live data.**
This is an **economics falsification** of a price/fee *assumption set*,
not a market simulation, backtest, measured win rate, optimization,
historical finding, approved paper-trading entitlement, or actual profit
forecast. It does not access the NSE, Upstox, broker accounts or market
data.

## The decision-relevant question

For a hypothetical ₹10,000 research account, how much **winning
frequency** would an imaginary repeated binary strategy need simply to
cover friction? A ₹2,000 hypothetical position with a 1.5% gross target
and a 1.0% gross stop might look superficially attractive before
charges. Actual modeled gross win: ₹30; gross loss: ₹20.

This calculation uses the **already merged** 
[2026 indicative Upstox fee engine](upstox_intraday_cost_stress.mjs)
without altering its modeled tax, fixed-cost, rounding, one-sided
STT or conservative IPFT-buffer assumptions. It is **not** an Upstox
contract note and **not** a reliable real fill model. Neither the
1.5%/1% price geometry nor any assumed hit rate came from a
verified strategy-performance distribution.

## Preregistered, non-tuned assumptions

- One hypothetical long BUY at ₹100, quantity 20 (₹2,000); one later
  hypothetical complete SELL at ₹101.50 if target, or ₹99.00 if stop
- **Four fixed extra adverse economic penalties** of 0, 5, 15 and 50
  basis points *each side*; no parameter search
- **200 basis point extra stop-gap penalty**, hypothetically affecting
  0% or 5% of **losing trades**; this is not a measured gap occurrence
  frequency or a claim about an actual stop-market fill
- **Assumed**, not observed, win fractions: 40%, 50%, 60%, 70%, 90%
- 60 purely hypothetical independent trade opportunities for arithmetic
  scaling only; **zero genuine forward trading days or sessions**
- No-trade comparator **₹0**, no trading fees and no estimated P&L
- Current proposed ₹50 maximum loss *per candidate* is a budgeting
  rule, **not a hard maximum loss when gaps occur**

A fixed risk/reward ratio does **not** determine a real strategy's
chance of success. Slippage and fees vary with price, order splitting,
STT/charges rounding, actual account plan and volatility. There are
no independently verified signal classifications, timestamps,
spread/book events, inventory/capital locks, or orders.

## Transparent math

Let \`W\` = illustrative **net** target outcome from the existing fee engine,
\`L\` = illustrative **net** ordinary stop outcome,
\`G\` = illustrative **net** stop with the extra 200 basis-point penalty,
\`q\` = assumed gap fraction among losing outcomes, and \`p\` = assumed
target hit frequency.

\`\`\`text
mean_losing_net = (1 - q) × L + q × G
expected_net_per_hypothetical_trade =
    p × W + (1 - p) × mean_losing_net
break_even_target_hit_rate =
    -mean_losing_net / (W - mean_losing_net)
conditional_60_trade_expected_net =
    60 × expected_net_per_hypothetical_trade
no_trade_expected_net = ₹0
\`\`\`

The denominator must be positive and all source outputs must be valid.
This is an algebraic *required threshold*, **not a probability of
future trading profitability** or a way to imply a positive empirical edge.

The [pure offline module](precommitted_payoff_viability.mjs) computes
the **full 8-case matrix** and retains all 5 hit-rate assumptions per
case, including adverse results. The
[regression tests](test_precommitted_payoff_viability.mjs) verify
consistency against the previously merged fee engine and falsification
invariants: increased friction cannot improve the payoff; adding tail
gaps cannot improve break-even hit rate; high hit-rate *assumptions*
cannot authorize real orders; a 200-bp stop gap breaches the intended
₹50 loss threshold.

## Practical interpretation

- If the calculated required hit rate rises sharply at 15 or 50
  basis points extra adversity, there is **no evidence** that an
  arbitrary breakout strategy can achieve that rate. Do not
  cherry-pick the optimistic cost scenario.
- A hypothetical 200-bp stop gap can exceed the intended ₹50 loss
  budget, even if the original intended stop fits the limit.
  This demonstrates why limit/stop geometry is not a guaranteed
  loss cap.
- A positive value under an assumed 70% or 90% win fraction is
  **not positive strategy evidence**, since the assumed hit rate is
  not derived from legally permitted, genuinely unseen market data.
- Historical February 2021 ACC/RELIANCE outcomes were already
  examined, were fragile/negative at higher modeled friction, and
  **are not retroactively reclassified as independently validated**.
- Under the NSE's published data-use restrictions, real-time
  market-fed hypothetical trades remain blocked without an appropriate
  agreement and independent interpretation. Running this
  constant-input experiment does **not** require data access and
  does not sidestep any source's terms.

## What could change the decision later

1. A documented private research entitlement covering the exact use,
   retention and instrument/source terms.
2. Independently witnessed market/source completeness, session calendar,
   corporate actions and valid candle/timestamp semantics.
3. A pre-frozen strategy tested against genuine untouched multi-regime
   data, with realistic costs, spread/liquidity, stop-gap, and
   uncertainty—and an explicit no-trade comparator.
4. At least 60 fully complete, authorized, prospective monitored
   sessions and independent outcomes review; the sample also needs a
   sufficient number of trades and robust statistics.
5. Separate applicable broker/SEBI/NSE compliance and explicit human
   authorization before any real-money order route.

## Reproduce

\`\`\`bash
node --test projects/qhap-trader/live_readiness/test_*.mjs
\`\`\`

Module exports only
\`assessPrecommittedSyntheticPayoffViability()\`.
Its outputs always set \`canTrade:false\`, \`realOrdersSent:0\`,
\`realOrderRoutePresent:false\`,
\`marketDataRightsVerified:false\`,
\`strategyHasDemonstratedEdge:false\`, and
\`independentlyVerifiedForwardSessions:0\`.
