def quote_model(good_value: float, bad_value: float, prior_good: float, informed_probability: float) -> dict:
    """Basic Glosten–Milgrom conditional-expectation model.

    Informed traders buy in the good state and sell in the bad state.
    Uninformed traders buy/sell with probability 0.5. A trader is informed
    with probability informed_probability.
    """
    if good_value <= bad_value:
        raise ValueError("good_value must exceed bad_value")
    if not 0 <= prior_good <= 1:
        raise ValueError("prior_good must be in [0, 1]")
    if not 0 <= informed_probability <= 1:
        raise ValueError("informed_probability must be in [0, 1]")
    p = prior_good
    q = informed_probability
    # Probability of a buy conditional on good/bad state.
    p_buy_good = q + (1 - q) * 0.5
    p_buy_bad = (1 - q) * 0.5
    p_buy = p * p_buy_good + (1 - p) * p_buy_bad
    p_sell = 1 - p_buy
    p_good_buy = (p * p_buy_good / p_buy) if p_buy > 0 else p
    p_good_sell = (p * (1 - p_buy_good) / p_sell) if p_sell > 0 else p
    midpoint = p * good_value + (1 - p) * bad_value
    ask = p_good_buy * good_value + (1 - p_good_buy) * bad_value
    bid = p_good_sell * good_value + (1 - p_good_sell) * bad_value
    return {
        "midpoint": midpoint, "ask": ask, "bid": bid, "spread": ask - bid,
        "p_good_buy": p_good_buy, "p_good_sell": p_good_sell,
        "p_buy": p_buy, "p_sell": p_sell
    }
