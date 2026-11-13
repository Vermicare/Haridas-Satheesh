# QHAP-TRADER — bounded 2026 illustrative fee audit (2026-11-05)

**Classification:** Independent source-to-formula desk audit, NOT an independently validated broker contract note, historical 2021 fee schedule, trading result, or data entitlement. No trading authorization.

## Scope and falsification criterion

Audit the exact fee expressions in `experiments/costed_intraday_pilot.mjs` (main Git blob `13c3e9d8857f22610435e9c9b1f2d4ee03888d0f`) against a current broker's *published* Indian NSE equity-intraday schedule. FAIL if any modeled percentage or taxable base differs; record exclusions and rounding assumptions separately. Do not modify historical P&L, fit parameters, or assert 2021 historical accuracy.

Primary published references checked 2026-11-05:
- Zerodha charges: https://zerodha.com/charges/
- Zerodha STT rounding explainer: https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated

## Line-item reconciliation (current illustrative NSE intraday, long buy then sell)

| Item | Committed expression | Current published schedule | Finding |
|---|---|---|---|
| Brokerage | min(₹20, 0.0003 × buy value) and likewise sell | 0.03% or ₹20, lower, per executed order | MATCH for exactly one execution each leg; actual split fills/orders not modeled |
| STT | floor(0.00025 × sell value + 0.5) | 0.025% sell side, nearest rupee | MATCH for nonnegative single-sale example; per-contract-note aggregation and broker rounding details not independently tested |
| NSE transaction | 0.0000307 × (buy+sell) | 0.00307% | MATCH for the published aggregate rate, not a separately itemized exchange/IPFT reconciliation |
| SEBI | 0.000001 × (buy+sell) | ₹10/crore = 0.0001% | MATCH |
| GST | 0.18 × (brokerage + exchange + SEBI) | 18% of same base | MATCH |
| Stamp | 0.00003 × buy | 0.003% on buy | MATCH |

**Independent arithmetic vector, not a live broker calculator comparison:** buy turnover ₹100,000; sell turnover ₹101,000; one buy and one sell executed order; zero simulated slippage. Brokerage ₹20 + ₹20; exchange ₹6.170700; SEBI ₹0.201000; GST ₹8.346906; buy stamp ₹3.000000; sell STT ₹25 after rounding ₹25.25 to nearest rupee. **Modeled total ₹82.718606; net ₹917.281394** before any separately excluded costs. These are raw mathematical component amounts; actual contract-note rounding can differ.

## Material limits / unresolved gates

1. **Historical mismatch:** Applying this 2026 published schedule to 2021 February prices is *illustrative only*. The exchange fee and any applicable IPFT contribution, broker schedule, 2021 tax/rate effective dates, and historical contract-note rounding are **NOT VERIFIED**. No claim of 2021 fee correctness.
2. **Exchange/IPFT split:** The current published 0.00307% is a headline aggregate. Do not separately add an IPFT component without confirming whether the chosen broker's published transaction line already includes it; doing so risks double counting. Exchange-issued effective-date circular and contract-note line reconciliation remain pending.
3. **Order semantics:** The pilot charges one buy and one sell. It cannot establish fees for multiple execution orders, broker auto square-off, partial fills, rejected orders, or contract-note rounding and aggregation. Any such unknown must remain an explicit scenario limitation, not silently treated as zero.
4. **Not a new test pass:** This is a documented source/formula inspection and independently computed arithmetic vector. No Node tests or GitHub Actions were executed as part of this audit; existing historical replay snapshots and negative findings are unchanged.
5. **Not broker-agnostic:** Zerodha is a *reference* schedule; Upstox application status does not establish an approved account, broker tariff, data entitlement, or execution access.

**Gate decision:** CURRENT_RATE_FORMULA_DESK_CHECK = PASS (six published line-item categories for the stated simple round trip). HISTORICAL_2021_CHARGES = UNKNOWN/BLOCKED. CONTRACT_NOTE_AND_ORDER_LEVEL_RECONCILIATION = UNKNOWN/BLOCKED. AUTHENTICATED_REPLAY = BLOCKED.

**Next falsifiable experiment:** obtain an official NSE cash-market exchange/IPFT effective-date circular and an independently published broker charge-calculation worked example, compare each item including rounding with a deterministic unit test, then preserve failures. No licensed data, funding, broker connection or live orders.
