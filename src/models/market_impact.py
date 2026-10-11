"""Synthetic order-book market impact simulator."""
from typing import Dict, List

import pandas as pd


def simulate_sweep(
    base_price: float,
    tick: float,
    depth_per_level: int,
    quantity: int,
    n_levels: int,
) -> Dict:
    """Simulate walking the ask side of a synthetic order book.

    Returns average execution price, impact, and fill details.
    """
    if base_price <= 0 or tick <= 0 or depth_per_level <= 0 or n_levels < 1:
        raise ValueError("Invalid parameters for order-book simulation.")

    # Build synthetic ask book
    book = []
    for i in range(n_levels):
        price = round(base_price + i * tick, 6)
        book.append({"price": price, "available_shares": depth_per_level})

    remaining = quantity
    fills: List[dict] = []
    total_cost = 0.0
    filled = 0

    for level in book:
        if remaining <= 0:
            break
        take = min(remaining, level["available_shares"])
        cost = take * level["price"]
        total_cost += cost
        filled += take
        remaining -= take
        fills.append(
            {
                "price": level["price"],
                "shares": take,
                "cost": cost,
            }
        )

    unfilled = remaining
    average_price = total_cost / filled if filled > 0 else None
    impact_pct = (
        (average_price - base_price) / base_price if average_price is not None else None
    )

    return {
        "average_price": average_price,
        "impact_pct": impact_pct,
        "filled": filled,
        "unfilled": unfilled,
        "fills": pd.DataFrame(fills) if fills else pd.DataFrame(),
        "book": pd.DataFrame(book),
    }
