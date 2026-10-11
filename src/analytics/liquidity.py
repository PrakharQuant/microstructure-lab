import numpy as np
import pandas as pd

def roll_estimate(returns: pd.Series) -> dict:
    """Compute Roll's proportional spread proxy from lag-one return covariance.

    The formula is only mathematically available for negative covariance. This
    function does not claim daily-close returns identify the true transaction spread.
    """
    r = pd.Series(returns).replace([np.inf, -np.inf], np.nan).dropna()
    n = len(r)
    if n < 3:
        return {"covariance": np.nan, "spread": np.nan, "n": n, "status": "insufficient_data",
                "message": "At least three valid returns are required for a lag-one covariance estimate."}
    cov = float(np.cov(r.iloc[1:].to_numpy(), r.iloc[:-1].to_numpy(), ddof=1)[0, 1])
    if not np.isfinite(cov):
        return {"covariance": cov, "spread": np.nan, "n": n, "status": "invalid",
                "message": "Covariance could not be estimated reliably."}
    if cov >= 0:
        return {"covariance": cov, "spread": np.nan, "n": n, "status": "nonnegative_covariance",
                "message": "Lag-one covariance is non-negative; Roll's square-root estimator is not real-valued for this sample. This does not imply zero trading costs."}
    return {"covariance": cov, "spread": float(2 * np.sqrt(-cov)), "n": n, "status": "ok",
            "message": "A numerical estimate is available, but daily close-to-close returns are not transaction-to-transaction returns."}

def rolling_roll_estimate(returns: pd.Series, window: int = 60) -> pd.DataFrame:
    r = pd.Series(returns).dropna()
    rows = []
    if window < 3:
        return pd.DataFrame(columns=["roll_spread", "covariance"])
    for end in range(window, len(r) + 1):
        sample = r.iloc[end-window:end]
        result = roll_estimate(sample)
        rows.append({"Date": r.index[end-1], "roll_spread": result["spread"], "covariance": result["covariance"]})
    if not rows:
        return pd.DataFrame(columns=["roll_spread", "covariance"])
    return pd.DataFrame(rows).set_index("Date")
