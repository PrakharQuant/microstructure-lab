"""Tests for the Glosten-Milgrom simulator."""
import pytest

from src.models.glosten_milgrom import quote_model


def test_symmetric_case_matches_textbook():
    # Classic example: V=120/80, prior=0.5, mu=0.4 → ask=108, bid=92
    result = quote_model(good_value=120, bad_value=80, prior_good=0.5, informed_prob=0.4)
    assert abs(result["midpoint"] - 100) < 1e-6
    assert abs(result["ask"] - 108) < 0.01
    assert abs(result["bid"] - 92) < 0.01
    assert abs(result["spread"] - 16) < 0.01
    assert abs(result["p_good_buy"] - 0.7) < 1e-6
    assert abs(result["p_good_sell"] - 0.3) < 1e-6


def test_no_information_zero_spread():
    result = quote_model(good_value=120, bad_value=80, prior_good=0.5, informed_prob=0.0)
    assert abs(result["spread"]) < 1e-6
    assert abs(result["ask"] - result["bid"]) < 1e-6
    assert abs(result["ask"] - 100) < 1e-6


def test_invalid_prior_raises():
    with pytest.raises(ValueError):
        quote_model(120, 80, prior_good=1.5, informed_prob=0.4)
    with pytest.raises(ValueError):
        quote_model(120, 80, prior_good=0.0, informed_prob=0.4)


def test_good_must_exceed_bad():
    with pytest.raises(ValueError):
        quote_model(good_value=80, bad_value=120, prior_good=0.5, informed_prob=0.4)
