import numpy as np
import pandas as pd

def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Return"] = out["Close"].pct_change(fill_method=None)
    out["LogReturn"] = np.log(out["Close"]).diff()
    out["RollingVol20"] = out["Return"].rolling(20, min_periods=10).std() * np.sqrt(252)
    return out

def summary_statistics(df: pd.DataFrame) -> dict:
    r = df["Return"].dropna()
    if r.empty:
        return {"mean_return": np.nan, "annualized_volatility": np.nan, "n_returns": 0}
    periods_per_year = 52 if len(df) and pd.infer_freq(df.index) and "W" in str(pd.infer_freq(df.index)) else 252
    return {
        "mean_return": float(r.mean()),
        "annualized_volatility": float(r.std(ddof=1) * np.sqrt(periods_per_year)) if len(r) > 1 else np.nan,
        "n_returns": int(len(r)),
    }
