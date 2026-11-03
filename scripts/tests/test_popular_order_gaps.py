"""Placeholder tests for piece 74 (fixture codes only; no real data)."""
import json
from pathlib import Path
import popular_order_gaps as g

ROOT = Path(__file__).resolve().parents[2]


def test_missing_skips_held_and_present():
    assert g.missing(["X01", "X02", "Y01", "Z01"], ["X01"], {"Z01"}) == ["X02", "Y01"]


def test_unranked_goes_to_end_of_type_group_stable():
    types = {"X01": "X", "Y01": "Y", "X02": "X", "X03": "X", "W01": "W"}
    out, notes = g.place(["X01", "Y01"], ["X03", "X02", "W01"], types)
    assert out == ["X01", "X03", "X02", "Y01", "W01"]
    assert notes[2][2].startswith("no type W")


def test_ranked_placed_by_blended_rank_without_reordering():
    out, _ = g.place(["X01", "Y01", "X02"], ["Y02"], {}, ["Y01", "Y02", "X02"])
    assert out == ["X01", "Y01", "Y02", "X02"]


def test_main_check_fails_then_passes(tmp_path, capsys):
    cat = tmp_path / "c.json"
    cat.write_text(json.dumps({"products": [{"ma": "X01", "status": "available", "type": "X"},
                                            {"ma": "X02", "status": "available", "type": "X"},
                                            {"ma": "X09", "status": "sold"}]}))
    o = tmp_path / "o.json"; o.write_text(json.dumps({"order": ["X01"]}))
    assert g.main(["--order", str(o), "--catalog", str(cat), "--plan"]) == 1
    assert "MISSING X02" in capsys.readouterr().out
    o.write_text(json.dumps({"order": ["X01", "X02"]}))
    assert g.main(["--order", str(o), "--catalog", str(cat)]) == 0


def test_repo_order_has_no_duplicates():
    order = json.loads((ROOT / "sassy-closet-shop/data/popular-order.json").read_text())["order"]
    assert len(order) == len(set(order))


def test_held_in_order_placeholder():
    from popular_order_gaps import held_in_order
    assert held_in_order(["X01", "X02", "X03"], {"X03", "X01", "X09"}) == ["X01", "X03"]
    assert held_in_order(["X01"], set()) == []
