"""Piece 167: a NaN or Infinity price must not pass into the daily export."""
import export_daily_inputs as e


def test_nonfinite_price_is_none():
    for bad in ("nan", "NaN", float("nan"), "inf", "-inf", float("inf")):
        assert e._price(bad) is None, bad


def test_good_prices_unchanged():
    assert e._price("25") == 25
    assert e._price(19.5) == 19.5
    assert e._price("0") is None
