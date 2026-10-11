"""Return calculations and summary statistics."""
from typing import Dict

import numpy as np
import pandas as pd


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple and log returns based on Close price."""
    out = df.copy()
    out["Return"] = out["Close"].pct_change()
    out["LogReturn"] = np.log(out["Close"]).diff()
    return out


def summary_statistics(df: pd.DataFrame, periods_per_year: int = 252) -> Dict:
    """Compute basic return summary statistics.

    For weekly data the annualization is approximate.
    """
    returns = df["Return"].dropna()
    if returns.empty:
        return {
            "n": 0,
            "mean_return": np.nan,
            "std_return": np.nan,
            "annualized_volatility": np.nan,
            "min_return": np.nan,
            "max_return": np.nan,
        }

    mean_r = returns.mean()
    std_r = returns.std(ddof=1)
    ann_vol = std_r * np.sqrt(periods_per_year)

    return {
        "n": int(len(returns)),
        "mean_return": float(mean_r),
        "std_return": float(std_r),
        "annualized_volatility": float(ann_vol),
        "min_return": float(returns.min()),
        "max_return": float(returns.max()),
    }
