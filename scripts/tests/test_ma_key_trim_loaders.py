"""Piece 184: price-map loaders trim mã keys, so ' A01 ' and 'a01' match 'A01'."""
import json

import caption_gia_check
import caption_lint
import held_price_proposal
import meta_inventory
import too_cheap_check


def _w(tmp_path, obj, name="x.json"):
    p = tmp_path / name
    p.write_text(json.dumps(obj))
    return p


def test_too_cheap_load_live(tmp_path):
    assert too_cheap_check.load_live(_w(tmp_path, {"products": [{"ma": " a01 ", "priceUsd": 20}]})) == {"A01": 20.0}
    assert too_cheap_check.load_live(_w(tmp_path, {"prices": {"A01 ": 20}})) == {"A01": 20.0}


def test_caption_lint_load_live(tmp_path):
    assert caption_lint.load_live(_w(tmp_path, {"products": [{"ma": " A01", "priceUsd": 20}]})) == {"A01": 20.0}
    assert caption_lint.load_live(_w(tmp_path, {"prices": {" a01": 20}})) == {"A01": 20.0}


def test_approved_gia(tmp_path):
    p = _w(tmp_path, {"approvedGia": {" A01 ": 20}})
    assert caption_gia_check.load_approved(p) == {"A01": 20.0}
    assert meta_inventory.load_approved(p) == {"A01": 20.0}


def test_held_price_load_live(tmp_path):
    assert held_price_proposal.load_live(_w(tmp_path, {"prices": {" k03 ": 52}})) == {"K03": 52}
