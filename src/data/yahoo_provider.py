"""Yahoo Finance data provider via yfinance."""
import re
from typing import Optional

import pandas as pd
import yfinance as yf


def validate_ticker(ticker: str) -> str:
    """Basic validation and normalization of Yahoo Finance ticker."""
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string.")
    ticker = ticker.strip().upper()
    # Allow alphanumeric, dots, hyphens, and carets (for indices like ^NSEI)
    if not re.match(r"^[A-Z0-9\^\.\-]+$", ticker):
        raise ValueError(f"Invalid ticker format: {ticker}")
    if len(ticker) > 20:
        raise ValueError("Ticker too long.")
    return ticker


def download_history(
    ticker: str,
    period: str = "2y",
    interval: str = "1d",
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Download historical OHLCV data from Yahoo Finance.

    Returns a DataFrame with DatetimeIndex and columns Open, High, Low, Close, Volume.
    """
    ticker = validate_ticker(ticker)
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            progress=False,
            threads=False,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to download data for {ticker}: {e}") from e

    if data is None or data.empty:
        raise ValueError(f"No data returned for ticker {ticker} with period={period}, interval={interval}.")

    # Flatten multi-index columns if present (yfinance sometimes returns them)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Ensure required columns
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns in data: {missing}")

    data = data[required].copy()
    data = data.dropna(subset=["Close"])
    if data.empty:
        raise ValueError(f"No valid close prices for {ticker}.")

    # Ensure index is datetime and named
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    data.index.name = "Date"

    return data.sort_index()
