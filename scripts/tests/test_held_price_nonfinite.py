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
    assert h._num("1,200") == Decimal("1200")
    assert h._num("$1,200") == Decimal("1200")
    assert h._num("1,200" + yen) == Decimal("1200")
    assert h._num(yen + "1,200.00") == Decimal("1200.00")
    for bad in (
        "2$5",
        "2" + yen + "5",
        "$$25",
        yen + yen + "80",
        yen + "$80",
        "2,5",
        "12,50",
        "1,2000",
        "0,025",
        "2.5e1",
        "25e0",
        "2_5",
        "25_0",
        "1,200e0",
    ):
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
    grouped = h.propose(_row("1,200", kg="0.3"), P)
    same = h.propose(_row("1200", kg="0.3"), P)
    assert grouped.status == "quote"
    assert grouped.tiered_usd == same.tiered_usd
    assert grouped.flat25_usd == same.flat25_usd
    exponent = h.propose(_row("2.5e1", kg="0.3"), P)
    assert exponent.status == "needs-boss"
    assert exponent.tiered_usd is None


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
    junk = tmp_path / "junk-s06.json"
    junk.write_text(
        json.dumps({"products": [{"ma": "S006", "priceUsd": "2.5e1", "status": "available"}]}),
        encoding="utf-8",
    )
    assert "S06" not in h.load_live_catalog(junk)
    padded = tmp_path / "padded-s06.json"
    padded.write_text(
        json.dumps({"products": [{"ma": "S6", "priceUsd": "0,025", "status": "available"}]}),
        encoding="utf-8",
    )
    assert "S06" not in h.load_live_catalog(padded)
    locked = tmp_path / "locked-s06.json"
    locked.write_text(
        json.dumps(
            {
                "products": [
                    {"ma": "S06", "priceUsd": "$25", "status": "available"},
                    {"ma": "A31", "priceUsd": "1,200", "status": "available"},
                    {"ma": "A32", "priceUsd": "12,50", "status": "available"},
                ]
            }
        ),
        encoding="utf-8",
    )
    live = h.load_live_catalog(locked)
    assert live["S06"] == Decimal("25")
    assert live["A31"] == Decimal("1200")
    assert "A32" not in live
