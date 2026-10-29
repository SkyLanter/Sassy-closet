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
