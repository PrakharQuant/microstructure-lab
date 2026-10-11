import pytest
from src.models.glosten_milgrom import quote_model

def test_no_informed_trading_zero_spread():
    out = quote_model(120, 80, 0.5, 0.0)
    assert out["spread"] == pytest.approx(0.0)
    assert out["ask"] == pytest.approx(100)
    assert out["bid"] == pytest.approx(100)

def test_informed_trading_widens_spread():
    out = quote_model(120, 80, 0.5, 0.4)
    assert out["ask"] > out["midpoint"]
    assert out["bid"] < out["midpoint"]
    assert out["spread"] > 0

def test_bayesian_posteriors():
    out = quote_model(120, 80, 0.5, 0.4)
    assert out["p_good_buy"] == pytest.approx(0.7)
    assert out["p_good_sell"] == pytest.approx(0.3)

def test_invalid_values():
    with pytest.raises(ValueError):
        quote_model(80, 120, 0.5, 0.4)
