"""s06_offer_price reads S06's own Product offer and ignores neighbour cards."""

import json

from s06_offer_price import _offer_amount, s06_offer_dollars


def _ld(obj) -> str:
    return f'<script type="application/ld+json">{json.dumps(obj)}</script>'


def _product(sku: str, price, url: str | None = None) -> dict:
    node = {"@type": "Product", "sku": sku, "offers": {"@type": "Offer", "price": price}}
    if url:
        node["url"] = url
    return node


def test_reads_s06_offer() -> None:
    assert s06_offer_dollars(_ld(_product("S06", "25.00")) + "<p>$26</p>") == 25


def test_ignores_neighbour_products_and_text() -> None:
    html = _ld([_product("A01", "25"), _product("S06", "26")]) + "<p>$25 $25</p>"
    assert s06_offer_dollars(html) == 26


def test_graph_and_spelling_and_url() -> None:
    assert s06_offer_dollars(_ld({"@graph": [_product("s6", 25)]})) == 25
    assert s06_offer_dollars(_ld(_product("", "25", url="https://x/m/S06"))) == 25
    assert s06_offer_dollars(_ld(_product("", "25", url="https://x/m/S16"))) is None


def test_missing_bad_or_disagreeing_is_none() -> None:
    assert s06_offer_dollars("<p>$25</p>") is None
    assert s06_offer_dollars('<script type="application/ld+json">{bad</script>') is None
    assert s06_offer_dollars(_ld(_product("S06", "25.50"))) is None
    assert s06_offer_dollars(_ld(_product("S06", "abc"))) is None
    assert s06_offer_dollars(_ld({"@type": "Product", "sku": "S06", "offers": [{"price": "25"}, {"price": "26"}]})) is None


def test_plain_offer_marks_still_read_25() -> None:
    for price in ("25", "25.00", "25.0", "25.", "025", "$25", "25$", "$25.00", "$ 25", "25 $", "+25", "+$25", "$+25"):
        assert s06_offer_dollars(_ld(_product("S06", price))) == 25, price
    assert s06_offer_dollars(_ld(_product("S06", 25))) == 25
    assert s06_offer_dollars(_ld(_product("S06", 25.0))) == 25


def test_spliced_exponent_and_underscore_are_not_25() -> None:
    for price in ("2$5", "$$25", "$2$5", "2.5e1", "25e0", "2.50E+1", "250e-1", "2_5", "0,025", "２５"):
        assert s06_offer_dollars(_ld(_product("S06", price))) is None, price


def test_bool_nan_blank_and_split_digits_are_not_25() -> None:
    for price in (True, False, "", "$", "2 5"):
        assert s06_offer_dollars(_ld(_product("S06", price))) is None, price
    assert not _offer_amount(True).is_finite()
    assert not _offer_amount(False).is_finite()
    assert not _offer_amount(float("nan")).is_finite()
    nan_page = _ld(_product("S06", float("nan")))
    assert s06_offer_dollars(nan_page) is None


def test_neighbour_25_does_not_repair_a_spliced_or_split_offer() -> None:
    for price in ("2$5", "", "$", "2 5", True):
        html = _ld([_product("A01", "$25"), _product("S06", price)]) + "<p>$25</p>"
        assert s06_offer_dollars(html) is None, price
    disagree = _ld(
        [
            _product("A01", "25"),
            {"@type": "Product", "sku": "S06", "offers": [{"price": "25"}, {"price": "26"}]},
        ]
    )
    assert s06_offer_dollars(disagree + "<p>$25</p>") is None
