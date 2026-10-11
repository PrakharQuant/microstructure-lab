# Methodology and interpretation

## 1. Data

The app downloads OHLCV data through `yfinance`. The data are used for descriptive historical analysis and return construction. Yahoo Finance is not treated as a historical quote or order-book feed.

## 2. Return definitions

Simple close-to-close return:

\[
R_t = \frac{P_t}{P_{t-1}} - 1
\]

Log return:

\[
r_t = \log(P_t)-\log(P_{t-1})
\]

Annualized volatility is the sample standard deviation of returns multiplied by the square root of the assumed number of periods per year (252 for daily data; the dashboard uses daily-style annualization for the weekly selection as a rough simplification, so interpret weekly annualization cautiously).

## 3. Roll (1984)

The textbook transaction-price representation is:

\[
P_t=M_t+\frac{S}{2}Q_t
\]

with trade direction \(Q_t\in\{-1,+1\}\). Under simplified assumptions, lag-one price-change autocovariance is \(-S^2/4\). The proportional-return version is:

\[
\widehat{s}=2\sqrt{-\widehat{\operatorname{Cov}}(R_t,R_{t-1})}.
\]

In this app, returns are daily close-to-close returns. They are not transaction-to-transaction returns and can include overnight news, closing-auction effects, and other components. The resulting estimate is an exploratory proxy, not a direct effective spread.

## 4. Glosten–Milgrom

Let fundamental value be either \(V_G\) or \(V_B\). The prior probability of the good state is \(p\). A trader is informed with probability \(q\); informed traders buy in the good state and sell in the bad state. Uninformed traders buy and sell with equal probability.

Then:

\[
P(Buy\mid G)=q+(1-q)/2,\quad P(Buy\mid B)=(1-q)/2.
\]

Bayes' rule produces the posterior state probabilities after a buy or sell. The ask and bid are the corresponding conditional expectations. This is a simulation, not a fitted model for the selected security.

## 5. Market impact

The impact demonstration walks through a synthetic ask book with equal displayed depth at ascending prices. It isolates the mechanical cost of consuming multiple levels. It does not include dynamic replenishment, quote revisions, strategic behavior, or information effects and is not an estimate of real-world impact.

## 6. Research interpretation

A numerical estimate is not automatically an economically valid estimate. Report the data source, interval, observation count, sample window, assumptions, and diagnostic state alongside each result.
