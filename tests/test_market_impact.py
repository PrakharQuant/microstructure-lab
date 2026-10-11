"""Tests for the synthetic market-impact simulator."""
import pandas as pd

from src.models.market_impact import simulate_sweep


def test_full_fill_within_book():
    result = simulate_sweep(
        base_price=100.0, tick=0.1, depth_per_level=100, quantity=250, n_levels=5
    )
    assert result["filled"] == 250
    assert result["unfilled"] == 0
    assert result["average_price"] > 100.0
    # First 100 at 100.0, next 100 at 100.1, last 50 at 100.2
    expected_avg = (100 * 100.0 + 100 * 100.1 + 50 * 100.2) / 250
    assert abs(result["average_price"] - expected_avg) < 1e-6


def test_partial_fill_when_quantity_exceeds_depth():
    result = simulate_sweep(
        base_price=100.0, tick=0.5, depth_per_level=50, quantity=1000, n_levels=3
    )
    assert result["filled"] == 150  # 3 levels * 50
    assert result["unfilled"] == 850
    assert result["average_price"] > 100.0


def test_zero_impact_when_quantity_fits_first_level():
    result = simulate_sweep(
        base_price=50.0, tick=0.25, depth_per_level=200, quantity=100, n_levels=4
    )
    assert result["filled"] == 100
    assert abs(result["average_price"] - 50.0) < 1e-6
    assert abs(result["impact_pct"]) < 1e-9


def test_returns_dataframes():
    result = simulate_sweep(100.0, 0.1, 10, 25, 5)
    assert isinstance(result["fills"], pd.DataFrame)
    assert isinstance(result["book"], pd.DataFrame)
    assert len(result["book"]) == 5
