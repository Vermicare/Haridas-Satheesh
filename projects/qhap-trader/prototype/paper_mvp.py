"""QHAP-TRADER research-only, single-security intraday CSV replay.

No network, broker login, live order or future data dependency. A deliberately
simple *unvalidated* baseline to test engineering invariants, not profitability.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path

STARTING_CASH = 10_000.0
POSITION_CAP = 2_000.0
CASH_RESERVE = 4_000.0
RISK_PER_TRADE = 50.0
DAILY_LOSS_LOCK = 100.0
TOTAL_DRAWDOWN_LOCK = 800.0
SLIPPAGE_BPS_PER_SIDE = 5.0    # Placeholder, not a verified market fill
COST_BPS_PER_SIDE = 10.0       # Placeholder; NOT an accurate Indian tax/fee model


@dataclass(frozen=True)
class Bar:
    ts: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


def parse_bars(path: Path) -> list[Bar]:
    bars: list[Bar] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = datetime.fromisoformat(row["timestamp"])
            if ts.tzinfo is None or ts.utcoffset() != timedelta(hours=5, minutes=30):
                raise ValueError("Bar timestamps must have explicit +05:30 IST offset")
            b = Bar(ts, row["symbol"].strip(), *(float(row[k]) for k in
                ("open", "high", "low", "close", "volume")))
            if not (b.symbol and b.open > 0 and b.low > 0 and b.volume >= 0 and
                    b.low <= min(b.open, b.close) <= max(b.open, b.close) <= b.high):
                raise ValueError(f"Malformed OHLCV row at {ts}")
            bars.append(b)
    if not bars:
        raise ValueError("No bars")
    if any(b.symbol != bars[0].symbol or b.ts.date() != bars[0].ts.date() for b in bars):
        raise ValueError("Replay requires one symbol and one session per file")
    if any(b.ts <= p.ts for p, b in zip(bars, bars[1:])):
        raise ValueError("Bars must be strictly time-ordered without duplicates")
    if any(b.ts.weekday() >= 5 or not time(9, 15) <= b.ts.time() <= time(15, 30)
           for b in bars):
        raise ValueError("Unexpected session timestamp; check exchange calendar")
    return bars


def run_replay(bars: list[Bar]) -> dict:
    # Opening range uses completed 09:15-09:24 minute bars only.
    opening = [b for b in bars if time(9, 15) <= b.ts.time() < time(9, 25)]
    if len(opening) != 10 or any((b.ts - p.ts).total_seconds() != 60
                                    for p, b in zip(opening, opening[1:])):
        raise ValueError("Required complete 10-bar opening range unavailable")
    opening_high = max(b.high for b in opening)
    cash, qty, entry, stop, peak_equity = STARTING_CASH, 0, 0.0, 0.0, STARTING_CASH
    pending_entry = False
    locked = False
    exceptions: list[str] = []
    ledger: list[dict] = []
    prev = None
    history: list[Bar] = []
    flat_recorded = False

    def record(b: Bar, event: str, **fields: object) -> None:
        ledger.append({"time": b.ts.isoformat(), "event": event, **fields})

    def exit_at(b: Bar, raw_price: float, cause: str) -> None:
        nonlocal cash, qty, entry, stop
        sale = raw_price * (1 - SLIPPAGE_BPS_PER_SIDE / 10_000)
        fee = sale * qty * COST_BPS_PER_SIDE / 10_000
        cash += sale * qty - fee
        record(b, "PAPER_EXIT", reason=cause, qty=qty, price=round(sale, 4), fee=round(fee, 4))
        qty, entry, stop = 0, 0.0, 0.0

    for b in bars:
        tm = b.ts.time()
        # Data gaps are fatal to further entries. Do not pretend a missing exit was filled.
        if prev and (b.ts - prev.ts).total_seconds() > 60:
            locked = True
            pending_entry = False
            exceptions.append(f"Data gap after {prev.ts.isoformat()}")
            record(b, "HALT", reason="missing_minute_bars")
        prev = b
        if tm >= time(15, 0):
            pending_entry = False
            if qty:
                if tm == time(15, 0):
                    exit_at(b, b.open, "scheduled_flat_by_1500")
                else:
                    exceptions.append("No 15:00 bar; exit not verifiably completed on time")
                    record(b, "HALT", reason="missing_1500_exit")
                    exit_at(b, b.open, "late_simulated_exit_NOT_compliant")
            flat_recorded = True
            history.append(b)
            continue

        # A signal from the PREVIOUS completed bar can fill only at this bar's open.
        if pending_entry and not locked and qty == 0 and time(9, 25) <= tm <= time(14, 45):
            buy_price = b.open * (1 + SLIPPAGE_BPS_PER_SIDE / 10_000)
            # An illustrative 1% protective stop: not an executable guaranteed stop.
            unit_estimated_loss = buy_price * (0.01 + 2 * SLIPPAGE_BPS_PER_SIDE / 10_000 +
                                               2 * COST_BPS_PER_SIDE / 10_000)
            max_qty = min(int(POSITION_CAP / buy_price),
                          int((cash - CASH_RESERVE) / (buy_price * (1 + COST_BPS_PER_SIDE / 10_000))),
                          int(RISK_PER_TRADE / unit_estimated_loss))
            if max_qty > 0:
                fee = max_qty * buy_price * COST_BPS_PER_SIDE / 10_000
                cash -= max_qty * buy_price + fee
                qty, entry, stop = max_qty, buy_price, buy_price * 0.99
                record(b, "PAPER_ENTRY", qty=qty, price=round(entry, 4),
                       stop=round(stop, 4), fee=round(fee, 4))
        pending_entry = False

        # If both stop and target could be touched in the same bar, prefer the stop.
        if qty and b.low <= stop:
            exit_at(b, min(stop, b.open), "protective_stop_pessimistic")

        equity = cash + qty * b.close
        peak_equity = max(peak_equity, equity)
        if equity <= STARTING_CASH - DAILY_LOSS_LOCK or \
           equity <= peak_equity - TOTAL_DRAWDOWN_LOCK:
            locked = True
            pending_entry = False
            if qty:
                exit_at(b, b.close, "loss_lock_proxy_current_close")
            record(b, "HALT", reason="loss_limit_reached")

        if not locked and qty == 0 and time(9, 25) <= tm < time(14, 45):
            recent = history[-5:]
            # Test-only breakout baseline; closed-bar signal -> next-bar simulated fill.
            avg_volume = sum(x.volume for x in recent) / len(recent) if recent else 0
            if len(recent) == 5 and avg_volume > 0 and \
               b.close > opening_high and b.volume >= 1.5 * avg_volume:
                pending_entry = True
                record(b, "CANDIDATE", reason="unvalidated_opening_range_breakout")
        history.append(b)

    # Never declare a day successfully flat without an observed scheduled exit bar.
    if not any(b.ts.time() == time(15, 0) for b in bars):
        exceptions.append("15:00 bar missing; day cannot be certified complete")
    if not flat_recorded:
        exceptions.append("Session not observed through exit window")
    if qty:
        exceptions.append("Open paper position remains; replay invalid")
    final_equity = cash + qty * bars[-1].close
    return {
        "mode": "OFFLINE_PAPER_ONLY",
        "status": "INCOMPLETE_OR_FAILED" if exceptions else "SIMULATED_COMPLETE",
        "symbol": bars[0].symbol,
        "session": bars[0].ts.date().isoformat(),
        "simulated_starting_cash": STARTING_CASH,
        "simulated_final_equity": round(final_equity, 4),
        "simulated_pnl_NOT_PERFORMANCE_EVIDENCE": round(final_equity - STARTING_CASH, 4),
        "costs": "FIXED PLACEHOLDERS: excludes complete Indian statutory & broker fee schedule",
        "strategy": "UNVALIDATED teaching baseline; cannot estimate future profits",
        "exceptions": exceptions,
        "journal": ledger,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Single-day 1-minute OHLCV CSV; no data fetched")
    parser.add_argument("--report", type=Path, default=Path("paper_report.json"))
    args = parser.parse_args()
    result = run_replay(parse_bars(args.csv_path))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"{result['status']}: {args.report}; {len(result['journal'])} journal events")
    if result["exceptions"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
