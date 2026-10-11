import pytest
from src.models.market_impact import simulate_sweep

def test_sweep_uses_more_expensive_levels():
    out = simulate_sweep(best_ask=100, tick_size=1, depth_per_level=100, quantity=250, levels=5)
    assert out["filled"] == 250
    assert out["unfilled"] == 0
    assert out["average_price"] == pytest.approx((100*100 + 100*101 + 50*102) / 250)
    assert out["impact_pct"] > 0

def test_unfilled_quantity_reported():
    out = simulate_sweep(100, 1, 10, 25, 2)
    assert out["filled"] == 20
    assert out["unfilled"] == 5
