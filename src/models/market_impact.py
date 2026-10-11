import pandas as pd

def simulate_sweep(best_ask: float, tick_size: float, depth_per_level: int, quantity: int, levels: int = 8) -> dict:
    """Walk a synthetic ask book; not a historical market-impact estimator."""
    if best_ask <= 0 or tick_size <= 0:
        raise ValueError("best_ask and tick_size must be positive")
    if depth_per_level < 1 or quantity < 1 or levels < 1:
        raise ValueError("depth_per_level, quantity, and levels must be positive")
    book = pd.DataFrame({
        "level": range(1, levels + 1),
        "price": [best_ask + i * tick_size for i in range(levels)],
        "available_shares": [int(depth_per_level)] * levels
    })
    remaining = int(quantity)
    fills = []
    total_cost = 0.0
    filled = 0
    for row in book.itertuples(index=False):
        take = min(remaining, int(row.available_shares))
        if take:
            fills.append({"level": row.level, "price": row.price, "shares_filled": take, "notional": take * row.price})
            total_cost += take * row.price
            filled += take
            remaining -= take
        if remaining == 0:
            break
    average = total_cost / filled if filled else float("nan")
    return {
        "book": book,
        "fills": pd.DataFrame(fills, columns=["level", "price", "shares_filled", "notional"]),
        "filled": filled,
        "unfilled": remaining,
        "average_price": average,
        "impact_pct": (average / best_ask - 1) if filled else float("nan")
    }
