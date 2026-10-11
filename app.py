import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.data.yahoo_provider import download_history, validate_ticker
from src.analytics.returns import add_returns, summary_statistics
from src.analytics.liquidity import rolling_roll_estimate, roll_estimate
from src.models.glosten_milgrom import quote_model
from src.models.market_impact import simulate_sweep

st.set_page_config(page_title="Microstructure Lab", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1450px;}
[data-testid="stMetric"] {background: rgba(128,128,128,.08); padding: 14px; border-radius: 10px;}
.small-note {font-size: .88rem; opacity: .82;}
</style>
""", unsafe_allow_html=True)

# Header with credits (no custom theme toggle — Streamlit's built-in menu handles dark mode)
st.title("📈 Microstructure Lab")
st.markdown("""
**Explore why the price you pay differs from the price you receive — even when fundamental value hasn't changed.**

An interactive laboratory connecting market microstructure theory (Roll 1984, Glosten–Milgrom 1985) to real historical data and transparent simulations. Estimate liquidity proxies, simulate adverse selection, and diagnose where textbook models succeed or fail on actual markets.
""")

# Credit block with enough vertical space so it is never cut off
st.markdown("""
<div style="margin-top: 0.5rem; margin-bottom: 1rem; padding: 8px 0; font-size: 0.95rem;">
    <strong>Made by Prakhar Gupta</strong> · <a href="mailto:bestofprakhar@gmail.com">bestofprakhar@gmail.com</a><br>
    <a href="https://www.linkedin.com/in/prakhar-gupta-5b7250372/" target="_blank" title="LinkedIn" style="text-decoration: none; margin-right: 8px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#0A66C2" style="vertical-align: middle;">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
    </a>
    <a href="https://x.com/PrakharQuant" target="_blank" title="X / Twitter" style="text-decoration: none;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: middle;">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
    </a>
</div>
""", unsafe_allow_html=True)

st.warning("Research note: Yahoo Finance OHLCV data are not a historical order book. Roll estimates calculated from daily closes are exploratory proxies, not direct measurements of quoted or effective spreads. The Glosten–Milgrom and market-impact modules are explicitly labelled simulations.")

with st.sidebar:
    st.header("Market data")
    market = st.selectbox("Market preset", ["US equities / ETFs", "Indian equities / ETFs", "Enter ticker"])
    presets = {
        "US equities / ETFs": ["AAPL", "MSFT", "SPY", "QQQ", "IWM", "TLT"],
        "Indian equities / ETFs": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "NIFTYBEES.NS", "BANKBEES.NS"],
        "Enter ticker": []
    }
    ticker = st.selectbox("Ticker", presets[market]) if presets[market] else st.text_input("Yahoo Finance ticker", "AAPL")
    period = st.selectbox("History", ["6mo", "1y", "2y", "5y", "10y"], index=2)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    load = st.button("Load / refresh data", type="primary", use_container_width=True)
    st.divider()
    st.caption("Examples: AAPL, SPY, RELIANCE.NS, TCS.NS, NIFTYBEES.NS.")
    st.caption("Data provider: Yahoo Finance via yfinance. Availability and terms may change.")
    st.caption("Theme: use the ⋮ menu (top-right) → Settings → Theme.")

if "data" not in st.session_state:
    st.session_state.data = None
    st.session_state.loaded_ticker = None
if load or st.session_state.data is None or st.session_state.loaded_ticker != ticker:
    try:
        validate_ticker(ticker)
        with st.spinner(f"Downloading {ticker} history…"):
            data = download_history(ticker, period=period, interval=interval)
        st.session_state.data = data
        st.session_state.loaded_ticker = ticker
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        st.info("Check the ticker, internet connectivity, and Yahoo Finance availability.")
        st.stop()

raw = st.session_state.data
if raw is None or raw.empty:
    st.error("No market data returned. Try another ticker or period.")
    st.stop()
df = add_returns(raw)
stats = summary_statistics(df)

st.subheader(f"{ticker.upper()} · Historical market explorer")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Observations", f"{len(df):,}")
c2.metric("Latest close", f"{df['Close'].dropna().iloc[-1]:,.2f}")
c3.metric("Annualized volatility", f"{stats['annualized_volatility']:.2%}" if pd.notna(stats["annualized_volatility"]) else "N/A")
c4.metric("Mean daily return", f"{stats['mean_return']:.3%}" if pd.notna(stats["mean_return"]) else "N/A")

tab_market, tab_roll, tab_gm, tab_impact, tab_compare, tab_method = st.tabs([
    "Market Explorer", "Roll Spread", "Glosten–Milgrom", "Market Impact", "Cross-Asset Research", "Methodology"
])

with tab_market:
    left, right = st.columns([1.7, 1])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="OHLC"))
        fig.update_layout(title="Historical OHLC", xaxis_title="Date", yaxis_title="Price", height=450, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        vol = px.bar(df.reset_index(), x="Date" if "Date" in df.reset_index().columns else df.index, y="Volume", title="Trading volume")
        vol.update_layout(height=450, showlegend=False)
        st.plotly_chart(vol, use_container_width=True)
    st.markdown("#### Return distribution")
    hist = px.histogram(df.dropna(subset=["Return"]), x="Return", nbins=60, marginal="box", title="Close-to-close returns")
    hist.update_layout(height=350)
    st.plotly_chart(hist, use_container_width=True)
    st.dataframe(df.tail(15).sort_index(ascending=False), use_container_width=True)

with tab_roll:
    st.markdown("### Roll (1984): infer a spread proxy from negative return autocovariance")
    st.latex(r"\widehat{spr}=2\sqrt{-\widehat{\operatorname{Cov}}(R_t,R_{t-1})}")
    st.write("The textbook result comes from transaction prices alternating around a fixed midpoint. Daily close-to-close returns are only a proxy and can be affected by overnight news, auctions, and non-synchronous trading.")
    window = st.slider("Estimation window (observations)", min_value=20, max_value=max(20, min(500, len(df)-1)), value=min(60, max(20, len(df)-1)), step=10)
    r = df["Return"].dropna()
    estimate = roll_estimate(r.tail(window))
    a, b, c = st.columns(3)
    a.metric("Lag-1 return covariance", f"{estimate['covariance']:.6g}" if pd.notna(estimate["covariance"]) else "N/A")
    b.metric("Roll proportional spread", f"{estimate['spread']:.3%}" if pd.notna(estimate["spread"]) else "Not estimable")
    c.metric("Observations", str(estimate["n"]))
    if estimate["status"] != "ok":
        st.warning(estimate["message"])
    else:
        st.info("Mathematically estimable under the Roll formula. This is not a directly observed bid–ask spread and should be interpreted cautiously with daily data.")
    rolling = rolling_roll_estimate(r, window=min(window, max(10, len(r)//2)))
    if not rolling.empty:
        fig = px.line(rolling, x=rolling.index, y="roll_spread", title="Rolling Roll spread proxy")
        fig.update_yaxes(tickformat=".2%")
        fig.update_layout(height=360, yaxis_title="Proportional spread proxy", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Assumptions and diagnostics")
    st.markdown("- The basic model assumes transaction prices execute at the bid or ask around an efficient midpoint.\n- Trade direction is assumed to be independent and balanced in the textbook derivation.\n- The estimator requires negative first-order autocovariance; a positive estimate does not imply zero transaction costs.\n- Returns here are close-to-close, not transaction-to-transaction returns.")
    st.download_button("Download return series (CSV)", df.to_csv().encode("utf-8"), file_name=f"{ticker.replace('.','_')}_returns.csv", mime="text/csv")

with tab_gm:
    st.markdown("### Glosten–Milgrom (1985): order flow as information")
    st.write("Illustrative model, not live quotes. Informed traders buy in the good state and sell in the bad state; uninformed traders choose either side with equal probability. Market makers are risk-neutral.")
    col1, col2 = st.columns(2)
    with col1:
        good_value = st.slider("Fundamental value in good state", 105, 200, 120, 5)
        bad_value = st.slider("Fundamental value in bad state", 10, 100, 80, 5)
        prior_good = st.slider("Prior probability of good state", 0.05, 0.95, 0.50, 0.05)
    with col2:
        informed_prob = st.slider("Probability arriving trader is informed", 0.0, 0.9, 0.4, 0.05)
        st.caption("Assumptions: one unit per order, equal prior probability of an uninformed buy or sell, and informed traders trade in the direction of their information.")
    if good_value <= bad_value:
        st.error("Good-state value must exceed bad-state value.")
    else:
        gm = quote_model(good_value, bad_value, prior_good, informed_prob)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Prior midpoint", f"{gm['midpoint']:.2f}")
        m2.metric("Conditional bid", f"{gm['bid']:.2f}")
        m3.metric("Conditional ask", f"{gm['ask']:.2f}")
        m4.metric("Model spread", f"{gm['spread']:.2f}")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Sell order", "Before order", "Buy order"], y=[gm["bid"], gm["midpoint"], gm["ask"]], text=[f"{gm['bid']:.2f}", f"{gm['midpoint']:.2f}", f"{gm['ask']:.2f}"], textposition="outside"))
        fig.update_layout(title="Conditional expected values", yaxis_title="Value", height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Posterior probability of good state after a buy: **{gm['p_good_buy']:.1%}**")
        st.write(f"Posterior probability of good state after a sell: **{gm['p_good_sell']:.1%}**")
        st.latex(r"Ask=E[V\mid I,\text{ buy}],\qquad Bid=E[V\mid I,\text{ sell}]")
        st.caption("The spread reflects the difference between conditional expectations. In this simple setup it is an information-based model spread, not an empirical estimate from the selected ticker.")

with tab_impact:
    st.markdown("### Market impact: walk through a simulated order book")
    st.caption("Synthetic order-book levels. These are not actual historical quotes for the selected ticker.")
    base = st.number_input("Best ask price", min_value=1.0, value=float(round(float(df["Close"].iloc[-1]), 2)), step=1.0)
    tick = st.number_input("Price step between levels", min_value=0.01, value=max(0.05, round(base * 0.001, 2)), step=0.05, format="%.2f")
    depth = st.number_input("Shares available at each level", min_value=1, max_value=1000000, value=100, step=25)
    quantity = st.number_input("Buy order quantity", min_value=1, max_value=10000000, value=250, step=25)
    levels = st.slider("Number of ask levels", 2, 20, 8)
    sweep = simulate_sweep(base, tick, depth, quantity, levels)
    if sweep["unfilled"] > 0:
        st.warning(f"Only {sweep['filled']:,} shares could be filled in the simulated book; {sweep['unfilled']:,} remain unfilled.")
    x1, x2, x3 = st.columns(3)
    x1.metric("Average execution price", f"{sweep['average_price']:,.2f}" if sweep["filled"] else "N/A")
    x2.metric("Best ask", f"{base:,.2f}")
    x3.metric("Price impact vs best ask", f"{sweep['impact_pct']:.3%}" if sweep["filled"] else "N/A")
    st.dataframe(sweep["fills"], use_container_width=True)
    fig = px.bar(sweep["book"], x="price", y="available_shares", title="Synthetic ask-side depth")
    fig.update_layout(xaxis_title="Ask price", yaxis_title="Available shares")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("The average execution price rises when a buy order consumes liquidity at increasingly expensive levels. Real market impact can also include quote revisions, replenishment, and information effects.")

with tab_compare:
    st.markdown("### Cross-asset liquidity research")
    st.write("Compare return-based statistics across a small basket. All tickers are user-selectable and all results depend on available historical data.")
    default = ["SPY", "AAPL", "MSFT", "RELIANCE.NS", "TCS.NS"]
    basket_text = st.text_input("Comma-separated Yahoo tickers", ", ".join(default))
    if st.button("Run cross-asset comparison"):
        tickers = list(dict.fromkeys([validate_ticker(x.strip()) for x in basket_text.split(",") if x.strip()]))
        rows, series = [], []
        with st.spinner("Downloading comparison data…"):
            for t in tickers[:12]:
                try:
                    d = add_returns(download_history(t, period=period, interval=interval))
                    s = summary_statistics(d)
                    rr = roll_estimate(d["Return"].dropna())
                    rows.append({"Ticker": t, "Observations": len(d), "Annualized volatility": s["annualized_volatility"], "Mean return": s["mean_return"], "Lag-1 covariance": rr["covariance"], "Roll proxy": rr["spread"], "Roll status": rr["status"]})
                    series.append(d["Return"].rename(t))
                except Exception as exc:
                    st.warning(f"{t}: {exc}")
        if rows:
            result = pd.DataFrame(rows).set_index("Ticker")
            st.dataframe(result.style.format({"Annualized volatility":"{:.2%}", "Mean return":"{:.3%}", "Lag-1 covariance":"{:.6g}", "Roll proxy":"{:.3%}"}), use_container_width=True)
            if series:
                aligned = pd.concat(series, axis=1)
                corr = aligned.corr()
                fig = px.imshow(corr, text_auto=".2f", aspect="auto", title="Return correlation matrix")
                st.plotly_chart(fig, use_container_width=True)
            st.download_button("Download comparison CSV", result.to_csv().encode("utf-8"), file_name="cross_asset_research.csv", mime="text/csv")

with tab_method:
    st.markdown("### Methodology, assumptions, and limitations")
    st.markdown("""
**Data**
- Historical OHLCV data are fetched through `yfinance` from Yahoo Finance.
- Indian tickers commonly use `.NS` for NSE-listed instruments and `.BO` for BSE-listed instruments; availability varies.
- Prices and volumes can be missing, revised, adjusted, or unavailable for some symbols and dates.

**Roll estimator**
- The textbook result is based on transaction-to-transaction price changes and a simplified bid–ask process.
- This app uses close-to-close returns as an exploratory proxy; it does not observe the historical bid, ask, trade direction, or midpoint.
- A non-negative lag-one covariance makes the simple square-root estimator unavailable as written.
- A valid numerical output is not proof that the estimate equals the true effective spread.

**Glosten–Milgrom**
- The good/bad fundamental values, prior, and informed-trader probability are hypothetical user inputs.
- Quotes are conditional expectations under the stated assumptions, not live market quotes.

**Market impact**
- The order book is synthetic. It demonstrates order-book walking, not realized market impact in the selected security.

**Reproducibility**
- Ticker, date range, interval, estimation window, sample size, and failure states should be reported with any research output.
- Yahoo Finance access is subject to its availability and terms; do not use this application as a trading system or investment advice.
""")
    st.markdown("### Core equations")
    st.latex(r"M_t=\frac{Ask_t+Bid_t}{2},\qquad S_t=Ask_t-Bid_t")
    st.latex(r"\widehat{spr}=2\sqrt{-\widehat{\operatorname{Cov}}(R_t,R_{t-1})}")
    st.latex(r"Mid=E[V\mid I],\quad Ask=E[V\mid I,\text{ buy}],\quad Bid=E[V\mid I,\text{ sell}]")
    st.markdown("### References")
    st.markdown("- Roll, R. (1984). A simple implicit measure of the effective bid–ask spread in an efficient market. *The Journal of Finance*.\n- Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*.\n- Campbell, J. Y. *A Course in Asset Pricing*, market microstructure chapter.")

st.divider()
st.caption("Microstructure Lab · Educational research prototype by Prakhar Gupta · Not investment advice")
