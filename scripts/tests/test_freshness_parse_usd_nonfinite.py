"""Piece 171: parse_usd must not return Infinity/NaN for a JSON float price.

A junk dollar sign or a comma that is not a thousands group is not a price.
"""
import json
from decimal import Decimal

import freshness_check as f
from held_policy import norm_ma


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


def test_junk_dollar_and_comma_text_is_none():
    for bad in (
        "2$5",
        "2$$5",
        "2,5",
        "25,",
        "12,50",
        "0,25",
        "0,025",
        "$0,025",
        "0,025$",
        "00,025",
        "0,000,025",
        "0,250",
        "01,025",
        "2,$500",
        "1.200,50",
        "$$25",
        "$25$",
        "1,2000",
        "1234,567",
    ):
        assert f.parse_usd(bad) is None, bad


def test_single_dollar_mark_and_thousands_commas_stay():
    assert f.parse_usd("$25") == Decimal("25")
    assert f.parse_usd("25$") == Decimal("25")
    assert f.parse_usd("$ 25") == Decimal("25")
    assert f.parse_usd("25 $") == Decimal("25")
    assert f.parse_usd("$1,200.50") == Decimal("1200.50")
    assert f.parse_usd("1,200.50") == Decimal("1200.50")
    assert f.parse_usd("1,200") == Decimal("1200")
    assert f.parse_usd("19.5") == Decimal("19.5")
    assert f.parse_usd("25") == Decimal("25")
    assert f.parse_usd("25.00") == Decimal("25.00")
    assert f.parse_usd("1200") == Decimal("1200")
    assert f.parse_usd("08") == Decimal("8")
    assert f.parse_usd("$1,200,000") == Decimal("1200000")
    assert f.parse_usd("1,200.5") == Decimal("1200.5")


def test_sign_exponent_and_hex_text_is_none():
    for bad in ("+25", "1e2", "0x19"):
        assert f.parse_usd(bad) is None, bad


def test_bool_blank_and_nonfinite_text_stay_none():
    assert f.parse_usd(True) is None
    assert f.parse_usd(False) is None
    assert f.parse_usd(None) is None
    assert f.parse_usd("") is None
    assert f.parse_usd("   ") is None
    assert f.parse_usd("NaN") is None
    assert f.parse_usd("Infinity") is None


def test_blob_junk_price_is_none_and_plain_25_stays():
    junk = f.parse_blob_catalog({"products": [{"ma": "S06", "priceUsd": "2$5"}]})
    assert [(row.ma, row.price_usd) for row in junk] == [("S06", None)]
    priced = f.parse_blob_catalog({"products": [{"ma": "S06", "priceUsd": 25}]})
    assert [(row.ma, row.price_usd) for row in priced] == [("S06", Decimal("25"))]
    both = f.parse_blob_catalog(
        {
            "products": [
                {"ma": "S06", "priceUsd": "2,5"},
                {"ma": "S006", "priceUsd": "$25"},
            ]
        }
    )
    assert [(row.ma, row.price_usd) for row in both] == [
        ("S06", None),
        (norm_ma("S006"), Decimal("25")),
    ]
    assert both[1].ma == "S06"
