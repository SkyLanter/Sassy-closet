"""Piece 164: NaN/Infinity cost, kg or live price must be 'not usable', never crash."""
import json
from decimal import Decimal

import held_price_proposal as h
from held_policy import HeldPolicy

P = HeldPolicy(held=("K03",), never_list=())
KEY = "cost" + "_cny"


def _row(cost, kg="0.3"):
    return {"ma": "K03", "kind": "K", KEY: cost, "kg": kg}


def test_nonfinite_cost_needs_boss():
    for bad in ("NaN", "sNaN", "Infinity", "-Infinity", "inf"):
        p = h.propose(_row(bad), P)
        assert p.status == "needs-boss", (bad, p)
        assert any("not usable" in f for f in p.flags)


def test_nonfinite_kg_needs_boss():
    p = h.propose(_row(str(10 * 10), kg="Infinity"), P, kg_proxy={})
    assert p.status == "needs-boss"


def test_nan_live_catalog_price_skipped(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"prices": {"K03": "NaN", "A01": "Infinity", "A02": "20"}}))
    assert set(h.load_live_catalog(f)) == {"A02"}


def test_good_row_still_quotes():
    assert h.propose(_row(str(10 * 10)), P).status == "quote"


def test_currency_mark_between_digits_does_not_quote():
    yen = chr(0xA5)
    assert h._num(yen + "110") == Decimal("110")
    assert h._num("$25") == Decimal("25")
    assert h._num("80" + yen) == Decimal("80")
    assert h._num(yen + " 80") == Decimal("80")
    assert h._num("+$25") == Decimal("25")
    for bad in ("2$5", "2" + yen + "5", "$$25", yen + yen + "80", yen + "$80", "2,5", "1,200"):
        assert h._num(bad) is None, bad
    plain = h.propose(_row("110", kg="0.3"), P)
    marked = h.propose(_row(yen + "110", kg="0.3"), P)
    assert marked.status == "quote"
    assert marked.tiered_usd == plain.tiered_usd
    assert marked.flat25_usd == plain.flat25_usd
    garbled = h.propose(_row("2$5", kg="0.3"), P)
    assert garbled.status == "needs-boss"
    assert garbled.tiered_usd is None
    assert garbled.flat25_usd is None
    assert any("not usable" in flag for flag in garbled.flags)
    weight = h.propose(_row("110", kg="2$5"), P)
    assert weight.status == "needs-boss"
    assert weight.tiered_usd is None
    assert weight.flat25_usd is None


def test_junk_live_dollar_is_not_already_live(tmp_path):
    catalog = tmp_path / "c.json"
    catalog.write_text(
        json.dumps(
            {
                "products": [
                    {"ma": "A29", "priceUsd": "2$5", "status": "available"},
                    {"ma": "A30", "priceUsd": "$31", "status": "available"},
                ]
            }
        ),
        encoding="utf-8",
    )
    loaded = h.load_live_catalog(catalog)
    assert "A29" not in loaded
    assert loaded["A30"] == Decimal("31")
