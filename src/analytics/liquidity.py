"""Liquidity measures including Roll (1984) spread estimator."""
from typing import Dict, Optional

import numpy as np
import pandas as pd


def roll_estimate(returns: pd.Series) -> Dict:
    """Estimate the Roll (1984) proportional spread from return autocovariance.

    Returns a dict with covariance, spread (or NaN), status, and message.
    The estimator is only defined when lag-1 autocovariance is negative.
    """
    r = returns.dropna()
    n = len(r)
    if n < 10:
        return {
            "covariance": np.nan,
            "spread": np.nan,
            "n": n,
            "status": "insufficient_data",
            "message": "Need at least 10 return observations for a reliable estimate.",
        }

    # Lag-1 autocovariance (sample covariance of consecutive returns)
    cov = r.cov(r.shift(1))
    if pd.isna(cov):
        return {
            "covariance": np.nan,
            "spread": np.nan,
            "n": n,
            "status": "invalid",
            "message": "Could not compute autocovariance.",
        }

    if cov >= 0:
        return {
            "covariance": float(cov),
            "spread": np.nan,
            "n": n,
            "status": "positive_covariance",
            "message": (
                "Lag-1 autocovariance is non-negative. "
                "The basic Roll square-root formula is not applicable. "
                "This does not imply zero trading costs; other dynamics may dominate."
            ),
        }

    spread = 2 * np.sqrt(-cov)
    return {
        "covariance": float(cov),
        "spread": float(spread),
        "n": n,
        "status": "ok",
        "message": "Roll proportional spread proxy estimated successfully.",
    }


def rolling_roll_estimate(
    returns: pd.Series, window: int = 60
) -> pd.DataFrame:
    """Compute rolling Roll spread estimates."""
    r = returns.dropna()
    if len(r) < window:
        return pd.DataFrame()

    results = []
    for i in range(window, len(r) + 1):
        window_returns = r.iloc[i - window : i]
        est = roll_estimate(window_returns)
        results.append(
            {
                "date": window_returns.index[-1],
                "roll_spread": est["spread"],
                "covariance": est["covariance"],
                "status": est["status"],
            }
        )

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.set_index("date")
    return df
