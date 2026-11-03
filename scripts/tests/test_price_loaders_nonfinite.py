"""Piece 172: price loaders drop NaN/Infinity instead of loading a price no check can catch."""
import json

import caption_gap_watch
import caption_gia_check
import caption_lint
import cost_basis_reconcile
import meta_inventory

BAD = ["NaN", "Infinity", "-Infinity"]


def _write(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj))
    return p


def test_caption_lint_load_live_prices(tmp_path):
    prices = {"A01": "20", **{f"B0{i}": b for i, b in enumerate(BAD)}}
    assert caption_lint.load_live(_write(tmp_path, "c.json", {"prices": prices})) == {"A01": 20.0}


def test_caption_lint_load_live_products(tmp_path):
    prods = [{"ma": "A01", "priceUsd": 20}] + [{"ma": f"B0{i}", "priceUsd": b} for i, b in enumerate(BAD)]
    assert caption_lint.load_live(_write(tmp_path, "c.json", {"products": prods})) == {"A01": 20.0}


def test_caption_lint_load_snapshot(tmp_path):
    items = [{"ma": "A01", "live": True, "sellUsd": 20}, {"ma": "B01", "live": True, "sellUsd": "NaN"}]
    live, known = caption_lint.load_snapshot(_write(tmp_path, "s.json", {"items": items}))
    assert live == {"A01": 20.0}


def test_approved_gia_loaders(tmp_path):
    p = _write(tmp_path, "a.json", {"approvedGia": {"A01": 20, "B01": "NaN", "B02": "Infinity"}})
    assert caption_gia_check.load_approved(p) == {"A01": 20.0}
    assert meta_inventory.load_approved(p) == {"A01": 20.0}


def test_caption_gap_watch_json_nan(tmp_path):
    p = tmp_path / "g.json"
    p.write_text('{"approvedGia": {"A01": 20, "B01": NaN, "B02": Infinity}}')
    out = caption_gap_watch.load_prices(p)
    assert "B01" not in out and "B02" not in out and out["A01"] == 20.0


def test_cost_basis_load_live(tmp_path):
    prods = [{"ma": "A01", "priceUsd": 20}, {"ma": "B01", "priceUsd": "NaN"}]
    assert cost_basis_reconcile.load_live(_write(tmp_path, "c.json", {"products": prods})) == {"A01": 20.0}
