"""Piece 166: non-finite sell $ text must read as unusable (None), never crash."""
import pickup


def test_nonfinite_sell_is_none():
    for bad in ("Infinity", "-inf", "NaN", "sNaN", "$Infinity"):
        assert pickup._whole_dollars(bad) is None, bad


def test_good_values_unchanged():
    assert pickup._whole_dollars("$25") == 25
    assert pickup._whole_dollars("1,200") == 1200
    assert pickup._whole_dollars("25.5") is None
    assert pickup._whole_dollars("") is None
