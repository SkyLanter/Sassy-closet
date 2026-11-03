"""Piece 169: a bad public ¥ value reads as missing (None), never crashes pickup."""
from decimal import Decimal

import pickup


def test_bad_public_cny_is_none():
    for bad in ("abc", "Infinity", "NaN", "sNaN", float("nan"), "¥", " "):
        assert pickup._decimal_or_none(bad) is None, bad


def test_good_public_cny_unchanged():
    assert pickup._decimal_or_none("88") == Decimal("88")
    assert pickup._decimal_or_none(88.5) == Decimal("88.5")
    assert pickup._decimal_or_none(None) is None
    assert pickup._decimal_or_none("") is None
