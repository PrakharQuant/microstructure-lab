# Microstructure Lab

**An Interactive Laboratory for Market Liquidity, Bid–Ask Spreads, and Information-Based Trading**

Microstructure Lab is a research-grade educational Streamlit application connecting market microstructure theory to historical market data and transparent simulations.

## Features

- Historical OHLCV data from Yahoo Finance through `yfinance`.
- US and Indian equity/ETF ticker presets.
- Return distribution, annualized volatility, and historical price visualizations.
- Roll (1984) spread proxy based on lag-one return autocovariance, with explicit failure states and limitations.
- Glosten–Milgrom (1985) Bayesian conditional-expectation simulation.
- Synthetic order-book sweep to illustrate market impact and depth.
- Cross-asset comparison and return-correlation matrix.
- CSV downloads, methodology documentation, and mathematical tests.

## Important data distinction

Yahoo Finance OHLCV history is not a historical limit order book. The application does **not** claim to directly measure historical quoted spreads, trade-level effective spreads, order-book depth, or the probability of informed trading from daily OHLCV alone.

Roll's formula is derived under simplified transaction-price assumptions. Here it is applied to close-to-close returns as an **exploratory proxy**, with warnings. Glosten–Milgrom quotes and the order book in the simulation tabs are **model outputs**, not observed market quotes.

## Run locally

Python 3.11 or 3.12 is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest -q
```

The tests cover the Roll estimator's mathematical contract, Glosten–Milgrom conditional expectations, and synthetic order-book sweeping. They do not require a live Yahoo Finance connection.

## Deploy on Render

1. Create a GitHub repository named `microstructure-lab` (already done if you are reading this).
2. In Render, choose **New + → Blueprint** and connect the repository containing `render.yaml`.
3. Review the service settings and deploy.
4. Render uses `requirements.txt` and starts Streamlit on its assigned `$PORT`.

Alternatively, create a Render Web Service manually:
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

Free services may spin down after inactivity, so the first request after a quiet period may be slower. Consult Render's current plan details before deployment.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open https://share.streamlit.io/
3. Select the repository, branch, and `app.py` entrypoint.
4. Deploy. No API key is required by this app, although Yahoo Finance availability is not guaranteed.

## Suggested research extensions

- Integrate a licensed or appropriately permitted quote/trade data source for direct spread measurement.
- Add intraday trade data where licensing, availability, and sampling quality permit.
- Compare Roll estimates at multiple frequencies and investigate estimator failure rates.
- Add effective-spread and realized-spread calculations only when quote/trade timestamps are available.
- Add a more formal PIN estimation implementation with identification diagnostics and simulated-data validation.
- Export reproducible research reports with ticker, interval, sample size, date range, assumptions, and estimator status.

## References

- Roll, R. (1984). “A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market.” *The Journal of Finance*.
- Glosten, L. R., & Milgrom, P. R. (1985). “Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders.” *Journal of Financial Economics*.
- Campbell, J. Y. *A Course in Asset Pricing*, chapter on asymmetric information and liquidity.
- `yfinance` documentation: https://ranaroussi.github.io/yfinance/
- Streamlit documentation: https://docs.streamlit.io/
- Render documentation: https://render.com/docs

## Disclaimer

Educational and research use only. Not investment advice. Market data availability, accuracy, adjustment conventions, and provider terms may change. Verify any empirical conclusion independently.
