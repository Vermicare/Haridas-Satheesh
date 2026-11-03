# QHAP-TRADER offline research prototype

This folder contains the **first executable**, isolated **single-instrument/single-session historical replay**. It is **not** an autonomous trading daemon, a market-data collector, a broker integration or evidence of profitable trading.

## Contents

- [paper_mvp.py](paper_mvp.py) — Python standard-library-only CSV reader, opening-range teaching rule, next-bar paper entries, position/risk limits, simulated exits, data-gap halt and JSON audit journal.
- [test_paper_mvp.py](test_paper_mvp.py) — five synthetic-data checks for the replay boundary.
- [dtt_prototype.py](dtt_prototype.py) — deterministic hypothetical policy-switching scanner (no market data, orders or profitability claim).
- [test_dtt_prototype.py](test_dtt_prototype.py) — seven synthetic invariant tests for the DTT calculation.


## Run

Requires Python 3.11+ on a machine with timezone support.

```bash
cd projects/qhap-trader/prototype
python -m unittest -v
python paper_mvp.py path/to/authorized_one_day_minute_bars.csv --report paper_report.json
```

Input CSV column names:

```text
timestamp,symbol,open,high,low,close,volume
```

`timestamp` must include an explicit `+05:30` time offset (for example `2026-11-02T09:15:00+05:30`). Prices, volume and market sessions are **not** downloaded by this program. Use legally obtained 1-minute data with all opening bars from 09:15 to 09:24 and a 15:00 bar. A failing or incomplete day returns process exit code 2 and is never certified complete.

### Safety and scope

- No network calls and no live broker SDK, order route, secrets or credentials.
- **Simulated** ₹10,000 account, max ₹2,000 long position, ≥₹4,000 nominal reserve, max illustrative ₹50 stop risk, daily ₹100 model-loss lock. It is not a complete weekly risk/reconciliation system.
- The opening-range breakout is **unvalidated**. It is only an engineering specimen to test causal signal/fill ordering.
- The 5 and 10 basis-point input assumptions are placeholders, **not an audited Indian fee/tax schedule or verified fill/slippage model**.
- A close-bar stop on a 1-minute bar is a deliberately coarse assumption and may not represent real fills, liquidity or gap risk.
- Missing bars, stale feeds, intrabar fill ordering, circuit halts, market-wide session exceptions and calendar changes need substantially more work.
- No morning agent orchestration, psychology inference, external data adapter, daemon supervisor, cloud deployment, notification service, or multi-day equity ledger is implemented yet.
- Do not use output P&L as investment or performance evidence.

## What comes next?

Build authorized time-correct intraday data ingestion, audited India-specific cost model, deterministic simulated exchange fill states, security/calendar state, replay performance metrics and independent watchdog. Once the core is demonstrably correct, experiment with pre-market expectation-versus-reality and psychological crowd-behavior proxies, then optional LLM research agents.

Read [the agent/autonomy blueprint](../AGENT_AUTONOMY_BLUEPRINT.md) for the full architecture and fail-closed progression.
