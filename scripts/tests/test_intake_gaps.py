import copy
import json
from decimal import Decimal

import intake_gaps as ig

BASE = {"ma": "A01", "kind": "A", "size": "S M L", "link": "https://e.tb.cn/h.x", "cost_cny": "67.23",
        "cost_usd": "10", "cost_currency": "USD", "sell_usd": "25", "photo_paths": ["A01/001.jpg"]}
CAT = {"kinds": [{"code": c, "sizes": ["S", "M", "L", "XL"]} for c in "AQVDKSBPHJO"] +
       [{"code": "G", "sizes": ["35", "36", "37"]}]}


def run(row, live=None, held=(), weights=None):
    return ig.build({"submissions": [row], "catalog": CAT}, live or {}, set(held), weights)["rows"][0]


def types(x, key="gaps"):
    return [g["type"] for g in x[key]]


def r(**kw):
    d = copy.deepcopy(BASE)
    d.update(kw)
    return d


def test_clean_row_only_has_proxy_kg():
    x = run(BASE)
    assert types(x) == ["kg"] and "A category proxy 0.3" in x["gaps"][0]["detail"]
    assert x["suspect"] == []


def test_measured_weight_clears_kg():
    assert types(run(BASE, weights={"A01": (Decimal("0.2"), "real")})) == []


def test_blank_and_garbled_cny():
    assert "cny" in types(run(r(cost_cny="")))
    x = run(r(cost_cny="127;145"))
    assert "garbled" in x["gaps"][0]["detail"] and "127;145" in x["gaps"][0]["detail"]


def test_kg_missing_without_proxy_and_g_needs_boss():
    x = run(r(ma="S14", kind="S"))
    assert x["gaps"][0]["detail"] == "no kg and no category proxy"
    g = run(r(ma="G01", kind="G", size="35 36"))
    assert "G needs Boss" in g["gaps"][0]["detail"]
    e = run(r(ma="S01", kind="S"), weights={"S01": (Decimal("0.5"), "est")})
    assert "estimate 0.5" in e["gaps"][0]["detail"]


def test_trailing_zero_counts_as_the_allowed_chip_and_the_row_stays():
    row = r(ma="G01", kind="G", size="35.0 36")
    before = copy.deepcopy(row)
    assert "size" not in types(run(row))
    assert row == before
    flagged = run(r(ma="G01", kind="G", size="35.0 44.0"))
    size_gaps = [gap for gap in flagged["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in size_gaps] == ["size not allowed for G: 44.0"]
    hundredths = run(r(ma="G01", kind="G", size="35.00"))
    hundredth_gaps = [gap for gap in hundredths["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in hundredth_gaps] == ["size not allowed for G: 35.00"]
    outside = run(r(ma="G01", kind="G", size="34.0 42.0"))
    outside_gaps = [gap for gap in outside["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in outside_gaps] == ["size not allowed for G: 34.0 42.0"]
    clothing = run(r(size="40.0"))
    clothing_gaps = [gap for gap in clothing["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in clothing_gaps] == ["size not allowed for A: 40.0"]


def test_delimiter_split_matches_listing_and_the_row_stays():
    row = r(ma="G01", kind="G", size="35;36|37")
    before = copy.deepcopy(row)
    assert "size" not in types(run(row))
    assert row == before
    mixed = run(r(ma="G01", kind="G", size="35;44"))
    mixed_gaps = [gap for gap in mixed["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in mixed_gaps] == ["size not allowed for G: 44"]
    blank = run(r(ma="G01", kind="G", size=";;;"))
    blank_gaps = [gap for gap in blank["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in blank_gaps] == ["no size"]
    assert "size" not in types(run(r(size="S;M")))
    odd = run(r(size="S;99"))
    odd_gaps = [gap for gap in odd["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in odd_gaps] == ["size not allowed for A: 99"]


def test_listing_alias_counts_as_the_allowed_chip_and_the_row_stays():
    allowed = ("2XS", "XS", "S", "M", "L", "XL", "2XL")
    assert ig.disallowed_size_tokens("XXS 3XL;XXL", allowed) == []
    assert ig.disallowed_size_tokens("4XL", allowed) == ["4XL"]
    assert ig.disallowed_size_tokens("XXS", ("S", "M", "L", "XL")) == ["XXS"]
    row = r(size="S XXS")
    before = copy.deepcopy(row)
    flagged = run(row)
    size_gaps = [gap for gap in flagged["gaps"] if gap["type"] == "size"]
    assert [gap["detail"] for gap in size_gaps] == ["size not allowed for A: XXS"]
    assert row == before
    kept = r(size="XXS;XXL|3XL")
    kept_before = copy.deepcopy(kept)
    gaps, _suspect = ig.row_gaps(kept, {}, {}, {"A": allowed})
    assert [gap for gap in gaps if gap["type"] == "size"] == []
    assert kept == kept_before


def test_size_missing_bad_and_not_needed():
    assert "size" in types(run(r(size="")))
    assert "size" in types(run(r(ma="G01", kind="G", size="35 44")))
    assert "size" not in types(run(r(ma="P01", kind="P", size="")))


def test_photos_and_live_images():
    x = run(r(photo_paths=[]), live={"A01": {"price": Decimal(25), "images": []}})
    assert x["gaps"][-1]["detail"] == "no intake photos; no catalog images"


def test_link_missing_and_non_taobao():
    assert "link" in types(run(r(link="")))
    assert "link" in types(run(r(link="https://example.com/x")))
    assert "link" not in types(run(r(link="https://item.taobao.com/item.htm?id=1")))


def test_category_blank_unknown_mismatch():
    assert "category" in types(run(r(kind="")))
    assert "category" in types(run(r(kind="Z")))
    assert "category" in types(run(r(kind="S")))


def test_junk_dollar_text_is_not_a_price(tmp_path):
    assert ig._num("$25") == Decimal("25")
    assert ig._num("25$") == Decimal("25")
    assert ig._num("$ 25") == Decimal("25")
    assert ig._num("25.00") == Decimal("25.00")
    assert ig._num(25) == Decimal("25")
    assert ig._num("-$25") == Decimal("-25")
    assert ig._num("+$25") == Decimal("25")
    assert ig._num("$-25") == Decimal("-25")
    for bad in (
        "2$5", "$$25", "$25$", "12$50", "2,$5", "1,200", "$1,200", "1,200$", "12,50", "-$ 25",
        "2.5e1", "25e0", "250e-1", "+$2.5e1", "2.5e1$", "$2.5e1", "2.5E1",
        "1e2", "$1e2", "1e2$", "2_5", "2__5", "25_0",
    ):
        assert ig._num(bad) is None, bad
    weighed = run(r(weight_kg="2$5"))
    assert "kg" in types(weighed)
    junk_sell = run(r(sell_usd="2$5"), live={"A01": {"price": Decimal("30"), "images": ["a"]}})
    assert "sell_vs_live" not in types(junk_sell, "suspect")
    exponent_sell = run(r(sell_usd="2.5e1"), live={"A01": {"price": Decimal("25"), "images": ["a"]}})
    assert "sell_vs_live" not in types(exponent_sell, "suspect")
    real_sell = run(r(sell_usd="$25"), live={"A01": {"price": Decimal("30"), "images": ["a"]}})
    assert "sell_vs_live" in types(real_sell, "suspect")
    junk_cost = run(r(cost_usd="2$5"))
    assert "no_usd_cost" in types(junk_cost, "suspect")
    assert "usd_vs_cny" not in types(junk_cost, "suspect")
    catalog = tmp_path / "live.json"
    catalog.write_text(
        json.dumps(
            {
                "products": [
                    {"ma": "S06", "priceUsd": "2$5", "images": ["s.jpg"]},
                    {"ma": "A07", "priceUsd": "$25", "images": []},
                ]
            }
        ),
        encoding="utf-8",
    )
    live = ig.load_live(catalog)
    assert live["S06"]["price"] is None
    assert live["A07"]["price"] == Decimal("25")
    exponent = tmp_path / "exponent.json"
    exponent.write_text(
        json.dumps(
            {
                "products": [
                    {"ma": "S006", "priceUsd": "2.5e1", "images": ["s.jpg"]},
                    {"ma": "S6", "priceUsd": "1e2", "images": ["t.jpg"]},
                ]
            }
        ),
        encoding="utf-8",
    )
    folded = ig.load_live(exponent)
    assert folded["S06"]["price"] is None


def test_suspect_costs_reported_not_fixed():
    row = r(ma="P03", kind="P", size="", sell_usd="18", cost_currency="CNY", cost_usd="")
    before = copy.deepcopy(row)
    x = run(row, live={"P03": {"price": Decimal(11), "images": ["a"]}})
    assert types(x, "suspect") == ["sell_vs_live", "no_usd_cost"]
    assert x["suspect"][0]["detail"] == "intake $18 vs live $11"
    assert row == before
    assert types(run(r(cost_currency="CNY")), "suspect") == ["cny_label"]
    assert types(run(r(cost_usd="20")), "suspect") == ["usd_vs_cny"]


def test_grouping_held_beats_live():
    rep = ig.build({"submissions": [BASE, r(ma="A02"), r(ma="A03")], "catalog": CAT},
                   {"A01": {"price": Decimal(25), "images": ["x"]}, "A03": {"price": Decimal(25), "images": ["x"]}},
                   {"A03"})
    assert [x["group"] for x in rep["rows"]] == ["live", "not live", "held"]


def test_cli_writes_only_named_outputs(tmp_path):
    intake = tmp_path / "i.json"
    intake.write_text(json.dumps({"submissions": [BASE], "catalog": CAT}))
    held = tmp_path / "h.json"
    held.write_text(json.dumps({"heldIncomplete": ["S14"], "neverList": []}))
    before = intake.read_bytes()
    assert ig.main(["--intake", str(intake), "--held", str(held), "--out-md", str(tmp_path / "o.md"),
                    "--out-json", str(tmp_path / "o.json")]) == 0
    assert intake.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["h.json", "i.json", "o.json", "o.md"]


def test_no_network_imports():
    src = open(ig.__file__, encoding="utf-8").read()
    for bad in ("urllib", "requests", "http.client", "socket"):
        assert f"import {bad}" not in src


# --- piece 249: bare-list intake regression (was AttributeError) ---
def _p249_row():
    return {"ma": "s006", "kind": "S", "cost_cny": "50", "cost_usd": "7.44", "size": "M",
            "photo_paths": ["a"], "link": "https://item.taobao.com/x"}


def test_p249_bare_list_intake_matches_object_shape():
    import intake_gaps as g
    a = g.build([_p249_row()], {}, set())
    b = g.build({"submissions": [_p249_row()]}, {}, set())
    assert a == b and a["intake_mas"] == 1 and a["rows"][0]["ma"] == "S06"


def test_p249_items_key_and_junk_shapes_never_crash():
    import intake_gaps as g
    assert g.build({"items": [_p249_row()]}, {}, set())["intake_mas"] == 1
    for junk in (None, "x", 3, {}, {"submissions": None}, [None, "x", 3]):
        assert g.build(junk, {}, set())["intake_mas"] == 0


def test_p249_main_cli_accepts_bare_list(tmp_path):
    import json
    import intake_gaps as g
    p = tmp_path / "intake.json"
    p.write_text(json.dumps([_p249_row()]), encoding="utf-8")
    out = tmp_path / "o.json"
    assert g.main(["--intake", str(p), "--out-json", str(out)]) == 0
    assert json.loads(out.read_text())["intake_mas"] == 1


def test_sold_and_hold_are_not_the_live_shop_price(tmp_path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"products": [
        {"ma": " a01 ", "status": "available", "priceUsd": 20, "images": ["a"]},
        {"ma": "Z03", "status": "sold", "priceUsd": 19},
        {"ma": "S14", "status": "hold", "priceUsd": 30},
        {"ma": "H02", "priceUsd": 12},
        {"ma": "K02", "status": None, "priceUsd": 15},
        {"ma": "A02", "status": "  ", "priceUsd": 22},
        {"ma": "A03", "status": "\n", "priceUsd": 23},
        "not-a-row",
        {"priceUsd": 5},
    ]}))
    live = ig.load_live(catalog)
    assert set(live) == {"A01", "A02", "A03", "H02", "K02"}
    assert live["A01"]["price"] == Decimal(20)
    assert live["A01"]["images"] == ["a"]
    intake = {
        "submissions": [
            {"ma": "Z03", "kind": "Z", "sell_usd": "40", "cost_usd": "10", "cost_cny": "67.23"},
            {"ma": "A01", "kind": "A", "sell_usd": "18", "cost_usd": "10", "cost_cny": "67.23", "size": "M"},
        ]
    }
    rows = {row["ma"]: row for row in ig.build(intake, live, set())["rows"]}
    assert rows["Z03"]["group"] == "not live"
    assert "sell_vs_live" not in [item["type"] for item in rows["Z03"]["suspect"]]
    assert rows["A01"]["group"] == "live"
    assert "sell_vs_live" in [item["type"] for item in rows["A01"]["suspect"]]


def test_prices_map_and_bare_catalog_list(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({"prices": {" k3 ": 40}}))
    assert ig.load_live(prices)["K03"]["price"] == Decimal(40)
    bare = tmp_path / "bare.json"
    bare.write_text(json.dumps([
        {"ma": "A01", "status": "Available", "priceUsd": 20},
        {"ma": "Z03", "status": "SOLD", "priceUsd": 19},
    ]))
    assert set(ig.load_live(bare)) == {"A01"}
