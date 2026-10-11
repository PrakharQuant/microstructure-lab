"""Glosten-Milgrom (1985) adverse selection model simulator."""
from typing import Dict


def quote_model(
    good_value: float,
    bad_value: float,
    prior_good: float,
    informed_prob: float,
) -> Dict:
    """Compute conditional bid, ask, and spread under Glosten-Milgrom assumptions.

    Assumptions:
    - Informed traders buy in good state, sell in bad state.
    - Uninformed traders buy/sell with equal probability 0.5.
    - Risk-neutral competitive market maker.
    """
    if not (0 < prior_good < 1):
        raise ValueError("prior_good must be between 0 and 1 (exclusive).")
    if not (0 <= informed_prob <= 1):
        raise ValueError("informed_prob must be between 0 and 1.")
    if good_value <= bad_value:
        raise ValueError("good_value must exceed bad_value.")

    prior_bad = 1.0 - prior_good
    q = informed_prob

    # P(buy | good) and P(buy | bad)
    p_buy_good = q * 1.0 + (1 - q) * 0.5
    p_buy_bad = q * 0.0 + (1 - q) * 0.5

    # Unconditional P(buy)
    p_buy = p_buy_good * prior_good + p_buy_bad * prior_bad
    # Under symmetry this is usually 0.5, but compute generally

    # Posterior P(good | buy)
    p_good_buy = (p_buy_good * prior_good) / p_buy if p_buy > 0 else prior_good
    p_bad_buy = 1.0 - p_good_buy

    # Posterior P(good | sell)
    p_sell_good = 1.0 - p_buy_good
    p_sell_bad = 1.0 - p_buy_bad
    p_sell = 1.0 - p_buy
    p_good_sell = (p_sell_good * prior_good) / p_sell if p_sell > 0 else prior_good
    p_bad_sell = 1.0 - p_good_sell

    # Conditional expectations
    ask = p_good_buy * good_value + p_bad_buy * bad_value
    bid = p_good_sell * good_value + p_bad_sell * bad_value
    midpoint = prior_good * good_value + prior_bad * bad_value
    spread = ask - bid

    return {
        "midpoint": float(midpoint),
        "bid": float(bid),
        "ask": float(ask),
        "spread": float(spread),
        "p_good_buy": float(p_good_buy),
        "p_good_sell": float(p_good_sell),
        "p_buy": float(p_buy),
    }
