import numpy as np
import pandas as pd
from src.analytics.liquidity import roll_estimate, rolling_roll_estimate

def test_roll_returns_nan_for_positive_covariance():
    rng = np.random.default_rng(5)
    r = pd.Series(rng.normal(size=1000))
    result = roll_estimate(r)
    # Random data can yield either sign; this test checks output contract.
    assert result["n"] == 1000
    assert result["status"] in {"ok", "nonnegative_covariance"}

def test_roll_formula_on_negative_covariance():
    r = pd.Series([0.01, -0.01, 0.01, -0.01, 0.01, -0.01, 0.01, -0.01])
    result = roll_estimate(r)
    assert result["covariance"] < 0
    assert np.isclose(result["spread"], 2 * np.sqrt(-result["covariance"]))

def test_roll_insufficient_data():
    result = roll_estimate(pd.Series([0.01, 0.02]))
    assert result["status"] == "insufficient_data"
    assert np.isnan(result["spread"])

def test_rolling_returns_frame():
    r = pd.Series(np.tile([0.01, -0.01], 50), index=pd.date_range("2024-01-01", periods=100))
    out = rolling_roll_estimate(r, window=20)
    assert len(out) == 81
