"""Piece 171: parse_usd must not return Infinity/NaN for a JSON float price."""
import json
from decimal import Decimal

import freshness_check as f


def test_infinite_float_is_none():
    for bad in (float("inf"), float("-inf"), float("nan"), Decimal("Infinity"), Decimal("NaN")):
        assert f.parse_usd(bad) is None, bad


def test_json_infinity_literal_is_none():
    assert f.parse_usd(json.loads('{"p": Infinity}')["p"]) is None


def test_good_unchanged():
    assert f.parse_usd(25) == Decimal("25")
    assert f.parse_usd(19.5) == Decimal("19.5")
    assert f.parse_usd("$1,200") == Decimal("1200")
    assert f.parse_usd(Decimal("30")) == Decimal("30")
