"""Tests for the Roll (1984) estimator."""
import numpy as np
import pandas as pd
import pytest

from src.analytics.liquidity import roll_estimate


def test_roll_positive_covariance_not_estimable():
    # Perfectly positively autocorrelated returns
    r = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10])
    result = roll_estimate(r)
    assert result["status"] == "positive_covariance"
    assert np.isnan(result["spread"])


def test_roll_negative_covariance_estimable():
    # Alternating returns that produce negative autocovariance
    r = pd.Series([0.01, -0.01, 0.01, -0.01, 0.01, -0.01, 0.01, -0.01, 0.01, -0.01])
    result = roll_estimate(r)
    assert result["status"] == "ok"
    assert result["spread"] > 0
    # For this series the lag-1 covariance is negative
    assert result["covariance"] < 0


def test_roll_insufficient_data():
    r = pd.Series([0.01, 0.02])
    result = roll_estimate(r)
    assert result["status"] == "insufficient_data"
    assert np.isnan(result["spread"])


def test_roll_formula_consistency():
    # Manually construct returns with known negative autocovariance
    # Expected: cov ≈ -0.0001 → spread ≈ 0.02
    rng = np.random.default_rng(42)
    # Create a series with strong negative serial correlation via bounce
    signs = np.array([1, -1] * 50)
    noise = rng.normal(0, 0.001, size=100)
    r = pd.Series(0.005 * signs + noise)
    result = roll_estimate(r)
    assert result["status"] == "ok"
    assert 0 < result["spread"] < 0.1
