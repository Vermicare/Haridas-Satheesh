"""Decision-Threshold Tomography: deterministic synthetic research prototype.

Not a trading signal, backtest, validated investor-behavior model or broker integration.
No I/O, no network, no real-money actions. Produces only hypothetical plan-flip mass.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Action = Literal[-1, 0, 1]
Rule = Literal["buy_above", "buy_below", "exit_below", "exit_above"]


@dataclass(frozen=True)
class Plan:
    name: str
    rule: Rule
    threshold: float
    min_relative_volume: float
    weight: float

    def __post_init__(self) -> None:
        if not self.name or self.threshold <= 0 or self.min_relative_volume <= 0 or self.weight < 0:
            raise ValueError("Invalid hypothetical plan")
        if self.rule not in {"buy_above", "buy_below", "exit_below", "exit_above"}:
            raise ValueError("Unsupported rule")


@dataclass(frozen=True)
class State:
    price: float
    relative_volume: float

    def __post_init__(self) -> None:
        if self.price <= 0 or self.relative_volume < 0:
            raise ValueError("Invalid state")


def action(plan: Plan, state: State) -> Action:
    if state.relative_volume < plan.min_relative_volume:
        return 0
    if plan.rule == "buy_above":
        return 1 if state.price >= plan.threshold else 0
    if plan.rule == "buy_below":
        return 1 if state.price <= plan.threshold else 0
    if plan.rule == "exit_below":
        return -1 if state.price <= plan.threshold else 0
    return -1 if state.price >= plan.threshold else 0


def scan(plans: list[Plan], state: State, price_shocks_bps: list[float]) -> list[dict]:
    """Find switching mass under explicitly hypothetical price perturbations.

    Does not estimate directional price alpha, real order sizes, or trader counts.
    Weights need not be probabilities; normalized here solely to describe the
    *constructed* plan population. No inference about actual market composition.
    """
    if not plans or not price_shocks_bps:
        raise ValueError("Plans and shocks are required")
    total = sum(p.weight for p in plans)
    if total <= 0:
        raise ValueError("Positive total plan weight required")
    baseline = [action(p, state) for p in plans]
    result = []
    for bps in price_shocks_bps:
        shocked = State(price=state.price * (1 + bps / 10000),
                        relative_volume=state.relative_volume)
        changed = 0.0
        signed = 0.0
        buys = 0.0
        exits = 0.0
        for p, before in zip(plans, baseline):
            after = action(p, shocked)
            w = p.weight / total
            if after != before:
                changed += w
                signed += w * (after - before)
                if after == 1: buys += w
                if after == -1: exits += w
        result.append({"shock_bps": bps, "switching_mass": round(changed, 8),
                       "signed_change": round(signed, 8),
                       "new_buy_activation_mass": round(buys, 8),
                       "new_exit_activation_mass": round(exits, 8),
                       "interpretation": "hypothetical switching only; no trade signal"})
    return result
