# Intraday time-of-day / selective abstention: exploratory audit (12 Nov 2026)

**Research, not live execution.** This report preserves the *previous* historical scratch-study summaries. New intraday_clock_replay.mjs is a separate, causal, offline-tested implementation and has **not** yet reproduced these real-data figures, so do not claim they are its output.

## Source and data limitations
- Pinned community source: https://github.com/gsidhu/nse-intraday-data, commit c95d7f187c2a317ca6a2287148cf10c50a80e928.
- 6 February dates/year in 2021, 2022, 2023, ACC and RELIANCE: 36 requested stock-days, 34 complete sessions on 18 distinct market dates, two incomplete ACC 2022 days excluded. Raw minute records were not committed or redistributed.
- Selected days and 2021 development sets have been previously inspected; no pristine forward or untouched historical holdout. This is NOT the NHPC symbol used for the live Upstox pilot.
- Source exchange authenticity and legal reuse rights unverified. A public repository's software MIT license doesn't establish rights to use exchange data for automated calculations or virtual trading.
- The data have 09:16–15:29 historical minutes, lack the official opening 09:15 auction print, and don't model exchange changes to the 2026 Closing Auction Session.

## Prior exploratory scratch-simulation results
Rules are research-only **1-minute** 5/20 *simple moving average* long crossover proxies, not the current five-second V3 model. FAST permits six round trips per stock-day, ONE permits one, TIME_GATE permits one only on 10:00–11:30 or 13:30–14:20 completed signals if 10-minute momentum is ≥0.35% and completed close exceeds cumulative same-day approximate VWAP. Entries modeled next-minute open; exits on stop/target/cross/down or 14:55 opening. Each stock-day uses its own reset ₹10,000 simulated account and max ₹2,500 position, not one compounded ₹10,000 portfolio. Illustrative fees plus extra slippage per side; no executable fill or broker-fee certification.

| Additional slippage per side | FAST (204 virtual round trips) | ONE (34) | TIME_GATE (5) | NO_TRADE |
|---|---:|---:|---:|---:|
| 5 bps | -₹819.51 | -₹104.69 | -₹2.05 | ₹0 |
| **15 bps** | **-₹1,674.39** | **-₹242.99** | **-₹17.57** | **₹0** |
| 30 bps | -₹2,929.90 | -₹450.24 | -₹40.86 | ₹0 |

15bps by selected February year-slice:

| Year | Stock-days | FAST | ONE | TIME_GATE |
|---|---:|---:|---:|---:|
| 2021 | 12 | -₹509.41 | -₹107.65 | -₹25.04 |
| 2022 | 10 | -₹575.75 | -₹99.96 | -₹15.66 |
| 2023 | 12 | -₹589.23 | -₹35.38 | +₹23.13 |

The 2023 TIME_GATE gain was from **one** winning virtual trade; the gate had only five total trades across 34 stock-days. The date-cluster 10,000 resample historical descriptive interval for its 15bps sum was [-₹77.03, +₹46.06], NOT a future profit probability or confidence interval. NO_TRADE outperformed the three trading proxies in all three cost scenarios.

## Time-of-day volatility
Equal-stock-day average absolute one-minute log return (bps), **not directional profitability**:

| Time IST | bps |
|---|---:|
| 09:16–09:29 | 13.45 |
| 09:30–09:59 | 10.05 |
| 10:00–10:59 | 7.98 |
| 11:00–11:59 | 6.60 |
| 12:00–12:59 | 6.32 |
| 13:00–13:59 | 6.09 |
| 14:00–14:59 | 7.52 |
| 15:00–15:29 | 7.39 |

Opening movement is larger than midday, but this doesn't imply entry edge. An option to abstain reduced modeled trading costs and losses; it did NOT produce stable positive simulated earnings.

## New reusable, licensed-data-only replay engine
The new module [intraday_clock_replay.mjs](intraday_clock_replay.mjs) implements four fixed alternatives, strict 374-minute session parsing, next-open signal scheduling, 14:55-open exit, stop-first/gap adverse assumptions, independent position limits, illustrative fee model, and sanitized aggregate outputs. Synthetic unit tests run with Node.js 22; no vendor feed, account, token or public data download. Its results may differ from the original exploratory scratch calculation because it independently models event ordering. Historical numerical reproducibility against approved raw data is **still pending**.

Usage from repo root:

    node --test projects/qhap-trader/experiments/test_intraday_clock_replay.mjs
    node projects/qhap-trader/experiments/intraday_clock_replay.mjs /licensed/data/root /licensed/manifest.json 15

Input shape YYYY/MM/DD/SYMBOL.csv, no header, columns SYMBOL,YYYYMMDD,HH:MM,open,high,low,close,volume,open_interest. Manifest JSON array with date and symbol; source files stay local under the user's own appropriate rights. Missing minute data rejects the whole stock-day; never forward-fill and never substitute prices.

**Decision:** Maintain NO_TRADE as preferred comparator, don't automatically promote TIME_GATE from these developmental dates, require genuinely unexamined multi-regime data under permissible terms. No real trades or unattended exchange data collection.

**Licensing/compliance references:** https://www.nseindia.com/static/market-data/nse-data-policy and https://archives.nseindia.com/content/circulars/COMP56426.pdf (2023 NSE warning against use of its data for gaming/virtual trading). For market-data-dependent simulation, obtain a clear permitted use before further activities.
