"""Placeholder tests for piece 72 (fixture codes only; no real data)."""
import json
import popular_carryover as pc


def test_ranked_live_first_then_carried():
    order, rl, car, drop = pc.build(["X02", "Y01", "X01"], ["X01", "X02", "Z01", "Z02"], set(), ["Z02", "X01", "Z01"])
    assert order == ["X02", "X01", "Z02", "Z01"] and rl == ["X02", "X01"] and car == ["Z02", "Z01"]
    assert drop == ["Y01"]


def test_held_left_out_even_if_ranked_and_live():
    order, *_ = pc.build(["X01", "X02"], ["X01", "X02"], {"X01"}, ["X01"])
    assert order == ["X02"]


def test_unlisted_previous_not_added():
    order, *_ = pc.build([], ["X01"], set(), ["Q09", "X01"])
    assert order == ["X01"]


def test_captionless_reel_rows_skipped():
    assert pc._codes([None, "", "reel", "x01", "X01"]) == ["X01"]


def test_live_leftovers_appended():
    order, *_ = pc.build([], ["X01", "X02"], set(), ["X02"])
    assert order == ["X02", "X01"]


def test_summary_and_home_parsers():
    assert pc.summary_live("a\nLive on sell site among ranked: X01 X02 only (rest)\n") == ["X01", "X02"]
    assert pc.home_order('<a href="/m/X02">x</a><a href="/m/X01"></a><a href="/m/X02">') == ["X02", "X01"]


def test_main_writes_markdown(tmp_path):
    c = tmp_path / "cyc"; c.mkdir()
    (c / "blended.json").write_text(json.dumps({"order": ["X02", "Y01"]}))
    (c / "SUMMARY.txt").write_text("Live on sell site among ranked: X02 Y02 only\n")
    cat = tmp_path / "cat.json"; cat.write_text(json.dumps({"products": [{"ma": "X02", "status": "available"}, {"ma": "X01", "status": "available"}]}))
    h = tmp_path / "held.json"; h.write_text(json.dumps({"heldIncomplete": ["Y01"], "neverList": []}))
    p = tmp_path / "prev.json"; p.write_text(json.dumps({"order": ["X01"]}))
    out = tmp_path / "P.md"
    assert pc.main(["--cycle", str(c), "--held", str(h), "--prev-order", str(p), "--catalog", str(cat), "--out", str(out)]) == 0
    t = out.read_text()
    assert "1. X02 — window rank" in t and "2. X01 — carried" in t and "Y01" not in t.split("## Order")[1]


def test_catalog_live_only_available():
    d = {"products": [{"ma": "X01", "status": "available"}, {"ma": "X02", "status": "sold"}, {"ma": None}, "junk"]}
    assert pc.catalog_live(d) == ["X01"]


def test_summary_never_makes_live(tmp_path):
    c = tmp_path / "cyc"; c.mkdir()
    (c / "blended.json").write_text(json.dumps({"order": ["Y02", "X01"]}))
    (c / "SUMMARY.txt").write_text("Live on sell site among ranked: Y02 X01 only\n")
    h = tmp_path / "held.json"; h.write_text(json.dumps({"heldIncomplete": [], "neverList": []}))
    cat = tmp_path / "cat.json"; cat.write_text(json.dumps({"products": [{"ma": "X01", "status": "available"}]}))
    out = tmp_path / "P.md"
    assert pc.main(["--cycle", str(c), "--held", str(h), "--catalog", str(cat), "--out", str(out)]) == 0
    order = out.read_text().split("## Order")[1]
    assert "1. X01" in order and "Y02 —" not in order
    assert "not live in catalog: Y02" in out.read_text()


def test_live_source_required(tmp_path):
    import pytest
    c = tmp_path / "cyc"; c.mkdir()
    (c / "blended.json").write_text(json.dumps({"order": []}))
    with pytest.raises(SystemExit):
        pc.main(["--cycle", str(c)])
