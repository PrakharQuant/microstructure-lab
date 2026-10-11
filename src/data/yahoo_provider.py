import re
import pandas as pd
import yfinance as yf

TICKER_PATTERN = re.compile(r"^[A-Za-z0-9.^=_-]{1,30}$")

def validate_ticker(ticker: str) -> str:
    ticker = ticker.strip()
    if not ticker or not TICKER_PATTERN.fullmatch(ticker):
        raise ValueError("Ticker contains unsupported characters or is empty.")
    return ticker

def download_history(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    ticker = validate_ticker(ticker)
    allowed_periods = {"6mo", "1y", "2y", "5y", "10y"}
    allowed_intervals = {"1d", "1wk"}
    if period not in allowed_periods:
        raise ValueError(f"Unsupported period: {period}")
    if interval not in allowed_intervals:
        raise ValueError(f"Unsupported interval: {interval}")
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False, actions=False)
    if df is None or df.empty:
        raise ValueError(f"No history returned for {ticker}. Check ticker availability.")
    df = df.rename_axis("Date")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Data provider omitted required columns: {missing}")
    df = df[required].copy()
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Close"]).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    if df.empty:
        raise ValueError(f"No valid closing prices for {ticker}.")
    return df
