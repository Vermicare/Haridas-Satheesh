# QHAP-TRADER — Data-gap, execution uncertainty and 2026 cost-scenario audit

**Research date:** 2026-11-04  
**Status:** Validated as a **software safety prototype** in GitHub Actions on PR #30; **not** a production simulator, profitable signal, or real-money trading service. Tests and historical execution results are recorded below.

## Reason for this change

The earlier `costed_intraday_pilot.mjs` reads an entire session and **retroactively rejects it** if *any* minute from 09:30 to 15:00 is absent. That makes missing data after a simulated position opened equivalent to "no trade", an invalid implication: a real trader's position would remain exposed until genuinely filled or reconciled. The previous historical sample happens to contain complete minutes, so this flaw could escape a clean-data regression.

A second source of false certainty is describing a stop price as if it were guaranteed fill. A one-minute bar supplies only open/high/low/close; actual queue position, exchange time, market impact and executable bid/ask are missing.

## Candidate implementation: guarded chronological replay

Files:
- [New pure paper state machine](guarded_paper_replay.mjs)
- [New offline executable CLI](guarded_paper_replay_cli.mjs)
- [Synthetic fail-closed tests](test_guarded_paper_replay.mjs)
- Preserved [original, historically reproducible development-sample replay](costed_intraday_pilot.mjs)

States and consequences:

| State | Meaning | May claim a verified net profit/loss? |
|---|---|---|
| `NO_TRADE` | All required candles were observed, no qualifying entry | ₹0 paper result only |
| `CLOSED` | A simulated entry and a modeled exit were both assigned from available bars | Only modeled net P&L, not a true broker fill |
| `HALTED_DATA` | Missing/invalid minute before any position/entry intention | No further entry; no claim of a clean session |
| `ENTRY_UNCONFIRMED` | The planned next-bar entry was unavailable or no traded volume was observed | **No**; final account valuation is unknown/conservatively withheld |
| `UNRESOLVED_POSITION` | Data vanished while a simulated position remained open | **No**; preserve entry and leave exit/net P&L `null` |
| `LOCKED` | A prior data/position uncertainty or risk breach prohibited subsequent sessions | No further simulated trades until independent review |

A gap detected **after a paper position already closed** does not retroactively erase that completed trade. A gap detected **while a position is open** does not get filled at the last remembered price or presumed stopped out. The book is locked; unresolved account valuation stays `null`.

The engine tests:
- Correct next-minute hypothetical entry after the completed signal bar;
- Conservative stop-first outcome when a minute candle overlaps both stop and target;
- Worse stop exit on an adverse opening gap;
- Scheduled 14:55 opening exit decided **before** viewing that candle's future extrema;
- Missing observations before entry, at intended entry, after entry and at exit;
- Fee and slippage sanity checks; ₹2,000 paper position cap, ₹4,000 liquidity reserve, approximate ₹50 per-trade risk sizing;
- Day-loss and uncertainty state propagation to a locked paper ledger.

**Limit:** The simulated stop assumes a price fill (after slippage) from observed bars. Real stop execution can be delayed, partial or entirely unavailable, and loss may exceed any nominal limit.

## Official reference-rate audit (as viewed 2026-11-04)

This is a hypothetical **2026 NSE/Zerodha-like rate scenario applied to February 2021 stock candles**, not a reconstruction of the actual charges payable in 2021. No broker is connected or chosen.

| Charge | Scenario calculation | Independent public reference |
|---|---|---|
| Equity intraday brokerage | min(0.03% turnover, ₹20) **per executed order**, buy and sell | [Zerodha current charges](https://zerodha.com/charges/) |
| Equity intraday STT | 0.025% **sell-side turnover**, nearest rupee | [Zerodha STT rate and rounding](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated) |
| NSE cash-market transaction charge | 0.00307% on aggregate buy and sell turnover | [Zerodha charges](https://zerodha.com/charges/) |
| SEBI turnover fee | ₹10 per ₹1 crore (0.0001%) on turnover | [Zerodha charges](https://zerodha.com/charges/) |
| GST | 18% on brokerage + exchange charge + SEBI fee | [Zerodha charges](https://zerodha.com/charges/) |
| Intraday stamp duty | 0.003% of buy turnover | [Zerodha charges](https://zerodha.com/charges/) |

**Important limitations and unresolved calculator reconciliation:**
- Broker support material presents a weighted-average-price example for intraday STT; this simple single-buy/single-sell model approximates it as sell-side turnover. The net amount may differ near the nearest-rupee boundary, and precise contract-note aggregation must be independently reconciled.
- The historical 2021 exchange charge schedule is not asserted. Later changes have occurred; do not backdate 2026 rates.
- Potential additional transaction-specific exchange investor-protection fund fees, auto-square-off fees, rare exchange special levies, income tax on intraday gains, account fees, and data subscriptions are not fully modeled.
- Ordinary cash equity delivery charges (DP), margin finance and derivatives are not part of this intraday, non-leveraged cash-stock research model.
- Market fill prices remain modeled, not exchange-confirmed; overnight holding is prohibited in the policy but **data outages can make this unknowable**, so no forced fictitious close.

## Data provenance / compliance boundary

The original 24 February 2021 ACC/RELIANCE stock-day files are public third-party material from [gsidhu/nse-intraday-data](https://github.com/gsidhu/nse-intraday-data), cryptographically pinned at [source manifest](SOURCE_BLOBS_FEB2021.tsv). A public repo and its stated software license **do not establish** exchange-market-data reuse or redistribution rights. The raw candles have not been included in this public project; the reproducibility workflow downloads temporary files and checks their source blob SHA-1.

NSE's [Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy) restricts market-data use/redistribution according to license agreements. New multi-year and prospective datasets require an independently verified permitted path. Refer to [NSE authorized real-time and minute snapshot product information](https://www.nse.in/static/market-data/real-time-data-subscription) for a compliant data-acquisition approach.

Any future API-based retail algorithm requires a separate regulatory feasibility review; NSE's [2026 retail algo procedure](https://www.nseindia.com/static/trade/platform-services-non-neat-decision-support-tools-algorithm-trading) is not bypassed by running software on a Raspberry Pi or labeling it an AI agent.

## Evidence gate

**Already verified before this PR:** Old replay's exact 24 input file blob fingerprints and 8 old net P&L outputs reproduced in [GitHub Actions run #41695270798](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41695270798). This was a development-sample deterministic check, **not proof of edge**.

**Verified in actual GitHub Actions job logs:**
- [Offline Paper Tests run #41698482817](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41698482817): **27/27 tests passed** — 8 legacy synthetic tests and **19 new fail-closed chronology/fee tests**, 0 failures.
- [Pinned Historical Replay run #41698482717](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41698482717): **24/24 pinned stock-day Git blobs** verified, the 8 original net-profit snapshots passed, and the guarded CLI independently processed both stocks at **5 and 15 basis points per side**.
- The guarded engine **matched all eight legacy simulated net results exactly** on the complete February 2021 source sessions. Every such guarded stock-session was either `CLOSED` or `NO_TRADE` (no unresolved live-source gaps in this small clean sample).

| Stock | Strategy | 5 bps/side guarded net P&L | 15 bps/side guarded net P&L |
|---|---|---:|---:|
| ACC | Plain breakout | −₹3.613323 | −₹22.987469 |
| ACC | Breakout + DTT veto | −₹22.784561 | −₹31.688167 |
| RELIANCE | Plain breakout | +₹17.168397 | −₹27.294151 |
| RELIANCE | Breakout + DTT veto | −₹34.806530 | −₹60.705623 |

The guarded CLI output SHA-256 fingerprints in the workflow log were:
- 5 bps/side: `cee5b60150f1769b41acfaa3d532409c2085bca8802a3baae5375450c2e2c57d`
- 15 bps/side: `4ebd9f280b1ea622b4aceb9df6854d158181317bef14e239c170a2a7209d0847`

**Interpretation:** Successful deterministic simulation replication and synthetic fail-closed checks, **not** evidence of historical price accuracy, real executed stops, low-risk profitability or a live deployable strategy.

**Release gate:** No real trades, no live broker connections, no trading credentials, no agent-managed order execution. A successful build or historical replay does not certify profitable performance, robustness, or deployability.

## Next falsification milestones

1. Preserve a verified Actions run for the new module and verify any output differences from the first simulation.
2. Test brokerage accounting and stop/market fills against independent invoice/contract-note examples **without uploading private account data**.
3. Add additional failure states: partially filled simulated entry, order rejection and stale price during a pending exit; these must be **unknown or canceled**, never optimistic fills.
4. Obtain licensed point-in-time stock data across multiple distinct market regimes; preregister before opening a new holdout.
5. Compare net-of-cost, risk-constrained baselines with doing nothing, not a cherry-picked high win rate.
